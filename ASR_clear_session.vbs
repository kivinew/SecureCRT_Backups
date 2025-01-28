# $language = "Python3"
# $interface = "1.0"

import pyperclip

crt.Screen.Synchronous = True

def main():
	memBuffer = pyperclip.paste()

	crt.Screen.Send ("clear subscriber session username " + memBuffer + chr(13))
main()