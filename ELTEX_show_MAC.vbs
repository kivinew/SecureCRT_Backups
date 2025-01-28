# $language = "Python3"
# $interface = "1.0"

# Для работы скрипта скопируй последние 4 символа мак-адреса

import pyperclip

crt.Screen.Synchronous = True	

def main():
	
	mac = pyperclip.paste()
	
	crt.Screen.Send(f'show mac interface ont 0-3 include mac-address {mac}\r')
	
main()
