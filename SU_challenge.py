# $language = "Python3"
# $interface = "1.0"

import pyperclip
import hashlib

crt.Screen.Synchronous = True   

def suPassword(challenge: str) -> str:
    premd5 = bytearray(8)
    for i in range(8):
        if ord(challenge[i]) <= 0x47:
            premd5[i]=ord(challenge[i])<<1
        else:
            premd5[i]=ord(challenge[i])>>1
    print ('premd5: ',premd5)
    md5hash = hashlib.md5()
    md5hash.update(premd5)
    print ('md5: ',md5hash.hexdigest())
    prepass = bytearray(md5hash.digest())
    challpass = bytearray(8)
    for i in range(8):
        temp2=(prepass[i]>>1)*0xB60B60B7
        temp2=temp2>>(5+32)
        temp1=temp2<<3
        temp1=temp1-(temp2<<1)
        temp3=(temp1<<4)
        temp3=temp3-temp1
        temp0=prepass[i]-temp3+0x21
        temp0=temp0&0xFF
        if temp0 == 0x3F:
            challpass[i]=0x3E
        else:
            challpass[i]=temp0
    sendPass = challpass.decode('utf-8')
    return sendPass

def main() -> None:
    memBuffer = pyperclip.paste()
    try:    
        if len(memBuffer)==8:
            supass = suPassword(memBuffer)
            pyperclip.copy(supass)
            crt.Screen.Send(f"{supass}\n")
        else:
            raise ValueError('Задание должно содержать 8 символов.')
    except Exception as e:
        crt.Dialog.MessageBox(f"Ошибка : {e}")

main()