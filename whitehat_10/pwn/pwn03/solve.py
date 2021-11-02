from pwn import *
#p=process('./Stack')
p=remote('103.229.41.18',5558)
elf = ELF('./Stack')

payload = "AABBCCDD"
p.sendline(payload)

p.interactive()