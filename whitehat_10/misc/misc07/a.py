import random
flagenc  = '936680065836676583668665826980365' 
key = 'oldtr4ff0rd'
LETTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
LETTERS = LETTERS.lower()

def decrypted(flag, key):
    
    for rd in key:
        encrypted = ''
        rd_number = ord(rd)%27
        i  = 0
        while i < len(flag): 
            s = int(flag[i:i+2]) ^ ord(rd) ^  key.index(rd)
            
            if chr(s) not in LETTERS:
                s = int(flag[i]) ^ ord(rd) ^  key.index(rd)
                i += 1
            else:
                i += 2
            encrypted += chr(s) 
        
        decrypted = ''
        for chars in encrypted:
                num  =  LETTERS.find(chars) 
                num -= rd_number
                decrypted += LETTERS[num]
                
        print('dec = ',decrypted) 
        print('----------------------------------------------')
        
      
          
def main():
    print(decrypted('936680065836676583668665826980365','oldtr4ff0rd'))
    


if __name__ == '__main__':
    main()