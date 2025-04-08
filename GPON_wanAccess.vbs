# $language = "Python3"
# $interface = "1.0"

# Для включения веб доступа на терминал необходимо выделить мышкой значение ONT (например 0/0/7 29)

import pyperclip
import time

crt.Screen.Synchronous = True

# Выбор конфигурации (1 - WanAccess, 0 - WanAccess_HG8245)
access = 1  # Можно изменить на 0 для другой конфигурации

def send_command(command, delay=0.5) -> None:
    """Отправка команды с задержкой"""
    crt.Screen.Send(command + "\r")
    time.sleep(delay)

def main() -> None:
    try:
        # Получаем данные из буфера обмена
        mem_buffer = pyperclip.paste().strip()
        
        # Проверяем, что данные в буфере соответствуют ожидаемому формату
        if not all(c.isdigit() or c in ['/', ' '] for c in mem_buffer):
            raise ValueError ("Неверный формат данных! Ожидается ONT (например: 0/0/7 29)")
            
        # Разбираем данные ONT
        ont_parts = mem_buffer.replace('/', ' ').split()
        if len(ont_parts) != 4:
            crt.Dialog.MessageBox("Неверный формат ONT! Ожидается 4 части (frame/slot/port ont)")
            return
        frame, slot, port, ont = ont_parts
        
        conf = "WanAccess" if access == 1 else "WanAccess_HG8245"
        # Отправка команд конфигурации
        send_command("diagnose")
        send_command(f"ont-load info configuration {conf}.xml ftp 10.2.1.3 huawei ksa5oz6y")
        send_command(f"ont-load select {frame}/{slot} {port} {ont}")
        send_command("ont-load start activemode next-startup", 1)

        # Цикл проверки загрузки конфигурации
        status = True
        timeout = 60  # Максимальное время ожидания в секундах
        start_time = time.time()
        
        while status and (time.time() - start_time) < timeout:
            send_command(f"display ont-load select {frame}/{slot} {port} {ont}")
            
            # Исправленная проверка условий (WaitForStrings вместо WaitForString)
            result = crt.Screen.WaitForStrings(["Success", "Fail", "Loading"], 2)
            
            if result == 1:  # Success
                status = False
                crt.Dialog.MessageBox("Конфигурация успешно загружена!")
            elif result == 2:  # Fail
                status = False
                crt.Dialog.MessageBox("Ошибка загрузки конфигурации!")
            elif result == 0:  # Таймаут
                continue
            else:  # Loading (result == 3)
                time.sleep(2)
        
        if status:  # Если вышли по таймауту
            crt.Dialog.MessageBox("Превышено время ожидания загрузки конфигурации!")
        
        # Завершение конфигурации
        send_command("ont-load stop")
        send_command("config")
        
    except Exception as e:
        crt.Dialog.MessageBox(f"Ошибка: {str(e)}")

main()