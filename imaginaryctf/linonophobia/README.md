<h1>Writeup imaginaryctf 2021</h1>
<h1>Author: dV</h1>
<h2>Challenge Name: linonophobia</h2>
<h3>Phân tích file</h3>
   <h4>Các cơ chế 
  
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
  Ta thấy có canary.
<h3>Reversing file</h3>
  <h4>
    
    main
    {
      int i; // [rsp+Ch] [rbp-124h]
      char buf[264]; // [rsp+20h] [rbp-110h] BYREF
      unsigned __int64 v6; // [rsp+128h] [rbp-8h]
      v6 = __readfsqword(0x28u);
      setvbuf(_bss_start, 0LL, 2, 0LL);
      setvbuf(stdin, 0LL, 2, 0LL);
      puts("wElCoMe tO mY sErVeR!");
      for ( i = 0; i <= 7; ++i )
        *((_BYTE *)&off_601020 + i) = ((__int64)&puts >> (8 * (unsigned __int8)i)) % 256;
      read(0, buf, 0x200uLL);
      printf(buf);
      read(0, buf, 0x200uLL);
      return 0;
    }
Ta thấy có bug bof ở hàm read khi input nhận vào tối đa là 0x200(512 bytes) nhưng biến buf chỉ được khai báo có 264 bytes. Bug thứ 2 nằm ở hàm printf(buf) khi hàm được gọi nhưng không có format nên sẽ có bug fmt.
    
Vậy ý tưởng của ta ở đây sẽ là:
    
Dùng bug fmt để leak canary nhầm bypass hàm kiểm tra canary, sau đó dùng bof để control ret, ở đây mình dùng ret2libc nhé.
