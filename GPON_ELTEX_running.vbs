# $language = "Python3"
# $interface = "1.0"
import pyperclip
import re

crt.Screen.Synchronous = True

def main():
    # Получите значение ont из буфера обмена
    ont_value = pyperclip.paste().strip()

    # Получите вывод конфигурации ONT
    crt.Screen.Send(f'show running-config interface ont {ont_value}\r')
    crt.Sleep(1000)
    output = crt.Screen.ReadString('#')  # Ожидаем символ '#' в конце вывода

    # Парсите вывод конфигурации ONT
    match = re.search(r'interface ont (\d+/\d+)', output)
    if match:
        ont_interface = match.group(1)
        port, ont = ont_interface.split('/')
    else:
        ont_interface = None

    match = re.search(r'description "([^"]+)"', output)
    if match:
        description = match.group(1)
        user_name = f'{description.replace("fl_", "kes")}'  # Заменяем "fl_" на "kes"
    else:
        description = None
        user_name = None

    match = re.search(r'serial "([^"]+)"', output)
    if match:
        serial = match.group(1)
        # Заменяем ELTX на 454C5458 для получения pon_serial
        pon_serial = serial.replace("ELTX", "454C5458")
    else:
        serial = None
        pon_serial = None

main()