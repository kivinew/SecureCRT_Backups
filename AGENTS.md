# SecureCRT Backups — AGENTS.md

## English — AI Agent Instructions

### Stack
- **Python 3.12+** with uv (`uv.lock`) — deps in `pyproject.toml` (PyQt6, pywin32, pyperclip)
- **VBScript** — SecureCRT scripts; header `#$Language="VBScript"` / `#$interface="1.0"`
- **Python inside SecureCRT** — header `#$language = "Python3"`; entry point `if __name__ == "builtins":`
- **lint**: `pylint` (rc: `pylintrc`), pyright (extraPaths: `.venv/Lib/site-packages`)

### Run
| What | Command |
|------|---------|
| Install deps | `uv sync` or `pip install -e .` |
| Qt GUI (standalone) | `uv run python GPON_HW/qtMain_complete.py` |
| VBScript/Python (SecureCRT) | File → Run Script → select file |
| Integration test | File → Run Script → `GPON_HW/test_gpont_integration.py` |
| Diagnostic script | File → Run Script → `GPON_HW/GPON_autodiagnostic_test.vbs` |
| Basic ONT info (direct) | File → Run Script → `GPON_HW/GPON_class.py` |

### Key files
| File | Role |
|------|------|
| `GPON_HW/GPON_class.py` | Core: `Ont` (F/S/P addressing), `GPON` (send/parse/diagnose), `GPONConfig` (settings), `COMMANDS`/`PATTERNS` dicts |
| `GPON_HW/GPON_autodiagnostic_test.vbs` | Full diagnostic orchestration |
| `GPON_HW/qtMain_complete.py` | PyQt6 GUI (3 modes: built-in, COM, standalone) |
| `GPON_HW/qt_securecrt_bridge.py` | COM bridge (requires SecureCRT Commercial License) |
| `PROJECT.md` | General project info |
| `HUAWEI.md` | Huawei GPON CLI details |
| `SECURECRT.md` | SecureCRT scripting rules |

### Architecture
- **SecureCRT** provides `crt.Screen` (Send, WaitForString/WaitForStrings, CurrentRow, Get, ReadString)
- **`inject_crt(obj)`** — injects SecureCRT `crt` into `GPON_class.py` from external scripts
- **`GPONConfig`** — tunable parameters (ping IP, thresholds, bad versions, scroll lines, OUI db path). Pass to `GPON(ont, config=GPONConfig(ping_ip="..."))`
- **`Ont`** — parses `F/S/P ONT-ID` from clipboard (`pyperclip.paste()`) or constructor args
- **`GPON.send(cmd, max_more)`** — sends command, handles pagination (`-1` = scroll all, `0` = first page + q, `N` = N pages then q)
- **`GPON.detect(buffer)`** — recognizes SN (16 hex), `F/S/P ONT-ID` (4 tokens), or description (1-16 chars)
- **`GPON.diagnose()`** — full cycle: ont-info → version → optics → line quality → LAN ports → MAC addresses → ping
- **COM mode**: requires Commercial SecureCRT; verify via `GPON_HW/test_securecrt_com.vbs`

### Patterns
- **ONT addressing**: `0/0/0 0` (frame/slot/port ont-id) or `0 0 0 0`
- **Pagination**: `---- More ( Press 'Q' to break ) ----` — `send()` handles this; always send `q` or space
- **Prompt**: line ending with `#` (`_wait_prompt()` + `_is_real_prompt()` verify this)
- **Cloneable entry for securecrt and standalone**: `if __name__ == "builtins":` vs `if __name__ == "__main__":`
- **Clipboard**: all results go to clipboard via `pyperclip.copy()` — consistent formatting required
- **VBScript template**:
  ```vb
  #$Language="VBScript"
  #$Interface="1.0"
  Option Explicit
  Sub Main()
      crt.Screen.Send "display version" & Chr(13)
  End Sub
  ```

### Equipment priority
1. Huawei GPON (MA5600/MA5608T) → 2. Eltex GPON → 3. BDCOM → 4. Juniper → 5. Cisco ASR

### Key conventions
- Russian language for agent responses (see `system-prompt.md`)
- VBScript for SecureCRT automation; Python for parsing/logic/GUI; PowerShell for Windows-only tasks
- Safe-by-default: `display`/show before config-changing commands; warn before irreversible actions
- Never invent CLI syntax or device behavior — state assumptions explicitly
- Read existing instruction files before generating code: `AGENTS.md`, `HUAWEI.md`, `SECURECRT.md`, `PROJECT.md`
- `.gitignore` sensitive: `*.json`, `secrets*.json`, `config*.json`, `kivinew.vbs`, `ASR_login.vbs`, `GePON_Login.vbs`



## Русский — Инструкции для AI-ассистента

