# $language = "Python3"
# $interface = "1.0"

import pyperclip

crt.Screen.Synchronous = True	

def main():
	
	memBuffer = pyperclip.paste()
	memBuffer = memBuffer.split()
	ip, interface = memBuffer[0], memBuffer[1]
	
	if memBuffer:

		sendRequest = "clear arp interface " + interface + " vpn NAT-IPoE hostname " + ip + chr(13)

		crt.Screen.Send(sendRequest)
	
main()
