# $language = "Python3"
# $interface = "1.0"

import pyperclip
crt.Screen.Synchronous = True	

def main():
	memBuffer = pyperclip.paste()
	ONT = memBuffer.replace('/', ' ').split()
	frame, slot, port, ont = ONT
	crt.Screen.Send(f'diagnose\ront wan-access http {frame}/{slot}/{port} {ont} enable\rconfig\r')
main()