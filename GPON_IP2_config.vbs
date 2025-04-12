#$language = "Python3"
#$interface = "1.0"

import time
import pyperclip

crt.Screen.Synchronous = False

# Параметры конфигурации
# Укажи файл ???.xml
config_file = "IP2"

def send_command(command, delay=0.5) -> None:
    """Отправка команды с задержкой"""
    crt.Screen.Send(command + "\r")
    time.sleep(delay)

def wait_for_condition(patterns, timeout=2) -> int:
    """Ожидание одного из условий с таймаутом"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        result = crt.Screen.WaitForStrings(patterns)
        if result > 0:
            return result
        time.sleep(1)
    return 0

def main() -> None:
    try:
        # содержимое буфера обмена помещается в переменную
        mem_buffer = pyperclip.paste().strip()
        # Если в буфере нет содержимого, то просто выводим команду "display ont info by-desc "
        if not mem_buffer:
            raise ValueError("Пустой буфер обмена!")
        mem_buffer = mem_buffer.replace('/', ' ').split()
        if len(mem_buffer) == 4:  # Если это адрес ONT (формат F/S/P ONT)
            frame, slot, port, ont = mem_buffer
        else:
            raise ValueError("Скопируй значение ont!")
        # Отображение информации о версии ONT
        send_command(f"display ont version {frame} {slot} {port} {ont}")
        
        # Переход в режим диагностики и загрузка конфигурации
        send_command("diagnose")
        send_command(f"ont-load info configuration {config_file}.xml ftp 10.2.1.3 huawei ksa5oz6y")
        send_command(f"ont-load select {frame}/{slot} {port} {ont}")
        send_command("ont-load start activemode next-startup")
        
        # Мониторинг процесса загрузки
        loading = True
        while loading:
            send_command(f"display ont-load select {frame}/{slot} {port} {ont}")
            condition = wait_for_condition(["Success", "Fail", "Loading"])
            if condition == 1:  # Success
                loading = False
                send_command("\r")
            elif condition == 2:  # Fail
                send_command("ont-load stop")
                send_command("config")
                loading = False
                raise Exception(f"Сбой конфигурации {config_file}.xml")
            elif condition==0: # таймаут
                continue
            else: # Loading (condition == 3)
                time.sleep(3)
        
        # Завершение загрузки конфигурации
        send_command("ont-load stop")
        send_command("config")
        
        # Проверка связи
        send_command(f"interface gpon {frame}/{slot}")
        send_command(f"ont remote-ping {port} {ont} ip-address 8.8.8.8")
        # Проверка WAN интерфейса для определенных конфигураций
        if config_file in ["all", "IP", "IP2", "inet_tv_wifi_vlan2"]:
            send_command(f"display ont ipconfig {port} {ont}")
            # send_command(" ")
        send_command("quit")
    
    except ValueError as e:
        crt.Dialog.MessageBox(f"Некорректное содержимое буфера!\r{str(e)}")
    except Exception as e:
        crt.Dialog.MessageBox(f"Внимание! {str(e)}")

main()