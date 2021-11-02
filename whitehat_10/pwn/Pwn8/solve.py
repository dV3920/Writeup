from pwn import *
p=process('./feedback')
elf = ELF('./feedback')
libc = ELF('libc-2.23.so')
raw_input("DEBUG")


def create(name,passwd):
	p.sendlineafter("choice: ","1")
	p.sendlineafter("Name:",str(name))
	p.sendlineafter("password:",str(passwd))
	p.recvuntil(": ")
	uid = p.recv(1)
	log.info("Create: "+uid)


def login(name,passwd):
	p.sendlineafter("choice: ","2")
	p.sendlineafter("Name:",str(name))
	p.sendlineafter("password:",str(passwd))
	log.info("Login...")

create("a"*20,"a"*20)
create("Administrator","Administrator")
create("b","b")
login("Administrator","Administrator")

def delete():
	p.sendlineafter("choice: ","3")
	log.info("Delete")

def show():
	p.sendlineafter("choice: ","4")
#delete()
#show()

def ticket_create(uid,size,data):
	p.sendlineafter(": ","1")
	p.sendlineafter(": ","1")
	p.sendlineafter(": ","1") #help desk
	p.sendlineafter("UID:",str(uid))
	p.sendlineafter("buff:",str(size))
	p.sendlineafter("problem?",str(data))

def change_passwd(uid,data):
	p.sendlineafter(": ","1")
	p.sendlineafter(": ","1")
	p.sendlineafter(": ","2") #change_passwd
	p.sendlineafter("UID:",str(uid))
	p.sendlineafter("password:",str(data))

def open_connect(uid,ip,port):
	p.sendlineafter(": ","1")
	p.sendlineafter(": ","1")
	p.sendlineafter(": ","3") #open_connect
	p.sendlineafter("UID:",str(uid))
	p.sendlineafter("to:",str(ip))
	p.sendlineafter("Port:",str(port))

ticket_create(0,48,"s"*47)
#ticket_create(2,48,"2"*47)

p.interactive()


'''
b*0x400ca5
strncmp 0x401387
b*0x400b53
'''