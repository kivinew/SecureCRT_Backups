# $language = "Python"
# $interface = "1.0"

import os
import sys
import json
import pyperclip
import re

def main():
    result = (f"Python Version: {sys.version}"
        f"Executable: {sys.executable}"
        f"Loaded Modules: {json.dumps(list(sys.modules.keys()), indent=1)}",
        "Python Module Path Information")

    result = str(result).replace('\\n', ' ').replace('\"', '')

    # Выводим информацию в удобном формате
    crt.Dialog.MessageBox(str(result))
    mem_buffer = pyperclip.copy(result)

main()