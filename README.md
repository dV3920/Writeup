<h1>Writeup imaginaryctf 2021</h1>
<h1>Author: dV</h1>
<h2>Challenge Name: Memory pile</h2>
<h3>Phân tích file</h3>
   <h4>Các cơ chế 
  
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
    RUNPATH:  './'

Tất cả các cơ chế đều bật
  <h3>Reversing file</h3>
  Chương trình có 3 chức năng chính
    <h4> 
      
    *acquire()   
    {
    int v0; // ebx
    void *v1; // rcx
    _QWORD *result; // rax

    v0 = read();
    v1 = malloc(0x20uLL);
    result = mem;
    mem[v0] = v1;
    return result;
    }
    malloc cho ta 1 size cố định là 0x20.
      
    fill()
    {
      int v1; // [rsp+Ch] [rbp-4h]
      v1 = read();
      printf("Let me have it, boss > ");
      return __isoc99_scanf("%31s", mem[v1]);
    }
    Nhập input cho index
    release()
    {
      int v0; // eax
      v0 = read();
      free((void *)mem[v0]);
    }
    free nhưng không set con trỏ về null nên có bug use after free.
    printf("Welcome. I'll keep it simple.\nI'll even give you a present, if you manage to unwrap it...\n%p\n", &printf);
    Hàm main cho ta địa chỉ của printf nên ta không cần phải leak, từ địa chỉ trên tính được libc_base và one_gadget.
    
Với libc đề cho sẵn là libc-2.27.so, ở phiên bản này tcache sẽ không check lỗi double free nên ta sẽ dùng lỗi này để ghi đè __free_hook thành one_gadget.
Ta sẽ malloc rồi free sau đó dùng bug UAF để edit fd thành địa chỉ của __free_hook, lúc này trong tcache bin sẽ là: [0] -> __free_hook, tiếp đến ta malloc sẽ lấy [0] trong bin ra, sau đó malloc thêm 1 lần nữa thì lần này sẽ là địa chỉ của __free_hook được malloc, cuối cùng ta chỉ cần edit với địa chỉ one_gadget là ghi đè thành công. Gọi free và get shell.
      <h4>
        
      [+] Opening connection to chal.imaginaryctf.org on port 42007: Done
      [*] '/mnt/c/Users/ADMIN/Desktop/ctf/imageCTF/Memory pile/memory_pile'
          Arch:     amd64-64-little
          RELRO:    Full RELRO
          Stack:    Canary found
          NX:       NX enabled
          PIE:      PIE enabled
          RUNPATH:  './'
      [*] '/mnt/c/Users/ADMIN/Desktop/ctf/imageCTF/Memory pile/libc-2.27.so'
          Arch:     amd64-64-little
          RELRO:    Partial RELRO
          Stack:    Canary found
          NX:       NX enabled
          PIE:      PIE enabled
      Base:  0x7f883039b000
      free_hook:  0x7f88307888e8
      One:  0x7f88303ea3c2
      Done
      [*] Switching to interactive mode
      $ cat flag.txt
      ictf{hemlock_for_the_tcache}
      $
