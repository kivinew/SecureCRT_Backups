# $language = "Python3"
# $interface = "1.0"

import pyperclip

crt.Screen.Synchronous = True	

def main():
	# поместить выделенный фрагмент в буфер
	memBuffer = pyperclip.paste()

	# разбить содержимое буфера в список
	ONT = memBuffer.replace('/', ' ').split()

	sn = ONT[0]

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
		# вывод по мак адресу
		crt.Screen.Send(getMac)
		# вывод информации по ONT
		crt.Screen.Send(getOntInfo)
		if (crt.Screen.WaitForStrings(pressQ, 5)):
			crt.Screen.Send("q\r")
		# вывод сетевых настроек на терминале
		crt.Screen.Send(getWanInfo)
		crt.Screen.Send("q\r")
		crt.Screen.WaitForStrings("(config)#")
		crt.Screen.Send(ifaceGpon)
		# вывод оптического уровня
		crt.Screen.Send(getOpticalInfo)
		if (crt.Screen.WaitForStrings(pressQ, 5)):
			crt.Screen.Send("q\r")
		# вывод логов 
		crt.Screen.Send(getRegisterInfo)
		if (crt.Screen.WaitForStrings(pressQ, 2)):
			crt.Screen.Send("q\r")
		crt.Screen.WaitForStrings(dashLine, 1)
		# вывод состояния LAN портов
		crt.Screen.Send(getEthPorts)
		crt.Screen.Send("q\r")

main()