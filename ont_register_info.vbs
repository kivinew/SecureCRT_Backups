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
	crt.Screen.Send("display ont register-info " + port + " " + ont + chr(13))
	crt.Screen.Send(" " + " " + " " + "q" + chr(13))
	
main()