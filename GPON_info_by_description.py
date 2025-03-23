# $language = "Python3"
# $interface = "1.0"

import pyperclip
import re

crt.Screen.Synchronous = True   

def main():
    # Получаем содержимое из буфера обмена
    memBuffer = pyperclip.paste()
    
    # Проверяем, что содержимое соответствует шаблону для номера лицевого счета (пяти- или шестизначное число)
    if re.match(r'^(fl_|kes)?\d{5,6}$', memBuffer):
        crt.Screen.Send(f"display ont info by-desc {memBuffer}\r")
    else:
        # Если номер в памяти не найден, вводим команду без параметра
        crt.Screen.Send("display ont info by-desc ")

main()

