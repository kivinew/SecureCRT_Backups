# $language = "Python3"
# $interface = "1.0"

# Для проверки по серийнику, скопировать его в буфер обмена 

import pyperclip

crt.Screen.Synchronous = True	

def main():
	
	mem_buffer = pyperclip.paste()

	# Проверка на соответствие шаблону серийных номеров HUAWEI
	if not (mem_buffer.startswith('48575443') or mem_buffer.upper().startswith('HWTC')):
		crt.Screen.Send("display ont info by-sn ")
		return

	crt.Screen.Send(f"display ont info by-sn {mem_buffer.upper()}\r")
	if (crt.Screen.WaitForString("---- More ( Press 'Q' to break ) ----", 2) == 1):
		crt.Screen.Send("q")

main()