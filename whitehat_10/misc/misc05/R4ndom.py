import random

enc = [121, 96, 19, 98, 89, 66, 82, 65, 31, 122, 47, 30, 54, 71, 90, 52, 40, 44, 60, 80, 49, 106, 8, 107, 48, 102, 91, 48]
key = list(random.randint(0, 128) for i in range(len(enc)))
dec = list((x ^ y) for x, y in zip(enc, key))
flag = "".join(chr(i) for i in dec)
print(flag)




import random

enc = [121, 96, 19, 98, 89, 66, 82, 65, 31, 122, 47, 30, 54, 71, 90, 52, 40, 44, 60, 80, 49, 106, 8, 107, 48, 102, 91, 48]
tmp = 0
while True:
 tmp+=1
 random.seed(tmp)
 key = list(random.randint(0, 128)  for i in range(len(enc)))
 dec = list((x ^ y) for x, y in zip(enc, key))
 flag = "".join(chr(i) for i in dec)
 if flag.find("WhiteHat") > -1:
  print(flag)
  break
