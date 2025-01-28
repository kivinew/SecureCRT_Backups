# $language = "Python3"
# $interface = "1.0"

# Для работы скрипта скопируй последние 4 символа мак-адреса

import pyperclip
import re

crt.Screen.Synchronous = True	

def main():
	
	strSelection = re.split(r'[: ]', pyperclip.paste())

	find_str = f'show epon onu-information detail interface epoN {strSelection[0]} {strSelection[1]}\r'
	
	crt.Screen.Send(find_str)
	
main()
