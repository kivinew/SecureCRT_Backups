# $language = "Python"
# $interface = "1.0"

# отдельный запускаемый модуль диагностики нужен для того,
# чтобы обойти ограничение на перезагрузку запущенного модуля

import os
import sys
import importlib
#______________________________________________________________
# Обязательная часть для работы с подключаемым модулем GPON_class
# Добавляем текущую папку, где находится скрипт
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
# Импортируем модуль GPON
import GPON_class
importlib.reload(GPON_class)
from GPON_class import inject_crt
# Передаём объект crt в импортированный модуль
inject_crt(crt)
#______________________________________________________________

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Перезагрузка рабочего модуля
if "GPON_autodiagnostic_logic_test" in sys.modules:
    del sys.modules["GPON_autodiagnostic_logic_test"]

import GPON_autodiagnostic_logic_test

GPON_autodiagnostic_logic_test.run(crt)   # передаём crt, если нужно