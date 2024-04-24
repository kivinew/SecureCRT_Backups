# $language = "Python3"
# $interface = "1.0"

# для включения веб доступа на терминал необходимо выделить мышкой значение ONT ( например 0 /0 /7 29 )

import pyperclip
crt.Screen.Synchronous = True	

def main():
	# содержимое буфера обмена помещается в переменную
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
	 WanAccess | WanAccess_HG8245 
	'''

	# содержит True, если получена указанная в аргументах одна из строк
	condition: str

	# состояние заливки конфига в цикле while/wend
	status: bool = True

	# файл конфигурации
	conf: str

	conf = "WanAccess"

	crt.Screen.Send("diagnose" + chr(13))
	crt.Screen.Send("ont-load info configuration " + conf + ".xml ftp 10.2.1.3 huawei ksa5oz6y" + chr(13))
	crt.Screen.Send("ont-load select 0/" + slot + " " + port + " " + ont + chr(13))
	crt.Screen.Send("ont-load start" + chr(13) + chr(13))


	# цикл проверки загрузки конфигурации
	while (status):
		
		crt.Screen.Send("display ont-load select 0/" + slot + " " + port + " " + ont + chr(13))
		condition = crt.Screen.WaitForString("Success", 1)		#### Ошибка Python AN INTEGER IS REQUIRED!!!
		#crt.Dialog.MessageBox(str(condition))
		match condition:
			case 1:
				status = False
			case 2:
				# Сбой конфигурации - выход из цикла опроса
				status = False
				crt.Dialog.MessageBox("Сбой конфигурации!!!")
			case 0:
				# Пауза 2 сек'
				crt.Sleep(1000)

	# Завершение конфигурации в режиме diagnose
	crt.Screen.Send("ont-load stop" + chr(13))
	crt.Screen.Send("config" + chr(13))

main()