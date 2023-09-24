# $language = "Python3"
# $interface = "1.0"

import pyperclip

crt.Screen.Synchronous = True	

def main():
	
	srvPort = pyperclip.paste()

	crt.Screen.Send("display traffic service-port " + srvPort + chr(13))

main()