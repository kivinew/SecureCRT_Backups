# $language = "Python3"
# $interface = "1.0"

import pyperclip

crt.Screen.Synchronous = True	

def main():
	
	memBuffer = pyperclip.paste()
	
	if memBuffer:

		sendRequest = "ping " + memBuffer + " detail record-route" + chr(13)

		crt.Screen.Send(sendRequest)
	
main()