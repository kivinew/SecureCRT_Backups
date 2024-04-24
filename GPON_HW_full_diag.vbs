# $language = "Python3"
# $interface = "1.0"

import pyperclip

crt.Screen.Synchronous = True	
pressQ = "( Press 'Q' to break ) ----"
dashLine = "------------------------------------------------------------------------------"

getMac = "display mac-address ont "
ifaceGpon = "interface gpon "
getOntInfo = "disp ont info "
getWanInfo = "display ont wan-info "
getOpticalInfo = "display ont optical-info "
getRegisterInfo = "display ont register-info "
getEthPorts = "display ont port state "
getOntLineQuality = "display statistics ont-line-quality "

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
		# вывод по мак адресу
		crt.Screen.Send(f'{getMac} {frame}/{slot}/{port} {ont}\r\r')

		# вывод информации по ONT
		crt.Screen.Send(f'{getOntInfo} {frame} {slot} {port} {ont}\r')
		if (crt.Screen.WaitForString(pressQ)):
			crt.Screen.Send('q\r')

		# вывод сетевых настроек на терминале
		crt.Screen.Send(f'{getWanInfo} {frame}/{slot} {port} {ont}\r')
		crt.Screen.Send('\r')
		crt.Screen.WaitForString('(config)#')

		crt.Screen.Send(f'{ifaceGpon} {frame}/{slot}\r')
		crt.Screen.Send(f'ont remote-ping {port} {ont} ip-address 8.8.8.8\r')

		# вывод оптического уровня
		crt.Screen.Send(f'{getOpticalInfo} {port} {ont}\r')
		if (crt.Screen.WaitForString(pressQ, 3)):
			crt.Screen.Send(" \r")

		# вывод логов 
		crt.Screen.Send(f'{getRegisterInfo} {port} {ont}\r')
		if (crt.Screen.WaitForString(pressQ, 1)):
			crt.Screen.Send("   ")
		crt.Screen.WaitForString(dashLine, 1)

		# вывод состояния LAN портов
		crt.Screen.Send(f'{getEthPorts} {port} {ont} eth-port all\r')

		# и ошибки на порту
		crt.Screen.Send(f'{getOntLineQuality} {port} {ont}\r')
		crt.Screen.Send('q\r')

main()
