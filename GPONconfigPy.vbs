# $language = "Python3"
# $interface = "1.0"
import pyperclip
crt.Screen.Synchronous = True	

def main():
	memBuffer = pyperclip.paste()

	ONT = memBuffer.replace('/', ' ').split()

	frame: str = ONT[0]
	slot: str  = ONT[1]
	port: str  = ONT[2]
	ont: str   = ONT[3]
 
	'''
	 HS8545M5_WAN - 80 порт
	 WanAccess - порт 88
	 WanAccess_HG8245 - порт 80
	 WanAccess | WanAccess_HG8245 | all | IP | wifi | inet_tv_wifi_vlan2 | inet_tv_wifi_test
	'''


	# содержит True, если получена указанная в аргументах одна из строк
	condition: bool = False
	# состояние заливки конфига в цикле while/wend
	status: bool =True

	# номер лицевого счёта для дескрипшена
	description: str
	# файл конфигурации
	conf: str

	conf        = "WanAccess_HG8245"
	description = "fl_70921"
	#########################################################################################################'

	crt.Screen.Send("display ont version 0 " + slot + " " + port + " " + ont + chr(13))
	crt.Screen.Send("diagnose" + chr(13))
	crt.Screen.Send("ont-load info configuration " + conf + ".xml ftp 10.2.1.3 huawei ksa5oz6y" + chr(13))
	crt.Screen.Send("ont-load select 0/" + slot + " " + port + " " + ont + chr(13))
	crt.Screen.Send("ont-load start" + chr(13) + chr(13))


	# цикл проверки загрузки конфигурации
	while (status):
		crt.Screen.Send("display ont-load select 0/" + slot + " " + port + " " + ont + chr(13))
		condition = crt.Screen.WaitForStrings("Success", "Fail", "Loading")
		match condition:
			case ["Success"]:
				# Конфига залита - выход из цикла опроса'
				status=false
			case ["Fail"]:
				# Сбой конфигурации - выход из цикла опроса
				status=false
				crt.Dialog.MessageBox("Сбой конфигурации")
			case _:
				# Пауза 2 сек'
				crt.Sleep(2000)
	wend 


# Завершение конфигурации в режиме diagnoseS'
	crt.Screen.Send("ont-load stop" + chr(13))
	crt.Screen.Send("config" + chr(13))
	crt.Screen.Send("interface gpon 0/" + slot + chr(13))
# Если конфига с пропиской IP то вывести настройки WAN интерфейса'    
	if (conf == "all") or (conf == "IP") or (conf == "inet_tv_wifi_vlan2"):
		crt.Screen.Send("display ont wan-info " + port + " " + ont + chr(13))
	
	crt.Screen.WaitForString(")#")
	crt.Screen.Send("ont modify " + port + " " + ont + " desc " + description + chr(13))
	crt.Screen.Send("ont remote-ping " + port + " " + ont + " ip-address 8.8.8.8" + chr(13))
	crt.Screen.Send("quit" + chr(13))

main()