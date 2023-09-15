# $language = "Python3"
# $interface = "1.0"

import pyperclip

crt.Screen.Synchronous = True	

def main():
	
	memBuffer = pyperclip.paste()

	ONT = memBuffer.replace('/', ' ').split()

	frame = ONT[0]
	slot  = ONT[1]
	port  = ONT[2]
	ont   = ONT[3]


	crt.Screen.Send("interface gpon " + frame + "/" + slot + chr(13))
	crt.Screen.Send("ont remote-ping " + port + " " + ont + " ip-address 8.8.8.8"+ chr(13))
	crt.Screen.Send("q\r")
	
main()