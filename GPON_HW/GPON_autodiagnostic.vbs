# $language = "Python"
# $interface = "1.0"

import sys
import os
import importlib

# Добавляем текущую папку, где находится скрипт
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

# Импортируем модуль GPON
import GPON_class
importlib.reload(GPON_class)
from GPON_class import GPON, inject_crt

# Передаём объект crt в импортированный модуль
inject_crt(crt)

def main():
    # Создаём экземпляр диагностики и запускаем
    crt.Screen.Send("scroll 32\n")
    gpon = GPON()
    gpon.run()

main()