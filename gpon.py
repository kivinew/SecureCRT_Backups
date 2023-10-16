# $language = "Python3"
# $interface = "1.0"

class Ont():
	def __init__(self, ontList: list = [0, 0, 0, 0]):
		self.frame = ontList[0]
		self.slot = ontList[1]
		self.port = ontList[2]
		self.ont = ontList[3]
		self.sn: str = 0
		self.srvPort: list = 0

	# вывод конфигурации ONT
	def getCurrentConfig(self) -> list:
		return str(self.srvPort)

	# метод удаления ONT
	def deleteOnt(self) -> None:
		crt.Screen.Send(servicePorts + str(self.frame) + '/' + str(self.slot) + '/' + str(self.port) + ' ' + str(self.ont) + chr(13))
		# поместить вывод команды до строки "return" в буфер
		strResult:str = crt.Screen.ReadString("return")
		# разделение строки на список слов
		currentConfiguration:list = strResult.replace('\\n', ' ').split()
		# поиск сервис портов в списке слов
		for index, elem in enumerate(currentConfiguration):
			if elem == "service-port":
				crt.Screen.Send(undoServPort + str(currentConfiguration[index + 1]) + chr(13))  	# удалить найденный в списке сервис порт
		# удалить ONT с интерфейса GPON
		crt.Screen.Send(ifaceGpon + str(self.frame) + '/' + str(self.slot) + chr(13))
		crt.Screen.Send(ontDelete + str(self.port) + ' ' + str(self.ont) + chr(13))
		crt.Screen.Send("q\r" + chr(13))

	# метод вывода серийника
	def getSerial(self) -> str:
		return self.sn
		
	# метод вывода уровня сигнала	
	def getOpticalInfo(self) -> str:
		return pass

	def setServicePorts(self) -> None:
		pass