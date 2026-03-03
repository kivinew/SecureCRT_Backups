# $language = "Python"
# $interface = "1.0"

# Для работы скрипта скопируй значение EPON ("0/1:23" или "0/1 23")

import pyperclip
import re

crt.Screen.Synchronous = True

send = crt.Screen.Send

def main():
	
	strSelection = re.split(r'[: ]', pyperclip.paste())
	port, onu = strSelection[0], strSelection[1]

	find_str = f'show epon interface EPON{port}:{onu} onu ctc basic-info\r'
	port_state = f'show epon interface EPON{port}:{onu} onu port 1 state\r'
	mac = f'show mac address-table interface epoN{port}:{onu}\r'
	mac = f'show mac address-table interface epoN{port}:{onu}\r'
	optic = f'show epon interface epon{port}:{onu} onu ctc optical-transceiver-diagnosis\r'
	onu_info = f'show epon onu-information interface epoN{port} {onu}\r'
	
	send(find_str)
	send(mac)
	send(port_state)
	send(optic)
	send(onu_info)
	
main()
