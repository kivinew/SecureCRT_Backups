# SecureCRT Backups — Контекст проекта

## Обзор

Проект содержит скрипты для автоматизации работы с сетевым оборудованием через терминальный эмулятор **SecureCRT**. Основной фокус — диагностика и управление **GPON Huawei** (MA5600/MA5800), а также поддержка оборудования **GPON Eltex**, **BDCOM**, **Juniper** и **Cisco ASR**.

Скрипты реализованы преимущественно на **VBScript** (для запуска из SecureCRT) и **Python** (для сложной логики, парсинга CLI-вывода и GUI-инструментов). Небольшая часть задач покрывается **PowerShell**.

---

## Структура директорий

```
.
├── GPON_HW/                    # Основной модуль Huawei GPON
│   ├── GPON_class.py           # Ядро: классы Ont и GPON, команды, паттерны
│   ├── qtMain_complete.py      # Полноценное Qt GUI для диагностики ONT
│   ├── qt_securecrt_bridge.py  # COM-мост для управления SecureCRT из Python
│   ├── test_gpont_integration.py # Тесты интеграции с SecureCRT
│   ├── README_QT_INTEGRATION.md # Документация по Qt-приложению
│   ├── diagnostic_notes.txt    # Заметки по разработке и запуску
│   └── *.vbs                   # VBScript-скрипты для SecureCRT (Huawei)
├── BDCOM/                      # Скрипты для BDCOM (VBScript)
├── Juniper/                    # Скрипты для Juniper (VBScript + Python)
├── *.vbs                       # VBScript-скрипты общего назначения и других вендоров
├── *.py                        # Python-скрипты верхнего уровня
├── *.ps1                       # PowerShell-скрипты
├── pyproject.toml              # Конфигурация Python-проекта
├── pylintrc                    # Настройки pylint
├── README.md                   # Краткое описание проекта
├── AGENTS.md                   # Инструкции для AI-ассистента (стиль, правила, приоритеты)
└── LICENSE                     # MIT License
```

---

## Технологический стек

| Технология | Назначение |
|------------|------------|
| **VBScript (.vbs)** | Основной язык скриптов SecureCRT; автоматизация CLI-взаимодействия |
| **Python 3.12+** | Парсинг вывода, сложная логика, GUI (PyQt6), COM-автоматизация |
| **PyQt6** | Графический интерфейс диагностического инструмента |
| **pywin32** | COM-взаимодействие с SecureCRT из внешнего Python-процесса |
| **pyperclip** | Работа с буфером обмена (вставка ONT ID / SN) |
| **PowerShell (.ps1)** | Windows-специфичные задачи |

---

## Зависимости и окружение

- **Python:** `>=3.12`
- **Управление зависимостями:** `pyproject.toml` (pip/uv)
- **Основные пакеты:**
  - `PyQt6>=6.11.0`
  - `pywin32>=311`
  - `pyperclip` (упоминается в документации Qt)

Установка зависимостей:

```bash
pip install -e .
# или
pip install PyQt6 pywin32 pyperclip
```

---

## Сборка и запуск

### Python GUI (Qt)

**Режим 1 — Встроенный Python в SecureCRT (рекомендуется):**
1. Открыть сессию с Huawei OLT в SecureCRT.
2. Запустить `GPON_HW/test_gpont_integration.py` через **File → Run Script**.
3. После успешных тестов запустить `GPON_HW/qtMain_complete.py` через SecureCRT Python.

**Режим 2 — COM-автоматизация (внешний процесс):**
1. Требуется Commercial License SecureCRT.
2. Убедиться, что `pywin32` установлен.
3. Запустить:
   ```bash
   python GPON_HW/qtMain_complete.py
   ```

**Режим 3 — Внутренний (без SecureCRT):**
- Только парсинг и тестирование интерфейса.
- Нет реальных команд к OLT.

### VBScript

Скрипты запускаются из SecureCRT:
- **File → Run Script →** выбрать `.vbs` файл.
- Обязательный заголовок:
  ```vb
  #$Language="VBScript"
  #$Interface="1.0"
  ```

### Python-скрипты для SecureCRT

