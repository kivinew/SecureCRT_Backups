# $Language="Python3"
# $Interface="1.0"
"""
Тест интеграции GPON_class с SecureCRT
Запускается внутри SecureCRT через File → Run Script
"""

import re
import sys

# Импортируем класс из GPON_class.py
from GPON_HW.GPON_class import GPON, Ont, inject_crt

def test_injection():
    """Проверка инъекции crt объекта"""
    print("=" * 50)
    print("Тест 1: Инъекция crt объекта")
    print("=" * 50)
    
    try:
        # Передаем глобальный crt в модуль
        inject_crt(crt)
        print("[OK] crt объект передан в GPON_class")
        print(f"     Версия SecureCRT: {crt.Version}")
        return True
    except Exception as e:
        print(f"[ERROR] Ошибка инъекции: {e}")
        return False

def test_ont_parsing():
    """Проверка парсинга ONT ID из буфера"""
    print("\n" + "=" * 50)
    print("Тест 2: Парсинг ONT ID")
    print("=" * 50)
    
    # Тестовые данные
    test_cases = [
        ["0", "1", "0", "1"],
        ["0", "1", "0", "1", "ALCL12345678"],
        ["0", "2", "5", "10"],
    ]
    
    for test_data in test_cases:
        try:
            ont = Ont(test_data)
            print(f"[OK] {test_data} -> {ont.frame}/{ont.slot}/{ont.port}/{ont.ont}")
            if len(test_data) > 4:
                print(f"     SN: {ont.sn}")
        except Exception as e:
            print(f"[ERROR] {test_data} -> {e}")

def test_command_sending():
    """Проверка отправки команды"""
    print("\n" + "=" * 50)
    print("Тест 3: Отправка команды")
    print("=" * 50)
    
    try:
        inject_crt(crt)
        
        # Отправляем простую команду
        crt.Screen.Send("display version\r")
        print("[OK] Команда отправлена")
        
        # Ждем вывод
        output = crt.Screen.ReadString(["#"], 10)
        print(f"[OK] Вывод получен ({len(output)} символов)")
        print(f"     Первые 200 символов: {output[:200]}...")
        
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_pattern_matching():
    """Проверка регулярных выражений"""
    print("\n" + "=" * 50)
    print("Тест 4: Парсинг паттернов")
    print("=" * 50)
    
    # Пример вывода Huawei (заглушка, подставьте реальный)
    test_output = """
    Frame 0 Slot 1 Port 0 Ont 1
    Run state         : online
    Config state      : normal
    Match state       : match
    SN                : ALCL12345678
    Description       : Test ONT
    ONT distance(m)   : 12500
    Last up time      : 2024-01-15 10:30:00
    Last down time    : 2024-01-14 08:00:00
    Last down cause   : LOSt
    ONT Type          : MA5620-24
    """
    
    patterns = {
        "status": r"Run state\s+:\s+(\w+)",
        "serial": r"SN\s+:\s+(\S+)",
        "description": r"Description\s+:\s+(.+)",
        "distance": r"ONT distance\(m\)\s+:\s+(\d+)",
        "ont_model": r"ONT Type\s+:\s+(.+)",
    }
    
    for name, pattern in patterns.items():
        match = re.search(pattern, test_output)
        if match:
            print(f"[OK] {name}: {match.group(1).strip()}")
        else:
            print(f"[WARN] {name}: не найдено")

def test_gpon_class():
    """Полный тест класса GPON"""
    print("\n" + "=" * 50)
    print("Тест 5: Класс GPON (без реальных команд)")
    print("=" * 50)
    
    try:
        inject_crt(crt)
        
        # Создаем тестовый ONT
        ont = Ont(["0", "1", "0", "1", "ALCL12345678"])
        gpon = GPON(ont)
        
        print("[OK] Объекты созданы")
        print(f"     ONT: {ont.frame}/{ont.slot}/{ont.port}/{ont.ont}")
        print(f"     SN: {ont.sn}")
        
        # Проверяем структуру данных
        print("\n     Поля data:")
        for key, value in gpon.data.items():
            print(f"       {key}: {value}")
        
        return True
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Запуск всех тестов"""
    print("\n")
    print("*" * 50)
    print("GPON SecureCRT Integration Test Suite")
    print("*" * 50)
    print(f"SecureCRT Version: {crt.Version}")
    print(f"Python Version: {sys.version}")
    print()
    
    # Запуск тестов
    results = []
    
    results.append(("Injection", test_injection()))
    results.append(("ONT Parsing", test_ont_parsing()))
    results.append(("Command Sending", test_command_sending()))
    results.append(("Pattern Matching", test_pattern_matching()))
    results.append(("GPON Class", test_gpon_class()))
    
    # Итоги
    print("\n" + "=" * 50)
    print("ИТОГИ")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {name}")
    
    print()
    print(f"Всего: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("\n[SUCCESS] Все тесты пройдены!")
        print("Готово для запуска Qt приложения")
    else:
        print("\n[WARNING] Некоторые тесты не пройдены")
        print("Проверьте ошибки выше")
    
    print("\n" + "=" * 50)

if __name__ == "builtins":
    main()
