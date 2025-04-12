# $language = "Python3"
# $interface = "1.0"

import os
import sys
import json
import pyperclip

def main():
    # # Создаем словарь с информацией о путях
    # path_info = {
    #     "python_version": sys.version,
    #     "executable": sys.executable,
    #     "sys_path": sys.path,
    #     "os_environ_path": os.environ.get('PATH', '').split(os.pathsep),
    #     "loaded_modules": list(sys.modules.keys())
    # }
    
    # crt.Dialog.MessageBox(str(path_info))

    result = (f"Python Version: {sys.version}"
        f"Executable: {sys.executable}"
        f"Loaded Modules: {json.dumps(list(sys.modules.keys()), indent=1)}",
        "Python Module Path Information")

    result = str(result)

    result = str(result).split()
    # Выводим информацию в удобном формате
    crt.Dialog.MessageBox(str(result))

    mem_buffer = pyperclip.copy(result)

main()