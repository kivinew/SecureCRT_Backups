import os


file_path = os.getcwd() + "\\log.txt"

# Чтение файла
with open(file_path, "r", encoding='utf-8') as file:  # "r" - открыть для чтения
    # Чтение каждой строки файла
    for line in file:
        # Разделение строки на столбцы (предполагается, что столбцы разделены табуляцией)
        columns = ' '.join(line.split())
        columns = columns.split(' ')
        
        # Проверка на наличие нужного количества столбцов
        if len(columns) >= 2:
            # Вывод нужных столбцов
            # 1 - ONT ID
            # 2 - модель терминала
            # 3 - дистанция до терминала
            # 4 - оптический сигнал
            # 5 - дескрипшн
            ont_id = columns[0].strip()    # ONT ID
            SN = columns[1].strip()   # SN
            description = columns[5].strip()    # Description
            print(f"ONT ID: {ont_id}, SN: {SN}, Description: {description}")
