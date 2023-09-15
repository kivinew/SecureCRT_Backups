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
		dashLine = "------------------------------------------------------------------------------"

		getMac = "display mac-address ont " + frame + "/" + slot + "/" + port + " " + ont + "\r" + chr(13)
		ifaceGpon = "interface gpon " + frame + "/" + slot + chr(13)
		getOntInfo = "disp ont info " + frame + " " + slot + " " + port + " " + ont + chr(13) 
		getWanInfo = "display ont wan-info " + frame + "/" + slot + " " + port + " " + ont + chr(13)
		getOpticalInfo = "display ont optical-info " + port + " " + ont + chr(13)
		getRegisterInfo = "display ont register-info " + port + " " + ont + chr(13)
		getEthPorts = "display ont port  state " + port + " " + ont + " eth-port all" + chr(13)

		crt.Screen.Send(getMac)
		crt.Screen.Send(getOntInfo)
		if (crt.Screen.WaitForStrings(pressQ, 5)):
			crt.Screen.Send("q\r")
		crt.Screen.Send(getWanInfo)
		crt.Screen.Send("q\r")
		crt.Screen.WaitForStrings("(config)#")
		crt.Screen.Send(ifaceGpon)
		crt.Screen.Send(getOpticalInfo)
		if (crt.Screen.WaitForStrings(pressQ, 5)):
			crt.Screen.Send("q\r")
		crt.Screen.Send(getRegisterInfo)
		if (crt.Screen.WaitForStrings(pressQ, 5)):
			crt.Screen.Send("q\r")
		crt.Screen.WaitForStrings(dashLine, 3)
		crt.Screen.Send(getEthPorts)
		crt.Screen.Send("q\r")

main()