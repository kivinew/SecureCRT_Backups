# $language = "Python3"
# $interface = "1.0"

import os
import sys
import pyperclip
import importlib

#______________________________________________________________
# Обязательная часть для работы с подключаемым модулем GPON_class
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
    """
    if not crt.Session.Connected:
        crt.Dialog.MessageBox("Нет активного соединения!")
        return
    crt.Screen.Synchronous = True
    try:
        memBuffer = pyperclip.paste()
    except pyperclip.PyperclipException as e:
        crt.Dialog.MessageBox(f"Ошибка чтения буфера обмена:\r{e}")
    ontSelect = memBuffer.replace('/', ' ').split()[:4]
    ont = Ont(ontSelect)
    try:
        ont.set_serial(serial=ontSelect[4])
    except Exception as e:
        crt.Dialog.MessageBox(f"Ошибка при смене серийного номера ONT:\r{e}")
main()  