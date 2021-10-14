- Main:
    
    ```python
    __int64 __fastcall main(int a1, char **a2, char **a3)
    {
      char s[128]; // [rsp+0h] [rbp-80h] BYREF
    
      signal(14, handler);
      alarm(0x14u);
      setvbuf(stdin, 0LL, 2, 0LL);
      setvbuf(stdout, 0LL, 2, 0LL);
      setvbuf(stderr, 0LL, 2, 0LL);
      do
      {
        gets(s);
        puts(s);
      }
      while ( !strstr(s, "QUIT") );
      return 0LL;
    }
    ```
    
    - Ta có thể thấy bug bof ở hàm gets(s) ta có thể ROP, ta chỉ cần nhập QUIT+payload để nó thoát ra vòng lặp và control ret.
