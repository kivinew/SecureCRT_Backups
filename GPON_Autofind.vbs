# $language = "Python3"
# $interface = "1.0"

# Прописка терминала из autofind
# Скопируй данные board/slot/port вместе с серийным номером. 
# Например:
# 0/3/14
# 485754436A7D3C13

import pyperclip

crt.Screen.Synchronous = True	

def main():
	
	memBuffer = pyperclip.paste()

	ONT = memBuffer.replace('/', ' ').split()

	board: str = ONT[0]
	slot: str  = ONT[1]
	port: str  = ONT[2]
	sn: str   = ONT[3]
	
	crt.Screen.Send('interface gpon ' + board + '/' + slot + chr(13))
	crt.Screen.Send(f'ont add {port} sn-auth {sn} omci' + chr(13))
	crt.Sleep(1000)
	crt.Screen.Send('\n')
	crt.Screen.Send('q\n')

main()