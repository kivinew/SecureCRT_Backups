# $language = "Python3"
# $interface = "1.0"

import pyperclip
import re

def is_mac_address(text):
    """
    Проверяет, является ли текст MAC-адресом.
    Формат MAC-адреса: XX:XX:XX:XX:XX:XX или XXXX.XXXX.XXXX
    """
    mac_pattern = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$|^([0-9A-Fa-f]{4}[.]){2}([0-9A-Fa-f]{4})$")
    return bool(mac_pattern.match(text))

def is_interface_name(text):
    """
    Проверяет, является ли текст именем интерфейса.
    Примеры имен интерфейсов: Gi0/1, Te1/0/1, Fa0/1
    """
    interface_pattern = re.compile(r"^(gi|te|fa)\d+(\/\d+)*$", re.IGNORECASE)
    return bool(interface_pattern.match(text))

def main():
    # Получаем содержимое буфера обмена
    memBuffer = pyperclip.paste().strip()  # Убираем лишние пробелы
    
    if not memBuffer:
        crt.Dialog.MessageBox("Буфер обмена пуст.", "Ошибка", 16)
        return
    # Определяем команду в зависимости от содержимого буфера
    if is_mac_address(memBuffer):
        command = f"show mac address-table address {memBuffer}\r"
    elif is_interface_name(memBuffer):
        command = f"show mac address-table interface {memBuffer}\r"
    else:
        command = "show mac address-table"

    # Отправляем команду на устройство
    crt.Screen.Send(command)

main()