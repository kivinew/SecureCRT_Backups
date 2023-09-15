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
		if (crt.Screen.WaitForStrings(pressQ, 5)):
			crt.Screen.Send(" ")

		strResult = crt.Screen.ReadString("return")



		
			
		re.Pattern = "service-port"
			

		if re.search(strResult) == True:
			matches = re.Execute(strResult)
			for match in matches:
		 		srvPorts = match.SubMatches(0)
		

		crt.Screen.Send("Serial number extracted as: " + srvPorts)



main()