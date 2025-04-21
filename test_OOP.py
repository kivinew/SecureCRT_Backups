# $language = "Python3"
# $interface = "1.0"

import random

import sys
sys.dont_write_bytecode = True  # отключаем .pyc

# Перезагрузка модуля (если он уже загружен)
if 'gpon' in sys.modules:
    del(sys.modules['gpon'])

import gpon
gpon.crt = crt  # Передаём объект crt в модуль

gpon.inject_crt(crt)  # передаём crt в модуль

def main():
    pass
    # gpon.send_command("display board 0")

main()