# $language = "Python"
# $interface = "1.0"

import pyperclip

crt.Screen.Synchronous = True

def main():
	memBuffer = pyperclip.paste()

	crt.Screen.Send ("show ip nat translations inside " + memBuffer + " total" + chr(13))
main()