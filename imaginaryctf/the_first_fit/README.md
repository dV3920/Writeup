<h1>Writeup imaginaryctf 2021</h1>
<h1>Author: dV</h1>
<h2>Challenge Name: the_first_fit</h2>
<h3>Reversing file</h3>
  <h4>
  
    #include <stdio.h>
    #include <stdlib.h>

    int main()
    {
      int choice, choice2;
      char *a = malloc(128);
      char *b;
      setvbuf(stdout,NULL,2,0);
      setvbuf(stdin,NULL,2,0);
      while (1) {
        printf("a is at %p\n", a);
        printf("b is at %p\n", b);
        printf("1: Malloc\n2: Free\n3: Fill a\n4: System b\n> ");
        scanf("%d", &choice);
        switch(choice) {
          case 1:
                  printf("What do I malloc?\n(1) a\n(2) b\n>> ");
                  scanf("%d", &choice2);
                  if (choice2 == 1)
                    a = malloc(128);
                  else if (choice2 == 2)
                    b = malloc(128);
                  break;
          case 2:
                  printf("What do I free?\n(1) a\n(2) b\n>> ");
                  scanf("%d", &choice2);
                  if (choice2 == 1)
                    free(a);
                  else if (choice2 == 2)
                    free(b);
                  break;
          case 3: printf(">> "); scanf("%8s", a); break;
          case 4: system((char*)b); break;
          default: return -1;
        }
      }
      return 0;
    }
Bài này tác giả cho source nên mình không cần dùng ida, ở đây ta thấy bài có 4 chức năng chính là malloc(a hoặc b), free(a hoặc b), fill(a) và system(b). Mục tiêu bài này ta sẽ làm sao để fill b bằng "/bin/sh", ta để ý ở hàm free() khi free không set con trỏ về null nên có bug UAF, ta dùng bug này để fill(a) sau khi đã được free. 
  
Đầu tiên ta sẽ free(a) lúc này trong bin sẽ là địa chỉ của a.
  
Tiếp đến malloc(b) thì địa chỉ của a trong bin sẽ được cấp phát cho b vì size b bằng size a.
  
Lúc này ta có thể thấy 2 chunk a và b của chúng ta có cùng địa chỉ:
  <h4>
    
    a is at 0x55e2822422a0
    b is at 0x55e2822422a0
Giờ ta dùng bug UAF để fill(a) thì b cũng sẽ thay đổi theo. Ta chỉ cần fill("/bin/sh") rồi gọi system b là thành công.
