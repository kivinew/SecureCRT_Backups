# $language = "Python3"
# $interface = "1.0"

import pyperclip
import re

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

		srvPort1 = list.index("service-port") + 1
		srvPort2 = list.index("service-port") + 1
		srvPort3 = list.index("service-port") + 1
		srvPort4 = list.index("service-port") + 1

		"""
		crt.Screen.Send("display service-port " + list[srvPort1] + chr(13))
		if (crt.Screen.WaitForStrings(pressQ)):
			crt.Screen.Send("q")
		"""
main()