- Main:
    
    ```python
    __int64 __fastcall main(int a1, char **a2, char **a3)
    {
      unsigned int v3; // eax
      char s[128]; // [rsp+10h] [rbp-E0h] BYREF
      __int64 v6[8]; // [rsp+90h] [rbp-60h] BYREF
      FILE *v7; // [rsp+D0h] [rbp-20h]
      FILE *stream; // [rsp+D8h] [rbp-18h]
      char *s2; // [rsp+E0h] [rbp-10h]
      unsigned int i; // [rsp+ECh] [rbp-4h]
    
      __sysv_signal(14, handler);
      alarm(0x14u);
      setvbuf(stdin, 0LL, 2, 0LL);
      setvbuf(stdout, 0LL, 2, 0LL);
      setvbuf(stderr, 0LL, 2, 0LL);
      s2 = (char *)malloc(0x22uLL);
      stream = fopen("/dev/urandom", "rb");
      fread(s2 + 30, 1uLL, 4uLL, stream);
      fclose(stream);
      printf("Guess a number: ");
      gets(s2);
      v6[0] = 0LL;
      v6[1] = 0LL;
      v6[2] = 0LL;
      v6[3] = 0LL;
      v6[4] = 0LL;
      v6[5] = 0LL;
      v6[6] = 0LL;
      v6[7] = 0LL;
      v6[0] = *(unsigned int *)(s2 + 30);
      for ( i = 1; i <= 0xF; ++i )
        *((_DWORD *)v6 + i) = 1103515245 * *((_DWORD *)v6 + i - 1) + 12345;
      sub_4011F6(v6);
      v3 = sub_401241(v6);
      sprintf(s, "%08x", v3);
      if ( !strcmp(s, s2) )
      {
        v7 = fopen("flag", "rt");
        if ( v7 )
        {
          memset(s, 0, sizeof(s));
          fread(s, 1uLL, 0x80uLL, v7);
          printf("Flag: %s\n", s);
          fclose(v7);
        }
      }
      else
      {
        puts("Try again");
      }
      return 0LL;
    }
    ```
    
    - Ta có thể thấy chương trình sẽ đọc random 4 bytes từ /dev/urandom đưa vào s2+30 và sau đó cho ta nhập input vào s2 qua gets(s2) ⇒ ta có thể overflow và kiểm soát được 4 bytes random.
    - Sau đó chương trình sẽ lấy 4 bytes random đó đưa vào vòng for và thực hiện thuật toán, nếu ta control random thành 0x0 thì kết quả sẽ luôn là "9a9c88bb" và ta có thể đoán được.
