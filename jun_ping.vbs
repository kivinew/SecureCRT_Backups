# $language = "Python3"
# $interface = "1.0"

import pyperclip
import re

crt.Screen.Synchronous = True

def is_valid_ip(ip):
    # Проверяем, соответствует ли строка формату IPv4 адреса
    pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    return re.match(pattern, ip) is not None

def main():
    memBuffer = pyperclip.paste().strip()  # Удаляем лишние пробелы
    if memBuffer:
        if is_valid_ip(memBuffer):
            sendRequest = "ping " + memBuffer + " record-route" + chr(13)
            crt.Screen.Send(sendRequest)
        else:
            crt.Screen.Send("ping ")

main()