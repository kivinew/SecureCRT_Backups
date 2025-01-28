# $language = "Python3"
# $interface = "1.0"

# Для работы скрипта скопируй последние 4 символа мак-адреса

import pyperclip

crt.Screen.Synchronous = True	

def main():
	
	strSelection = pyperclip.paste()

	find_str = f'show epon interface epon {strSelection} onu ctc optical-transceiver-diagnosis\r'
	
	crt.Screen.Send(find_str)
	
main()
