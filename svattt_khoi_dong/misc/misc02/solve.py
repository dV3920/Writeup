from pwn import *
p=remote('125.235.240.166',20103)

p.recvuntil("\n")
p.recvuntil("\n")


while(1):

	a = p.recvuntil("\n")
	print a
	if "*" in a:
		s = a.split("*")
		so1 = int(s[0],10)
		so2 = s[1].split("=")
		so2 = int(so2[0],10)
		kq = so1*so2
		p.sendline(str(kq))
		s = p.recvuntil("\n")
		#print "S: ",s
		if "ASCIS" in s:
			print "S: ",s
			break
		p.recvuntil("\n")

	elif "+" in a:
		s = a.split("+")
		so1 = int(s[0],10)
		so2 = s[1].split("=")
		so2 = int(so2[0],10)
		kq = so1+so2
		p.sendline(str(kq))
		s = p.recvuntil("\n")
		#print "S: ",s
		if "ASCIS" in s:
			print "S: ",s
			break
		p.recvuntil("\n")

	elif "-" in a:
		s = a.split("-")
		so1 = int(s[0],10)
		so2 = s[1].split("=")
		so2 = int(so2[0],10)
		kq = so1-so2
		p.sendline(str(kq))
		s = p.recvuntil("\n")
		#print "S: ",s
		if "ASCIS" in s:
			print "S: ",s
			break
		p.recvuntil("\n")

	elif "/" in a:
		s = a.split("/")
		so1 = int(s[0],10)
		so2 = s[1].split("=")
		so2 = int(so2[0],10)
		kq = so1/so2
		p.sendline(str(kq))
		s = p.recvuntil("\n")
		#print "S: ",s
		if "ASCIS" in s:
			print "S: ",s
			break
		p.recvuntil("\n")


p.interactive()