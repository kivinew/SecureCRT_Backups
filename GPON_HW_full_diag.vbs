# $language = "Python3"
# $interface = "1.0"

import pyperclip

crt.Screen.Synchronous = True	
pressQ = "( Press 'Q' to break ) ----"
macAddress = "display mac-address ont "
ifaceGpon = "interface gpon "
ontInfo = "display ont info "
ontVersion = "display ont version "

wanInfo = "display ont wan-info "
opticalInfo = "display ont optical-info "
registerInfo = "display ont register-info "
ethPorts = "display ont port state "
ontLineQuality = "statistics ont-line-quality "

def main():
	# поместить выделенный фрагмент в буфер
	memBuffer = pyperclip.paste()

	# разбить содержимое буфера в список
	ONT = memBuffer.replace('/', ' ').split()

	frame = ONT[0]
	slot  = ONT[1]
	port  = ONT[2]
	ont   = ONT[3]

	if memBuffer:

		# вывод информации по ONT
		crt.Screen.Send(f"{ontVersion} {frame} {slot} {port} {ont}\r")
		crt.Screen.Send(f"{ontInfo} {frame} {slot} {port} {ont}\r")
		if (crt.Screen.WaitForString(pressQ)):
			crt.Screen.Send("q\r")

		crt.Screen.WaitForString("(config)#", 1)

		crt.Screen.Send(f"{ifaceGpon} {frame}/{slot}\r")
		crt.Screen.Send(f"ont remote-ping {port} {ont} ip-address 8.8.8.8\r")

		# вывод оптического уровня
		crt.Screen.Send(f"{opticalInfo} {port} {ont}\r ")
		if (crt.Screen.WaitForString(pressQ, 1)):
			crt.Screen.Send(" \r")

		# вывод логов 
		crt.Screen.Send(f"{registerInfo} {port} {ont}\r ")
		# if (crt.Screen.WaitForString(pressQ)):
		crt.Screen.Send(" \r")
		crt.Screen.Send(" \r")

		# вывод состояния LAN портов
		crt.Screen.Send(f"{ethPorts} {port} {ont} eth-port all\r")

		# и ошибки на порту
		crt.Screen.Send(f"display {ontLineQuality} {port} {ont}\r")
		crt.Screen.Send(f"clear {ontLineQuality} {port} {ont}\r")
		crt.Screen.Send(" q\r")

		# вывод по мак адресу
		crt.Screen.Send(f"{macAddress} {frame}/{slot}/{port} {ont}\r\r")
		
		# вывод сетевых настроек на терминале
		crt.Screen.Send(f"{wanInfo} {frame}/{slot} {port} {ont}\n")
		while crt.Screen.WaitForString(pressQ, 1) > 0:	
			crt.Screen.Send(" ")

main()