При запуске внутри SecureCRT Python используется специфическая точка входа:

```python
if __name__ == "builtins":
    main()
```

---

## Ключевые файлы и модули

| Файл | Описание |
|------|----------|
| `GPON_HW/GPON_class.py` | Ядро проекта. Классы `Ont` (адресация F/S/P/ONT) и `GPON` (отправка команд, парсинг, диагностика). Содержит словари `COMMANDS` и `PATTERNS` для Huawei CLI. |
| `GPON_HW/qtMain_complete.py` | Полноценное Qt-приложение. Поддерживает три режима работы (встроенный Python, COM, внутренний). Фоновая диагностика через `QThread`. |
| `GPON_HW/qt_securecrt_bridge.py` | COM-бридж (`SecureCRTBridge`). Позволяет внешнему Python-процессу управлять SecureCRT через `win32com.client`. |
| `GPON_HW/test_gpont_integration.py` | Набор тестов для проверки интеграции с SecureCRT перед запуском GUI. |
| `GPON_HW/README_QT_INTEGRATION.md` | Подробная инструкция по установке, режимам работы и расширению Qt-приложения. |
| `GPON_HW/diagnostic_notes.txt` | Заметки разработчика: особенности запуска в SecureCRT, обработка пагинации, история изменений. |
| `AGENTS.md` | Инструкции для AI-ассистента: приоритеты технологий, стиль кодирования, правила именования, обработка ошибок, safe-by-default подход. |
| `pyproject.toml` | Метаданные проекта, зависимости, настройки `pyright`. |
| `pylintrc` | Настройки pylint (`init-hook` для `sys.path`). |

---

## Правила разработки и стиль кодирования

### VBScript (SecureCRT)

- Всегда использовать заголовок:
  ```vb
  #$Language="VBScript"
  #$Interface="1.0"
  ```
- Использовать `Option Explicit` до основного кода.
- Точка входа — `Sub Main()`.
- После `crt.Screen.Send` учитывать перевод строки: `chr(13)` или `vbCr`.
- Использовать явное ожидание: `WaitForString`, `WaitForStrings`, `MatchIndex`.
- Обрабатывать таймауты и пустой ввод (корректный `Exit Sub`).
- Отправлять полные команды; не полагаться на TAB-autocomplete или случайный prompt.
- Имена переменных: `strHost`, `nTimeout`, `objShell`, `bResult`.

### Python

- **Версия:** 3.12+.
- **Точка входа в SecureCRT:** `if __name__ == "builtins":`.
- Классы для повторяющейся логики (см. `GPON_class.py`).
- Регулярные выражения для парсинга CLI-вывода.
- `pyperclip` для работы с буфером обмена.
- Обработка пагинации: паттерн `---- More ( Press 'Q' to break ) ----`.

### PowerShell

- Использовать только для Windows-специфичных задач (файлы, процессы, запуск программ).

### Общие принципы

- **Safe-by-default:** сначала предлагать безопасную проверку (`dry-run`), затем рабочий вариант.
- **Приоритет оборудования:** Huawei GPON → Eltex GPON → BDCOM → Juniper → Cisco ASR.
- **Приоритет технологий:** VBScript → Python → PowerShell.
- Не выдумывать команды CLI, синтаксис оборудования или поведение устройства.
- При недостатке данных задать 1–2 уточняющих вопроса.

---

## Особенности и заметки

- **Пагинация Huawei:** при выводе `More` скрипты отправляют `q` (первая страница), пробел (листать дальше) или обрабатывают до конца в зависимости от параметра `max_more`.
- **Prompt:** метод `_wait_prompt()` в `GPON_class.py` проверяет, что строка действительно заканчивается на `#`, чтобы не спутать prompt с данными.
- **COM-автоматизация:** требует Commercial License SecureCRT; проверяется через `test_securecrt_com.vbs`.
- **Кодировка:** рекомендуется UTF-8 в настройках сессии SecureCRT.
- **Лицензия:** MIT License, Copyright (c) 2023 Ivan Kudryavtsev.

---

## Обновление контекста

При изменении архитектуры, добавлении новых вендоров или смене ключевых зависимостей — актуализировать данный файл.
