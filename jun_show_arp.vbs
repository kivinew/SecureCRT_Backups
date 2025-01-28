# $language = "Python3"
# $interface = "1.0"
import time
import pyperclip
import re

# Функция для проверки, является ли строка IP-адресом
def is_ip_address(address):
    if address is None:
        return False
    # Регулярное выражение для проверки формата IP-адреса
    pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    result = re.fullmatch(pattern, address)
    if result:
        # Проверка, чтобы каждый октет был в диапазоне от 0 до 255
        return all(0 <= int(octet) <= 255 for octet in address.split('.'))
    return False

# Функция для проверки, является ли IP-адрес адресом мультикаста (начинается с 239.254)
def is_multicast_address(address):
    return address.startswith('239')

# Функция для проверки, является ли строка MAC-адресом
def is_mac_address(address):
    # Регулярное выражение для проверки формата MAC-адреса
    pattern1 = r'^[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}$'
    pattern2 = r'^[0-9a-fA-F]{4}\.[0-9a-fA-F]{4}\.[0-9a-fA-F]{4}$'
    pattern3 = r'^[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}$'
    return re.fullmatch(pattern1, address) or re.fullmatch(pattern2, address) or re.fullmatch(pattern3, address)

def format_mac_address(address):
    if re.fullmatch(r'^[0-9a-fA-F]{4}\.[0-9a-fA-F]{4}\.[0-9a-fA-F]{4}$', address):
        parts = address.split('.')
        return ':'.join([parts[0][:2], parts[0][2:], parts[1][:2], parts[1][2:], parts[2][:2], parts[2][2:]])
    elif re.fullmatch(r'^[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}$', address):
        parts = address.split('-')
        return ':'.join([parts[0][:2], parts[0][2:], parts[1][:2], parts[1][2:], parts[2][:2], parts[2][2:]])
    return address

def main():
    # Получение содержимого буфера обмена
    content = pyperclip.paste().strip()

    # Проверка, является ли содержимое буфера обмена IP-адресом
    if is_ip_address(content):
        # Если IP-адрес является адресом мультикаста, выполняем специальную команду
        if is_multicast_address(content):
            # Выполнение команды для адреса мультикаста
            crt.Screen.Send(f"show route table inet.1 | match {content}\n")
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