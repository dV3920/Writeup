<h1>Writeup imaginaryctf 2021</h1>
<h1>Author: dV</h1>
<h2>Challenge Name: String Editor 2</h2>
<h3>Phân tích file</h3>
   <h4>Các cơ chế 
  
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
    Ta thấy rằng không PIE và Partial RELRO, khác bài trước là Full RELRO, ở bài này ta có thể ghi đè GOT.
<h3>Reversing file</h3>
  <h4> 
    
    Main
    char v3; // [rsp+Fh] [rbp-11h] BYREF
    __int64 v4[2]; // [rsp+10h] [rbp-10h] BYREF

    v4[1] = __readfsqword(0x28u);
    setvbuf(_bss_start, 0LL, 2, 0LL);
    setvbuf(stdin, 0LL, 2, 0LL);
    strcpy(target, "***************");
    puts(s);
    puts("Today, you will have the AMAZING opportunity to edit a string!");
    sleep(1u);
    printf("But first, a word from our sponsors: 0x%x%x%x%x%x%x\n\n", 127LL, 255LL, 255LL, 108LL, 111LL, 108LL);
    while ( 1 )
    {
      puts("Here ya go! Your string is:");
      puts(target);
      puts("What character would you like to edit? (enter in 15 to see utils)");
      __isoc99_scanf("%ld%*c", v4);
      if ( v4[0] > 15 )
        break;
      if ( v4[0] == 15 )
      {
        puts("1. Admire your string");
        puts("2. Delete your string");
        puts("3. Exit");
        __isoc99_scanf("%ld%*c", v4);
        switch ( v4[0] )
        {
          case 1LL:
            admire();
            break;
          case 2LL:
            del();
            break;
          case 3LL:
            exit(0);
        }
      }
      else
      {
        puts("What character should be in that index?");
        __isoc99_scanf("%c%*c", &v3);
        target[v4[0]] = v3;
        puts("Done.");
      }
    }
    puts("Go away hacker.");
    exit(-1);
<h3>Như bài trước chương trình cho ta nhập index và thay đổi từ ở vị trí đó, nhưng bài này sẽ check index có lớn hơn 15 hay không. Nếu có thì break, nếu bằng thì có 3 lựa chọn nhưng không kiểm tra index có bé hơn 0 hay không.</h3>
   <h4> 
    int admire()
    {
      puts("AMAZING STRING!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! :rooPOG: :rooYay:");
      return puts(target);
    }
    char *del()
    {
      return strcpy(target, "***************");
    }
    void __noreturn exit(int status)
    {
      exit(status);
    }
    
    
