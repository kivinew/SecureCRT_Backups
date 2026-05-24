# SecureCRT Backups — SECURECRT.md

## VBScript template

```vb
#$Language="VBScript"
#$Interface="1.0"
Option Explicit

Const TIMEOUT = 10

Sub Main()
    If Not crt.Session.Connected Then
        crt.Dialog.MessageBox "Нет активной сессии."
        Exit Sub
    End If
    crt.Screen.Synchronous = True
    ' ... logic ...
End Sub
```

### Правила VBScript

- Заголовок `#$Language="VBScript"` / `#$Interface="1.0"` обязателен
- `Option Explicit` — снижает риск ошибок в именах переменных
- `Sub Main()` — стандартная точка входа
- `crt.Screen.Send strCmd & Chr(13)` — отправка команды
- `crt.Screen.WaitForString(strPrompt, nTimeout)` — ожидание prompt
- `crt.Screen.WaitForStrings(Array(">", "#"), nTimeout)` + `MatchIndex` — несколько вариантов
- Всегда учитывать таймауты и неожиданный вывод
- При пустом вводе / отмене — `Exit Sub`
- Не полагаться на TAB-autocomplete, ручные паузы или случайный state CLI
- Отправлять полные команды

### WaitForStrings example

```vb
Dim nIndex
nIndex = crt.Screen.WaitForStrings(Array(">", "#", "---- More ----", "Error"), 10)
Select Case nIndex
    Case 1: ' user mode
    Case 2: ' enable/config mode
    Case 3: crt.Screen.Send " "
    Case 4: Exit Sub
    Case Else: Exit Sub
End Select
```

## Python-in-SecureCRT

```python
#$language = "Python3"
#$interface = "1.0"

import sys
sys.path.append("GPON_HW")
from GPON_class import GPON, Ont, GPONConfig

def main():
    crt.Screen.Synchronous = True
    gpon = GPON(ont, crt=crt)
    gpon.inject_crt(crt)
    # ...

if __name__ == "builtins":
    main()
```

### Правила Python в SecureCRT

- Точка входа: `if __name__ == "builtins"` (не `"__main__"`)
- `crt` — built-in объект только при прямом запуске через File → Run Script
- `GPON.inject_crt(crt)` — передать объект crt в класс
- `GPON.send()` использует `_g_crt.Screen`, `_read_rows()`, `_g_crt.Sleep(100)`

## crt API reference

| API | Описание |
|-----|----------|
| `crt.Screen.Send(str)` | Отправить строку в терминал |
| `crt.Screen.WaitForString(str, timeout)` | Ждать строку; вернуть True/False |
| `crt.Screen.WaitForStrings(arr, timeout)` | Ждать одну из строк; вернуть индекс |
| `crt.Screen.MatchIndex` | Индекс совпавшей строки (после WaitForStrings) |
| `crt.Screen.CurrentRow` | Номер текущей строки (1-based) |
| `crt.Screen.Get(row1, col1, row2, col2)` | Прочитать прямоугольную область экрана |
| `crt.Screen.ReadString(str1, str2)` | Прочитать всё между str1 и str2 |
| `crt.Screen.Synchronous = True` | Блокирующий режим отправки |
| `crt.Session.Connected` | Статус подключения |
| `crt.Dialog.MessageBox(msg)` | Диалоговое окно |
| `crt.Sleep(ms)` | Пауза в миллисекундах |

## COM bridge (внешний процесс)

Требуется **Commercial License SecureCRT**. `pywin32` обязателен.

```python
from win32com.client import Dispatch
app = Dispatch("SecureCRT.CRTApplication")
session = app.OpenSession("Huawei GPON")
```

Проверка: File → Run Script → `GPON_HW/test_securecrt_com.vbs`. Результат в `com_test_result.txt`.

## Clipboard

Все диагностические результаты — через `pyperclip.copy()`. Формат: единый стиль (заголовок, чек-лист, значения).

## Error handling

- `crt.Screen.Synchronous = True` — сериализовать Send
- `WaitForString` с таймаутом — не ждать бесконечно
- `_wait_prompt()` — retry limit 5, проверка `_is_real_prompt()` на `#` в конце
- `send()` — проверка на псевдоотклик (stale `#` от предыдущей команды)
- `MessageBox` для фатальных ошибок (в VBScript) и для пользовательских сценариев

## UTF-8

Session Options → Terminal → Encoding → UTF-8.
