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

	if memBuffer:
		
		crt.Screen.Send("display current-configuration ont " + frame + "/" + slot + "/" + port + " " + ont + chr(13))

		if (crt.Screen.WaitForStrings("( Press 'Q' to break ) ----", 1)):
			crt.Screen.Send(' ' + '\r')
			
main()