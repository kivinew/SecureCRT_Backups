# $language = "Python3"
# $interface = "1.0"

# Для работы скрипта скопируй последние 4 символа мак-адреса
import pyperclip

crt.Screen.Synchronous = True	

def main():
	
	strSelection = pyperclip.paste()
	
	split_chars = '.-: '

	mac = strSelection.translate(str.maketrans('', '', split_chars))

	find_str = "display mac-address all | include " + mac + "\r"
	
	crt.Screen.Send(find_str)
	
main()
