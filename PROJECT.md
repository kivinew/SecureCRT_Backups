# SecureCRT Backups — PROJECT.md

## Overview

Скрипты для автоматизации работы с сетевым оборудованием через **SecureCRT** (Telnet/SSH). Фокус — **диагностика Huawei GPON** (MA5600/MA5608T/MA5800), также поддерживаются **Eltex GPON, BDCOM, Juniper, Cisco ASR**.

Скрипты на **VBScript** (запуск внутри SecureCRT), **Python** (парсинг, логика, GUI), небольшой слой **PowerShell** (Windows-задачи).

## Directory structure

```
.
├── GPON_HW/                    # Huawei GPON — ядро проекта
│   ├── GPON_class.py           # Ont, GPON, GPONConfig, COMMANDS, PATTERNS
│   ├── GPON_autodiagnostic_test.vbs  # Полная диагностика ONT
│   ├── qtMain_complete.py      # PyQt6 GUI (3 режима)
│   ├── qt_securecrt_bridge.py  # COM-мост SecureCRT
│   ├── test_gpont_integration.py     # Интеграционные тесты
│   ├── GPON_class_old.py       # Референс (старая версия)
│   ├── GPON_autodiagnostic_test_old.vbs  # Референс (старая версия)
│   ├── oui.txt                 # База OUI/MAC вендоров
│   ├── diagnostic_notes.txt    # Ченжлог
│   └── *.vbs                   # VBScript-скрипты Huawei
├── BDCOM/                      # VBScript для BDCOM
├── Juniper/                    # VBScript + Python для Juniper
├── AGENTS.md                   # Инструкции для AI
├── PROJECT.md                  # Этот файл
├── HUAWEI.md                   # Huawei GPON CLI
├── SECURECRT.md                # SecureCRT scripting
├── system-prompt.md            # Поведение AI (русский)
├── CLOUDFLARE_agent_setup_prompt.md  # Cloudflare MCP setup
├── MCP-servers.md              # Справка по MCP-серверам
├── pyproject.toml              # Python-зависимости + настройки
├── pylintrc                    # Lint
├── .gitignore
├── README.md                   # Краткое описание (публичное)
└── LICENSE                     # MIT
```

## Stack

| Технология | Назначение |
|------------|------------|
| **Python 3.12+** | `GPON_class.py`, Qt GUI, парсинг, COM |
| **VBScript (.vbs)** | SecureCRT-автоматизация CLI (.Send, .WaitForString) |
| **PyQt6** | Графический интерфейс диагностики для Huawei GPON |
| **pywin32** | COM-доступ к SecureCRT из внешнего Python |
| **pyperclip** | Буфер обмена (ONT ID, результаты) |
| **PowerShell** | Windows-специфичные задачи |
| **uv / pip** | Управление зависимостями (`pyproject.toml`) |

## Dependencies

```bash
uv sync              # или: pip install -e .
pip install PyQt6 pywin32 pyperclip
```

## Running

| Режим | Команда |
|-------|---------|
| **Qt GUI (внутри SecureCRT)** | File → Run Script → `GPON_HW/qtMain_complete.py` |
| **Qt GUI (COM)** | `uv run python GPON_HW/qtMain_complete.py` (требуется Commercial SecureCRT) |
| **Qt GUI (стенд, без OLT)** | `uv run python GPON_HW/qtMain_complete.py` (внутренний режим) |
| **Полная диагностика ONT** | File → Run Script → `GPON_HW/GPON_autodiagnostic_test.vbs` |
| **Базовая информация ONT** | File → Run Script → `GPON_HW/GPON_class.py` |
| **Интеграционные тесты** | File → Run Script → `GPON_HW/test_gpont_integration.py` |
| **Проверка COM** | File → Run Script → `GPON_HW/test_securecrt_com.vbs` |

## Key modules

| Файл | Роль |
|------|------|
| `GPON_HW/GPON_class.py` | `Ont` (F/S/P адресация), `GPON` (send/parse/diagnose), `GPONConfig` (настройки), словари `COMMANDS`/`PATTERNS` |
| `GPON_HW/GPON_autodiagnostic_test.vbs` | Оркестратор: SN → ont-info → версия → оптика → line-quality → LAN → MAC → ping → буфер обмена |
| `GPON_HW/qtMain_complete.py` | PyQt6 GUI (3 режима: встроенный Python SecureCRT / COM / внутренний) |
| `GPON_HW/qt_securecrt_bridge.py` | `SecureCRTBridge` через `win32com.client.Dispatch("SecureCRT.CRTApplication")` |

## Equipment support

Приоритет: **Huawei GPON (MA560x/MA580x)** → Eltex GPON → BDCOM → Juniper → Cisco ASR.

## Git

`.gitignore` скрывает: `*.json`, `secrets*.json`, `config*.json`, `kivinew.vbs`, `ASR_login.vbs`, `GePON_Login.vbs`.

## License

MIT, Copyright (c) 2023 Ivan Kudryavtsev.
