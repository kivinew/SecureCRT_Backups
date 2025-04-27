# $language = "Python3"
# $interface = "1.0"

import pyperclip
import re

def read_output() -> str:
    """Чтение вывода в терминал построчно"""
    output = ""
    while True:
        line = crt.Screen.ReadString("\n", 1)
        if not line:
            break
        output += line
    return output

def main():
	memBuffer = pyperclip.paste().strip()
	ONT = memBuffer.replace('/', ' ').split()
	frame, slot, port, ont = ONT
	crt.Screen.Send(f'display ont wan-info {frame}/{slot} {port} {ont}\r ')
	output = read_output()
	match = re.search(r'IPv4 address\s+:\s(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})', output)
	pyperclip.copy(match.group(1))

main()