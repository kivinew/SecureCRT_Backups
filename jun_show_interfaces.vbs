# $language = "Python3"
# $interface = "1.0"

import pyperclip

crt.Screen.Synchronous = True	

def main():
	
	memBuffer = pyperclip.paste()
	
	sendRequest = "show interfaces " + memBuffer + "\r"
	
	crt.Screen.Send(sendRequest)

main()