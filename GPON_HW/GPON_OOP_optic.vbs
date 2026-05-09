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
        ontSelect = memBuffer.replace('/', ' ').split()
        if len(ontSelect) < 4 or not all(item.isdigit() for item in ontSelect[:4]):
            raise ValueError("Значение ONT должно быть представлено числами, например: 0/1/2 3")
        ont = Ont(ontSelect)
        ont.get_optic()
    except Exception as e:
        crt.Dialog.MessageBox(f"Ошибка при проверке оптического сигнала:\r{e}")
main()  