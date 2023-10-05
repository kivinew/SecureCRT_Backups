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
		pressQ = "( Press 'Q' to break ) ----"

		servicePorts = "display current-configuration ont " + frame + "/" + slot + "/" + port + " " + ont + chr(13)
		ifaceGpon = "interface gpon " + frame + "/" + slot + chr(13)
		undoServPort = "undo service-port "

		crt.Screen.Send(servicePorts)
				
		strResult = crt.Screen.ReadString("return")

		list = strResult.replace('\\n', ' ').split()

		for index, elem in enumerate(list):
			if elem == "service-port":
				crt.Screen.Send("undo service-port " + str(list[index + 1]) + chr(13))

		crt.Screen.Send("interface gpon " + frame + '/' + slot + chr(13))
		crt.Screen.Send("ont delete " + port + ' ' + ont + chr(13) + 'q\r')
			
main()