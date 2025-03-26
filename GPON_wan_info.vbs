# $language = "Python3"
# $interface = "1.0"

import pyperclip

def main():
	memBuffer = pyperclip.paste().strip()
	ONT = memBuffer.replace('/', ' ').split()
	frame, slot, port, ont = ONT
	crt.Screen.Send(f'display ont wan-info {frame}/{slot} {port} {ont}\r ')
main()