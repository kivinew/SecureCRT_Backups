# $language = "Python3"
# $interface = "1.0"

# GPON Diagnostics v2 — точка входа для SecureCRT
# Использует GPON_class_new.py (Ont, GPON, GPONConfig, GPONDiagnostics)
# Аргументы: -n (no actions), -o (optics only), -r (register only), -d (delete)

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import GPON_class
from GPON_class import inject_crt, GPONDiagnostics

inject_crt(crt)

def main():
    try:
        GPONDiagnostics().run()
    except Exception as e:
        _g_crt.Dialog.MessageBox(f"Критическая ошибка: {e}")

if __name__ == "builtins" or __name__ == "__main__":
    main()