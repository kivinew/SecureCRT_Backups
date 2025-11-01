# $language = "Python3"
# $interface = "1.0"

import os
import sys
import pyperclip
import importlib

#______________________________________________________________
# Обязательная часть для работы подключаемого модуля GPON_class
# Добавляем текущую папку, где находится скрипт
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
# Импортируем модуль GPON
import GPON_class
importlib.reload(GPON_class)
from GPON_class import Ont, inject_crt
# Передаём объект crt в импортированный модуль
inject_crt(crt)
#______________________________________________________________

def main():
    """
    Основной цикл работы SecureCRT-скрипта.
    Читает буфер обмена, создает и удаляет объект Ont.
    """
    if not crt.Session.Connected:
        crt.Dialog.MessageBox("Нет активного соединения!")
        return
    crt.Screen.Synchronous = True
    try:
        memBuffer = pyperclip.paste()
    except pyperclip.PyperclipException as e:
        crt.Dialog.MessageBox(f"Ошибка чтения буфера обмена:\r{e}")
    ontSelect = memBuffer.replace('/', ' ').split()
    ont = Ont(ontSelect)
    try:
        ont.delete_ont()
    except Exception as e:
        crt.Dialog.MessageBox(f"Ошибка при удалении ONT:\r{e}")
main()  
