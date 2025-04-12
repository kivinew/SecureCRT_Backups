# $language = "Python3"
# $interface = "1.0"

import time
import pyperclip
import re
import subprocess
import ipaddress

crt.Screen.Synchronous = True   
path: str = 'C:\\Program Files\\VideoLAN\\VLC\\vlc.exe'

# Функция для проверки, является ли строка IP-адресом
def is_ip_address(address):
    if not isinstance(address, str) or not address.strip():
        return False
    try:
        ipaddress.ip_address(address.strip())
        return True
    except ValueError:
        return False

# Функция для проверки, является ли IP-адрес адресом мультикаста
def is_multicast_address(address):
    try:
        ip = ipaddress.ip_address(address)
        return ip.is_multicast
    except ValueError:
        return False  # Невалидный IP-адрес

def is_mac_address(address):
    """
    Проверяет, является ли строка валидным MAC-адресом.
    Поддерживает форматы:
    - 00:11:22:33:44:55
    - 00-11-22-33-44-55
    - 0011.2233.4455
    - 001122334455
    """
    if not isinstance(address, str):
        return False
    # Единое регулярное выражение для всех форматов
    pattern = r'^([0-9a-fA-F]{2}[:.-]?){5}[0-9a-fA-F]{2}$|^([0-9a-fA-F]{4}[.-]){2}[0-9a-fA-F]{4}$'
    if not re.fullmatch(pattern, address):
        return False
    # Дополнительная проверка для смешанных разделителей
    separators = set(c for c in address if not c.isalnum())
    return len(separators) <= 1  # Все разделители должны быть одинаковыми

def format_mac_address(mac):
    """
    Преобразует MAC-адрес в формат с двоеточиями.
    Поддерживает входные форматы:
    - 001a6479e360 → 00:1a:64:79:e3:60
    - 00-1a-64-79-e3-60 → 00:1a:64:79:e3:60
    - 001a.6479.e360 → 00:1a:64:79:e3:60
    """
    # Удаляем все нецифро-буквенные символы
    clean_mac = re.sub(r'[^0-9a-fA-F]', '', mac)
    
    # Проверяем длину (должно быть 12 символов)
    if len(clean_mac) != 12:
        raise ValueError(f"Некорректная длина MAC-адреса: {mac}")
    
    # Разбиваем на пары символов и объединяем через двоеточие
    formatted = ':'.join(clean_mac[i:i+2] for i in range(0, 12, 2))
    return formatted.lower()  # Возвращаем в нижнем регистре

def main():
    # Получение содержимого буфера обмена
    content = pyperclip.paste().strip()

    # Проверка, является ли содержимое буфера обмена IP-адресом
    if is_ip_address(content):
        # Если IP-адрес является адресом мультикаста, выполняем специальную команду
        if is_multicast_address(content):
            # Выполнение команды для адреса мультикаста
            crt.Screen.Send(f"show route table inet.1 | match {content}\n")
            # Список аргументов для запуска VLC в свернутом виде и без отображения заголовка видео
            args = [
                "--qt-start-minimized", # Запуск VLC в свернутом виде
                "--no-video-title-show",
                "--repeat",
                f"udp://@{content}:1234"
                ]
            # Запускаем VLC с передачей аргументов
            process = subprocess.Popen([path] + args)
        else:
            # Выполнение команды show route для обычного IP-адреса
            crt.Screen.Send(f'\nshow route {content}\n')
            # Добавление двух пробелов перед выполнением команды show arp
            crt.Screen.Send(" \n")
            crt.Screen.Send(" \n")
            # Выполнение команды show arp для обычного IP-адреса
            crt.Screen.Send(f"show arp no-resolve | match {content}\n")
    # Проверка, является ли содержимое буфера обмена MAC-адресом
    elif is_mac_address(content):
        # Переформатирование MAC-адреса
        formatted_address = format_mac_address(content)
        # Выполнение команды show arp для MAC-адреса
        crt.Screen.Send(f"show arp no-resolve | match {formatted_address}\n")
    else:
        # Если содержимое буфера обмена не является IP-адресом или MAC-адресом, выполняем команду show configuration
        crt.Screen.Send(f"show configuration | match {content} | display set\n")

main()
