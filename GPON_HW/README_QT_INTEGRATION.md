# Qt Integration Guide

Инструкция по использованию Qt приложения для диагностики GPON Huawei.

## Файлы проекта

| Файл | Описание |
|------|----------|
| `qtMain_complete.py` | Полноценное GUI приложение (основной файл) |
| `qt_securecrt_bridge.py` | Модуль для COM-автоматизации SecureCRT |
| `test_securecrt_com.vbs` | Скрипт проверки COM-поддержки |
| `test_gpont_integration.py` | Тесты интеграции с SecureCRT |

## Установка зависимостей

```bash
pip install PyQt6 pywin32 pyperclip
```

## Режимы работы

### Режим 1: Встроенный Python в SecureCRT (рекомендуется)

**Преимущества:**
- Прямой доступ к сессии
- Нет COM-ограничений
- Работает с любой лицензией SecureCRT

**Запуск:**
1. Откройте сессию с Huawei OLT в SecureCRT
2. File → Run Script → `GPON_HW/test_gpont_integration.py`
3. Проверьте результаты тестов
4. Запустите `qtMain_complete.py` через SecureCRT Python

**Код для SecureCRT:**
```python
# Внутри SecureCRT Python
import sys
sys.path.append("GPON_HW")
from qtMain_complete import main
main()
```

### Режим 2: COM автоматизация

**Преимущества:**
- Отдельное Qt приложение
- Полный контроль GUI

**Требования:**
- Commercial License SecureCRT
- pywin32 установлен

**Проверка COM:**
1. Запустите `test_securecrt_com.vbs` из SecureCRT
2. Проверьте `com_test_result.txt`
3. Если COM доступен — используйте режим COM

**Запуск:**
```python
# Отдельный Python процесс
from qtMain_complete import main
main()
```

### Режим 3: Внутренний (без SecureCRT)

**Ограничения:**
- Только парсинг и валидация
- Нет реальных команд к OLT

**Использование:**
- Тестирование интерфейса
- Работа с сохраненными отчетами

## Использование

### Базовый сценарий

1. **Запуск приложения**
   ```bash
   python GPON_HW/qtMain_complete.py
   ```

2. **Ввод параметров ONT**
   - Frame: 0
   - Slot: 1
   - Port: 0
   - ONT ID: 1
   - SN: ALCLXXXXXXXX (опционально)

3. **Диагностика**
   - Нажмите "Диагностика"
   - Дождитесь завершения
   - Проверьте вывод

4. **Сохранение**
   - "Сохранить" → TXT файл
   - "Копировать" → буфер обмена

### Через буфер обмена

В `GPON_class.py` используется `pyperclip`:

1. Скопируйте ONT ID в формате `0/1/0/1` или `0/1/0/1 ALCL12345678`
2. Вставьте в соответствующие поля (автоматически при использовании класса)

## Диагностика

### Ошибки подключения

| Ошибка | Решение |
|--------|---------|
| `pywin32 не установлен` | `pip install pywin32` |
| `COM НЕ доступен` | Проверьте лицензию SecureCRT |
| `crt объект не найден` | Запустите внутри SecureCRT |
| `Сессия не найдена` | Убедитесь что сессия активна |

### Проверка работы

```python
# Тест интеграции
python GPON_HW/test_gpont_integration.py
```

## Настройки

### Таймауты

В `GPON_class.py`:
```python
TIMEOUT = 10  # секунд
```

### Пагинация

Скрипт автоматически обрабатывает "Press 'Q'" — отправляет `q`.

## Расширения

### Добавление новых команд

В `GPON_class.py` → `COMMANDS`:
```python
"new_command": "display ont <param> {frame} {slot} {port} {ont}"
```

### Новые паттерны парсинга

В `GPON_class.py` → `PATTERNS`:
```python
"new_field": r"Pattern\s+:\s+(\S+)"
```

## Troubleshooting

### Проблема: GUI не реагирует

**Решение:** Проверьте лог в нижнем окне — там отображаются ошибки.

### Проблема: Таймауты команд

**Решение:** Увеличьте timeout в `execute_command()`:
```python
output = bridge.execute_command(cmd, timeout=30)
```

### Проблема: Неправильная кодировка

**Решение:** Убедитесь что SecureCRT использует UTF-8:
- Setup → Session Options → Terminal → Encoding → UTF-8

## Контакты

Вопросы по интеграции — к команде проекта.
