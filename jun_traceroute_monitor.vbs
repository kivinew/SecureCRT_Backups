# $language = "Python3"
# $interface = "1.0"

import pyperclip

crt.Screen.Synchronous = True	

def main():
	
	memBuffer = pyperclip.paste()
	
	if memBuffer:

		sendRequest = "traceroute monitor " + memBuffer + chr(13)

		crt.Screen.Send(sendRequest)
	
main()