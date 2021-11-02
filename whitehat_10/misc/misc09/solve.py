from pwn import *
p=remote('103.229.41.18',8084)


def tinh(n):
	kq = (2*n*(2*n-1))/2
	return kq

p.recvuntil('n:\n')
n = int(p.recvuntil("\n"))
p.sendline(str(tinh(n)))
while(1):
	s = p.recvuntil("\n")
	if "Flag" in s:
		print "Bingo: ",s
		break
	print s
	n = int(s)
	p.sendline(str(tinh(n)))
p.interactive()