# $language = "Python3"
# $interface = "1.0"

# Для работы скрипта скопируй данные ont ( пример: 0/1/1 1 )

import time
import re
import pyperclip
crt.Screen.Synchronous = True	

def main():

	# текстовые константы
	pressQ = "( Press 'Q' to break ) ----"
	servicePorts = "display current-configuration ont "
	ifaceGpon = "interface gpon "
	undoServPort = "undo service-port "
	ontDelete = "ont delete "

	class Ont():
		def __init__(self, ontList: list = [0, 0, 0, 0]):
			self.frame = ontList[0]
			self.slot = ontList[1]
			self.port = ontList[2]
			self.ont = ontList[3]
			self.sn: str = 0
			self.srvPort: list = self._get_service_ports()

		# вывод конфигурации ONT
		def _get_service_ports(self) -> list:
			command: str = f"display current-configuration ont {self.frame}/{self.slot}/{self.port} {self.ont}\n"
			crt.Screen.Send(command)
			# чтение в буфер экрана до строки "return"
			console_output = crt.Screen.ReadString("return")
			# Шаблон для поиска строк с сервис-портами
			service_port_pattern = re.compile(r'service-port (\d+)')

			# Найдем все совпадения с шаблоном
			service_ports = service_port_pattern.findall(console_output)

			# Преобразуем найденные значения в список целых чисел
			service_ports = [int(port) for port in service_ports]

			return service_ports

		# метод удаления ONT
		def delete(self) -> None:
			""" Удаление всех сервис портов. """
			service_ports = self.srvPort

			for port in service_ports:
				command = f"undo service-port {port}\n"
				crt.Screen.Send(command)

			crt.Screen.Send(f"{ifaceGpon} {self.frame}/{self.slot}\n")
			crt.Screen.Send(f"ont delete {self.port} {self.ont}\n")
			crt.Screen.Send("q\n")

	# поместить выделенный фрагмент экрана в буфер
	memBuffer = pyperclip.paste()
	ontSelect = memBuffer.replace('/', ' ').split()

	# создать объект Ont
	ont: Ont = Ont(ontSelect)

	# удалить Ont
	ont.delete()
			
main()