# $language = "Python3"
# $interface = "1.0"

import pyperclip

crt.Screen.Synchronous = True	

def main():
	
	memBuffer = pyperclip.paste()

	ONT = memBuffer.replace('/', ' ').split()

	frame: str = ONT[0]
	slot: str  = ONT[1]
	port: str  = ONT[2]
	ont: str   = ONT[3]
	
	
	crt.Screen.Send(f'display ont wan-info {frame}/{slot} {port} {ont}\r')
	crt.Sleep(1000)

main()