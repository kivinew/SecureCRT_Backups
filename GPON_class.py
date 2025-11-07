# $language = "Python3"
# $interface = "1.0"

import pyperclip

# Текстовые константы
pressQ = "( Press 'Q' to break ) ----"
ont_info = "display ont info" # информация об ONT
optic = "display ont optical-info" 
servicePorts = "display current-configuration ont " # конфигурация ont
ifaceGpon = "interface gpon "
undoServPort = "undo service-port port"
ont_delete = "ont delete "

# Глобальная ссылка на объект crt (инициализируется из основного скрипта)
def inject_crt(obj):
    """Инъекция SecureCRT-объекта crt. Вызывать обязательно из основного скрипта после импорта этого модуля."""
    global crt
    crt = obj

class Ont:
    def __init__(self, ontSelect:list=[]):
        """Инициализация объекта ONT из списка параметров (frame, slot, port, ont)."""
        memBuffer = pyperclip.paste()
        ontSelect = memBuffer.replace('/', ' ').split()
        if ontSelect is None or len(ontSelect) < 4:
            raise ValueError("Некорректное содержимое буфера")
        self.frame = ontSelect[0]
        self.slot = ontSelect[1]
        self.port = ontSelect[2]
        self.ont = ontSelect[3]
        self.sn = ontSelect[4] if len(ontSelect) > 4 else ""

    def delete_ont(self) -> None:
        """
        Удаление сервисных портов и самой ONT.
        Показывает сообщения об ошибках пользователю.
        """
        scr = crt.Screen
        if crt is None:
            raise RuntimeError("CRT не инициализирован.")
        try:
            scr.Send(f"{undoServPort} {self.frame}/{self.slot}/{self.port} ont {self.ont}\r")
            scr.WaitForString("gemport", 5)
            scr.Send("\r")
            scr.WaitForString("(y/n)", 5)
            scr.Send("y\r")
            scr.Send(f"{ifaceGpon} {self.frame}/{self.slot}\r")
            scr.Send(f"{ont_delete} {self.port} {self.ont}\r")
            scr.Send("q\r")
        except Exception as e:
            crt.Dialog.MessageBox(f"Ошибка при удалении ONT: {e}")

    def get_optic(self) -> None:
        """Получает уровень оптики"""
        scr = crt.Screen
        if crt is None:
            raise RuntimeError("CRT не инициализирован.")
        scr.Send(f"{ifaceGpon} {self.frame}/{self.slot}\r")
        scr.Send(f"{optic} {self.port} {self.ont}\r")
        scr.Send(" quit\r")

    def get_info(self) -> None:
        """Получает информацию об ONT."""
        if crt is None:
            raise RuntimeError("CRT не инициализирован.")
        try:
            crt.Screen.Send(f"{ont_info} {self.frame} {self.slot} {self.port} {self.ont}\rq")
        except Exception as e:
            crt.Dialog.MessageBox(f"Ошибка при получении данных ONT: {e}")

    def set_serial(self, serial: str) -> None:
        """Устанавливает серийный номер ONT."""
        scr = crt.Screen
        if crt is None:
            raise RuntimeError("CRT не инициализирован.")
        scr.Send(f"{ifaceGpon} {self.frame}/{self.slot}\r")
        self.sn = serial

if __name__ == "builtins":
    try:
        memBuffer = pyperclip.paste()
        ontSelect = memBuffer.replace('/', ' ').split()
        ont = Ont(ontSelect)
        ont.get_info()
    except pyperclip.PyperclipException as e:
        crt.Dialog.MessageBox(f"Ошибка чтения буфера обмена:\r{e}")
    except ValueError as e:
        crt.Dialog.MessageBox(f"Ошибка при получении данных об ONT: {e}")
    except Exception as e:
        crt.Dialog.MessageBox(f"Ошибка при выполнении:\r{e}")
