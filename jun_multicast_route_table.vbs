# $language = "Python3"
# $interface = "1.0"

import pyperclip

crt.Screen.Synchronous = True	

def main():
	
	memBuffer = pyperclip.paste()
	
	sendRequest = f"show route table inet.1 | match {memBuffer}\n"
	
	crt.Screen.Send(sendRequest)

main()