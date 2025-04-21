# $language = "Python3"
# $interface = "1.0"

# crt = None  # глобальная переменная для crt

# class Test():
# 	def inject_crt(obj_crt):
# 		global crt
# 		crt = obj_crt

# 	def send_command(command):
# 		if crt is not None:
# 			crt.Screen.Send(command + "\n")
# 		else:
# 			print("Ошибка: crt не инициализирован!")

import pyperclip

crt.Screen.Synchronous = True	

ont_info = "display ont info" # информация об ONT
ifaceGpon = "interface gpon"  # интерфейс GPON
undoServPort = "undo service-port"  # удаление сервис портов
ontDelete = "ont delete "  # удаление ONT

class Ont():
	def __init__(self, ont: list):
		self.frame = ont[0]
		self.slot = ont[1]
		self.port = ont[2]
		self.ont_id = ont[3]
		self.sn: str = ''
		self.srvPort: list = []

	def get_ont_info(self) -> None:
		frame, slot, port, ont = self.frame, self.slot, self.port, self.ont_id
		crt.Screen.Send(f"{ont_info} {frame} {slot} {port} {ont}\rq")

	# вывод конфигурации ONT
	def get_current_config(self) -> str:
		return str(self.srvPort)

	# метод удаления ONT
	def delete_ont(self) -> None:
		crt.Screen.Send(f'display current-configuration ont {self.frame}/{self.slot}/{self.port} {self.ont_id}\n')

	# 	# поместить вывод команды до строки "return" в буфер
		strResult: str = crt.Screen.ReadString('return')

	# 	# разделение строки на список слов
		currentConfiguration: list = strResult.replace('/', ' ').split()

	# 	# поиск сервис портов в списке слов
		for index, elem in enumerate(currentConfiguration):
			if elem == 'service-port':
				# crt.Screen.Send(undoServPort + str(currentConfiguration[index + 1]) + '\r')  	# удалить найденный в списке сервис порт
				pass
	# 	# удалить ONT с интерфейса GPON
		crt.Screen.Send(ifaceGpon + str(self.frame) + '/' + str(self.slot) + '\r')
		crt.Screen.Send(ontDelete + str(self.port) + ' ' + str(self.ont_id) + '\r')
		crt.Screen.Send('q\r' + '\r')

	# метод вывода серийника
	def get_serial(self) -> str:
		return self.sn
		
	# метод вывода уровня сигнала	
	def get_optical_info(self) -> str:
		crt.Screen.Send(f"display ont optical-info {self.port} {self.ont_id}")
		return ''

	def set_service_ports(self) -> list:
		return self.srvPort


def main() -> None:

	mem_buffer = pyperclip.paste().strip()
	ont: Ont = Ont(mem_buffer.replace('/',' ').split())
	ont.get_ont_info()


main()

