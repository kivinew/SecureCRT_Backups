# $language = "Python"
# $interface = "1.0"

# Для работы скрипта скопируй данные ont ( пример: 0/1/1 1 )

# import time
import pyperclip
scr = crt.Screen
scr.Synchronous = True	

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

        # метод удаления ONT
        def delete(self) -> None:
            """ Удаление всех сервис портов и ONT """
            
            # Удаляем все сервис-порты, привязанные к ONT
            command = f"undo service-port port {self.frame}/{self.slot}/{self.port} ont {self.ont}\n"
            scr.Send(command) # type: ignore
            
            # Ждем появления запроса на указание gemport и нажимаем Enter
            scr.WaitForString("(gemport)") # pyright: ignore[reportUndefinedVariable]
            scr.Send("\n")
            
            # crt.Sleep(1)
            # Ждем запроса подтверждения и нажимаем 'y'
            scr.WaitForString("[Y/N]")
            scr.Send("y\n")
            
            # Переходим в интерфейс GPON и удаляем ONT
            scr.Send(f"{ifaceGpon} {self.frame}/{self.slot}\n")
            scr.Send(f"ont delete {self.port} {self.ont}\n")
            
            # Подтверждаем удаление ONT
            scr.WaitForString("[Y/N]")
            scr.Send("y\n")
            
            # Выходим из интерфейса
            scr.Send("q\n")

    # поместить выделенный фрагмент экрана в буфер
    memBuffer = pyperclip.paste()
    ontSelect = memBuffer.replace('/', ' ').split()

    # создать объект Ont
    ont: Ont = Ont(ontSelect)

    # удалить Ont
    ont.delete()
            
main()