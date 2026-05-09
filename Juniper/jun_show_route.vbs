# $language = "Python"
# $interface = "1.0"

import pyperclip

crt.Screen.Synchronous = True	

def main():
	
	memBuffer = pyperclip.paste()
	
	if memBuffer:

		sendRequest = f"show route {memBuffer}\n \n"

		crt.Screen.Send(sendRequest)
	
main()