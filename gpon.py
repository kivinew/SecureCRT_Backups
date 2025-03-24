# $language = "Python3"
# $interface = "1.0"

import pyperclip
crt.Screen.Synchronous = True	

ontInfo = "display ont info " # информация об ONT
ifaceGpon = "interface gpon "  # интерфейс GPON
undoServPort = "undo service-port "  # удаление сервис портов
ontDelete = "ont delete "  # удаление ONT

class Ont():
	def __init__(self, frame='0', slot='0', port='0', ont_id='0'):
		self.frame = frame
		self.slot = slot
		self.port = port
		self.ont_id = ont_id
		self.sn: str = ""
		self.srvPort: list = []

	# вывод конфигурации ONT
	def getCurrentConfig(self) -> str:
		return str(self.srvPort)

	# метод удаления ONT
	def deleteOnt(self) -> None:
		crt.Screen.Send(f'display current-configuration ont {self.frame}/{self.slot}/{self.port} {self.ont_id}\n')

		# поместить вывод команды до строки "return" в буфер
		strResult: str = crt.Screen.ReadString('return')

		# разделение строки на список слов
		currentConfiguration: list = strResult.replace('\\n', ' ').split()

		# поиск сервис портов в списке слов
		for index, elem in enumerate(currentConfiguration):
			if elem == 'service-port':
				crt.Screen.Send(undoServPort + str(currentConfiguration[index + 1]) + '\r')  	# удалить найденный в списке сервис порт

		# удалить ONT с интерфейса GPON
		crt.Screen.Send(ifaceGpon + str(self.frame) + '/' + str(self.slot) + '\r')
		crt.Screen.Send(ontDelete + str(self.port) + ' ' + str(self.ont_id) + '\r')
		crt.Screen.Send('q\r' + '\r')

	# метод вывода серийника
	def getSerial(self) -> str:

		return self.sn
		
	# метод вывода уровня сигнала	
	def getOpticalInfo(self) -> str:
		pass
		return ''

	def setServicePorts(self) -> list:
		return self.srvPort


def main():

	memBuffer = pyperclip.paste()
	ONT = memBuffer.replace('/', ' ').split()
	frame: str    = ONT[0]
	slot: str     = ONT[1]
	port: str     = ONT[2]
	ont_id: str   = ONT[3]
	terminal = Ont(frame, slot, port, ont_id)
	crt.Screen.Send(f'{ontInfo} {frame} {slot} {port} {ont_id}\rq')
	terminal.getCurrentConfig()

main()