### Стек
- **Python 3.12+** с uv (`uv.lock`) — зависимости в `pyproject.toml` (PyQt6, pywin32, pyperclip)
- **VBScript** — скрипты SecureCRT; заголовок `#$Language="VBScript"` / `#$interface="1.0"`
- **Python внутри SecureCRT** — заголовок `#$language = "Python3"`; точка входа `if __name__ == "builtins":`
- **Линтеры**: `pylint` (rc: `pylintrc`), pyright (extraPaths: `.venv/Lib/site-packages`)

### Запуск
| Действие | Команда |
|----------|---------|
| Установка зависимостей | `uv sync` или `pip install -e .` |
| Qt GUI (отдельно) | `uv run python GPON_HW/qtMain_complete.py` |
| VBScript/Python (SecureCRT) | File → Run Script → выбрать файл |
| Интеграционный тест | File → Run Script → `GPON_HW/test_gpont_integration.py` |
| Полная диагностика | File → Run Script → `GPON_HW/GPON_autodiagnostic_test.vbs` |
| Базовая информация ONT | File → Run Script → `GPON_HW/GPON_class.py` |

### Основные файлы
| Файл | Роль |
|------|------|
| `GPON_HW/GPON_class.py` | Ядро: `Ont` (адресация F/S/P), `GPON` (send/parse/diagnose), `GPONConfig` (настройки), словари `COMMANDS`/`PATTERNS` |
| `GPON_HW/GPON_autodiagnostic_test.vbs` | Оркестратор полной диагностики |
| `GPON_HW/qtMain_complete.py` | PyQt6 GUI (3 режима: встроенный, COM, отдельный) |
| `GPON_HW/qt_securecrt_bridge.py` | COM-мост (требуется Commercial License SecureCRT) |
| `PROJECT.md` | Общая информация о проекте |
| `HUAWEI.md` | CLI-команды Huawei GPON |
| `SECURECRT.md` | Правила написания скриптов SecureCRT |

### Архитектура
- **SecureCRT** предоставляет `crt.Screen` (Send, WaitForString/WaitForStrings, CurrentRow, Get, ReadString)
- **`inject_crt(obj)`** — передаёт объект SecureCRT `crt` в `GPON_class.py` из внешних скриптов
- **`GPONConfig`** — настраиваемые параметры (ping IP, пороги, bad versions, scroll, OUI db). Передаётся в `GPON(ont, config=GPONConfig(ping_ip="..."))`
- **`Ont`** — парсит `F/S/P ONT-ID` из буфера обмена (`pyperclip.paste()`) или аргументов конструктора
- **`GPON.send(cmd, max_more)`** — отправка команды с обработкой пагинации (`-1` = всё, `0` = первая стр + q, `N` = N стр)
- **`GPON.detect(buffer)`** — распознаёт SN (16 hex), `F/S/P ONT-ID` (4 токена), или описание (1-16 символов)
- **`GPON.diagnose()`** — полный цикл: ont-info → version → оптика → line quality → LAN порты → MAC → ping
- **COM-режим**: требуется Commercial SecureCRT; проверка `GPON_HW/test_securecrt_com.vbs`

### Паттерны
- **Адресация ONT**: `0/0/0 0` (frame/slot/port ont-id) или `0 0 0 0`
- **Пагинация**: `---- More ( Press 'Q' to break ) ----` — `send()` обрабатывает автоматически
- **Промпт**: строка, заканчивающаяся на `#` (`_wait_prompt()` + `_is_real_prompt()` верифицируют)
- **Точка входа для SecureCRT**: `if __name__ == "builtins":` (не `"__main__"`)
- **Буфер обмена**: все результаты через `pyperclip.copy()` — единый формат обязателен
- **Шаблон VBScript**:
  ```vb
  #$Language="VBScript"
  #$Interface="1.0"
  Option Explicit
  Sub Main()
      crt.Screen.Send "display version" & Chr(13)
  End Sub
  ```

### Приоритет оборудования
1. Huawei GPON (MA5600/MA5608T) → 2. Eltex GPON → 3. BDCOM → 4. Juniper → 5. Cisco ASR

### Ключевые правила
- Язык ответа ассистента — русский (см. `system-prompt.md`)
- VBScript для SecureCRT; Python для парсинга/логики/GUI; PowerShell только для Windows-задач
- Safe-by-default: сначала `display`/show, потом изменяющие команды; предупреждать о необратимых действиях
- Не выдумывать синтаксис CLI или поведение устройства — явно указывать допущения
- Перед генерацией кода прочитать файлы: `AGENTS.md`, `HUAWEI.md`, `SECURECRT.md`, `PROJECT.md`
- `.gitignore` чувствительные файлы: `*.json`, `secrets*.json`, `config*.json`, `kivinew.vbs`, `ASR_login.vbs`, `GePON_Login.vbs`
