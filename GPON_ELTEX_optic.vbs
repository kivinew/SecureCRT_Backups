# $language = "Python3"
# $interface = "1.0"

# Для проверки уровня сигнала скопируй в буфер обмена строку ONT формата "x/xx"
import pyperclip
crt.Screen.Synchronous = True	

def main():
	
	memBuffer = pyperclip.paste().strip()

	ONT = memBuffer.replace('/', ' ').split()

	port: str  = ONT[0]
	ont: str   = ONT[1]
		
	crt.Screen.Send(f'show interface ont {port}/{ont} laser\r')
	crt.Sleep(1000)

main()