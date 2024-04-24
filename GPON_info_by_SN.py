# $language = "Python3"
# $interface = "1.0"

import pyperclip

crt.Screen.Synchronous = True	

def main():
	
	memBuffer = pyperclip.paste()

	# Проверка на соответствие шаблону серийных номеров HUAWEI
	if not (memBuffer.startswith('48575443') or memBuffer.startswith('HWTC')):
		crt.Screen.Send("display ont info by-sn ")
		return

	crt.Screen.Send(f"display ont info by-sn {memBuffer}\rq")

main()