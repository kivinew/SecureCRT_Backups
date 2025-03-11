# $language = "Python3"
# $interface = "1.0"
import re
import pyperclip
import time

crt.Screen.Synchronous = True

def get_ont_interface(output):
    match = re.search(r'interface ont (\d+/\d+)', output)
    if match:
        return match.group(1).split('/')
    return None, None

def get_description(output):
    match = re.search(r'description "([^"]+)"', output)
    return match.group(1) if match else None

def get_serial(output):
    match = re.search(r'serial "([^"]+)"', output)
    return match.group(1) if match else None

def delete_ont(port, ont):
    crt.Screen.Send('configure terminal\r')
    crt.Screen.Send(f'interface ont {port}/{ont}\r')
    crt.Screen.Send('no description\r')
    crt.Screen.Send('no serial\r')
    crt.Screen.Send('no template\r')
    crt.Screen.Send('exit\r')
    crt.Screen.Send(f'no interface ont {port}/{ont}\r')
    crt.Screen.Send('do commit\r')
    crt.Screen.Send('exit\r')

def delete_ont_from_acs(pon_serial, description):
    crt.Screen.Send('acs\r')
    crt.Screen.WaitForString('(acs)#', 1)
    crt.Screen.Send('ont\r')
    crt.Screen.WaitForString('(acs-ont)#', 1)

    if description == 'ONT_NO_DESCRIPTION':
        crt.Screen.Send(f'show ont {pon_serial}\r')
        crt.Screen.WaitForString('Subscriber', 1)
        ont_output = crt.Screen.ReadString("(acs-ont)#", 1)
        match = re.search(r'\s*=\s*"([^"]+)"', ont_output)
        if match:
            user_name = match.group(1)
            crt.Dialog.MessageBox(f"Значение Subscriber: {user_name}", "Информация")
        else:
            user_name = None
            crt.Dialog.MessageBox("Значение Subscriber не найдено", "Информация")

    crt.Screen.Send(f'delete ont {pon_serial}\r')
    crt.Screen.WaitForString('(acs-ont)#', 1)
    crt.Screen.Send('commit\r')
    crt.Screen.Send('exit\r')
    crt.Screen.WaitForString('(acs)#', 1)
    crt.Screen.Send('exit\r')

def delete_user(user_name):
    if user_name:
        crt.Screen.Send('acs\r')
        crt.Screen.WaitForString('(acs)#', 1)
        crt.Screen.Send('user\r')
        crt.Screen.Send(f'delete user {user_name}\r')
        
        # Ожидаем вывод команды и проверяем на наличие ошибки
        output = crt.Screen.ReadString('(acs-user)#', 1)
        
        if "ERROR: Subscriber" in output and "doesn't exists" in output:
            # Если ошибка, меняем приставку "fl_" на "kes"
            new_user_name = user_name.replace("fl_", "kes")
            crt.Screen.Send(f'delete user {new_user_name}\r')
            output = crt.Screen.ReadString('(acs-user)#', 1)
            
            # Проверяем, успешно ли удалился пользователь с новым именем
            if "ERROR" in output:
                crt.Dialog.MessageBox(f"Не удалось удалить пользователя {new_user_name}", "Ошибка")
                return
        
        crt.Screen.Send('commit\r')
        crt.Screen.Send('exit\r')
        crt.Screen.WaitForString('(acs)#', 1)
        crt.Screen.Send('exit\r')

def main():
    ont_value = pyperclip.paste().strip()
    if not ont_value:
        crt.Dialog.MessageBox("Буфер обмена пуст или содержит некорректные данные", "Ошибка")
        return

    crt.Screen.Send(f'show running-config interface ont {ont_value}\r')
    output = crt.Screen.ReadString('#')  # Ожидаем символ '#' в конце вывода

    port, ont = get_ont_interface(output)
    if not port or not ont:
        crt.Dialog.MessageBox("Не удалось определить интерфейс ONT", "Ошибка")
        return

    description = get_description(output)
    user_name = f'{description.replace("fl_", "kes")}' if description else None

    serial = get_serial(output)
    pon_serial = serial.replace("ELTX", "454C5458") if serial else None

    delete_ont(port, ont)

    if pon_serial:
        delete_ont_from_acs(pon_serial, description)

    delete_user(user_name)

main()