#$language = "Python3"
#$interface = "1.0"

import os
import sys
import pyperclip

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

import GPON_class
import importlib
importlib.reload(GPON_class)

from GPON_class import inject_crt, GPON, GPONConfig

inject_crt(crt)

crt.Screen.Synchronous = True


def main():
    buffer = pyperclip.paste().strip()
    if not buffer:
        crt.Screen.Send("\rdisplay ont info by-desc ")
        return

    gpon = GPON()
    ont = gpon.detect(buffer)
    if not ont:
        crt.Dialog.MessageBox("ONT не найдена.")
        return

    diag = GPON(ont)
    result = diag.diagnose()
    pyperclip.copy(result)
    crt.Dialog.MessageBox("Результат диагностики скопирован в буфер обмена.")


main()
