# $language = "Python3"
# $interface = "1.0"

import pyperclip

crt.Screen.Synchronous = True

def main():
	memBuffer = pyperclip.paste()

	crt.Screen.Send ("show subscriber session | include " + memBuffer + chr(13))
main()