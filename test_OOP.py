# $language = "Python3"
# $interface = "1.0"

import sys
sys.dont_write_bytecode = True  # отключаем .pyc

# Перезагрузка модуля (если он уже загружен)
if 'gpon' in sys.modules:
    del(sys.modules['gpon'])

import gpon

gpon.inject_crt(crt)  # передаём crt в модуль

def main():
    gpon.send_command("display board 0")

main()