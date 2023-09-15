# $language = "Python3"
# $interface = "1.0"

import pyperclip

crt.Screen.Synchronous = True	

def main():
	
	strSelection = pyperclip.paste()

	find_str = "show epon interface epon " + strSelection + " onu ctc optical-transceiver-diagnosis\r"
	
	crt.Screen.Send(find_str)
	
main()
