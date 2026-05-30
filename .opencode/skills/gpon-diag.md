## Skill: gpon-diag

**Base directory**: \\king\FS\ОСА\Кудрявцев ИВ\Scripts

Activate this skill when working with the GPON diagnostic project — scripts for automating network equipment diagnostics via SecureCRT.

## When to Use This Skill

- Working with scripts in `GPON_HW/`, `BDCOM/`, `Juniper/` directories
- Writing or modifying SecureCRT `.vbs` scripts (Python-based, `# $language = "Python"`)
- Working with `GPON_class.py` — the core OOP module
- Adding new diagnostic commands for Huawei GPON OLT, Eltex GPON, BDCOM EPON, Juniper
- Parsing CLI output from network equipment
- Loading/configuring ONT via FTP

## Project Structure

### Huawei GPON (`GPON_HW/`) — основное ядро

```
GPON_class.py                     — OOP-ядро: класс GPON (from_serial, from_description, from_fspo, from_buffer)
  ├── get_status_info()           — статус, SN, desc, uptime, downtime, distance
  ├── get_version_info()          — модель + версия ПО
  ├── get_optical_powers()        — ONT Rx / OLT Rx (dBm)
  ├── get_line_quality(clear)     — BIP-ошибки upstream/downstream
  ├── get_lan_ports_status()      — состояние LAN-портов
  ├── get_eth_errors(lan_id, clear) — Ethernet-ошибки (FCS, bad bytes)
  ├── reset_lan_port(lan_id)      — перезапуск порта (off/on)
  ├── get_register_info()         — история регистрации
  ├── get_mac_table()             — MAC-адреса за ONT
  ├── remote_ping(ip)             — ping с ONT
  ├── delete()                    — удаление ONT + service-port
  └── Фабрики: from_serial / from_description / from_fspo / from_buffer

GPON_diagnosis.vbs                — полная авто-диагностика (SN / F/S/P / desc)
GPON_autodiagnostic_test.vbs      — то же + CLI-аргументы (-o, -r, -d, -n)
GPON_HW_full_diag.vbs             — слепая отправка всех команд в терминал
SU_challenge.py                   — генерация SU-пароля Huawei (MD5)
oui.txt                           — база MAC-адресов (IEEE OUI)
GPON_Autofind.vbs                 — прописка ONT из autofind
GPON_optical.vbs                  — просмотр оптики
GPON_register_info.vbs            — информация о регистрации
GPON_remote_ping.vbs              — ping с ONT
GPON_wan_info.vbs                 — WAN-инфо (извлекает IPv4)
GPON_find_MAC.vbs                 — поиск ONT по MAC
GPON_DownUp_speed.vbs             — скорость по service-port
GPON_IP_config.vbs                — загрузка конфига IP+LAN+WANacc через FTP
GPON_IP2_config.vbs               — загрузка конфига IP2
GPON_wanacc_enable.vbs            — включение wan-access http
GPON_wanAccess.vbs                — загрузка WanAccess/WanAccess_HG8245 конфига
GPON_currentConf.vbs              — show running-config ONT
GPON_delete_ont.vbs               — удаление ONT
GPON_OOP_optic.vbs                — оптическая диагностика (через GPON_class)
GPON_OOP_set_serial.vbs           — смена SN (через GPON_class)
GPONconfig.vbs                    — (VBScript) загрузка конфига на ONT
```

### Eltex GPON (корень)
```
GPON_ELTEX_delete.vbs    — удаление ONT + ACS + user
GPON_ELTEX_optic.vbs     — show interface ont laser
GPON_ELTEX_running.vbs   — show running-config interface ont
```

### BDCOM EPON (`BDCOM/`)
```
BDCOM_by_desc.vbs        — поиск по desc
BDCOM_epon_basic_info.vbs / BDCOM_epon_info.vbs
BDCOM_optic.vbs          — оптическая диагностика
BDCOM_show_MAC.vbs       — MAC-адреса
```

### Juniper (`Juniper/`)
```
jun_show_arp.vbs / jun_clear_arp.vbs
jun_show_route.vbs
jun_show_interfaces.vbs
jun_ping.vbs / jun_traceroute_monitor.vbs
jun_conf_match.vbs
jun_multicastVLC.py / jun_multicast_route_table.vbs
jun_file_DELETE.vbs
```

## Core Patterns

### Import boilerplate (для SecureCRT Python-скриптов)
```python
# $language = "Python3"  # или "Python"
# $interface = "1.0"

import os, sys, re, time, pyperclip
import importlib

# Добавить путь к GPON_class
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

import GPON_class
importlib.reload(GPON_class)
from GPON_class import GPON, inject_crt, COMMANDS
inject_crt(crt)
```

### SecureCRT API
```python
crt.Screen.Synchronous = True
crt.Screen.Send(command + "\r")
crt.Screen.ReadString("\n", timeout_sec)     # построчное чтение
crt.Screen.ReadString("#", timeout_sec)       # чтение до промпта
crt.Screen.WaitForString(pattern, timeout)    # ожидание строки
crt.Screen.WaitForStrings([p1, p2, ...])      # ожидание одной из строк
crt.Dialog.MessageBox("text")                 # сообщение
crt.Sleep(milliseconds)
```

### Парсинг вывода (регулярки)
```python
# Шаблон для поиска ONT по SN
r"F\/S\/P\s*:\s(\d+)\/(\d+)\/(\d+).*ONT-ID\s*:\s(\d+)"

# Шаблон для поиска по desc
r"(\d+)\/\s*(\d+)\/\s*(\d+)\s+(\d+)"

# Статус ONT
r"Run state\s+:\s+(\S+)"

# Серийный номер (SN)
r"(?i)SN\s+:\s+([\da-f]{16})"

# Оптический сигнал
r"Rx optical power\(dBm\)\s*:\s*([\d.-]+)"
r"OLT Rx ONT optical power\(dBm\)\s*:\s*([\d.-]+)"

# BIP-ошибки
r"Upstream frame BIP error count\s*:\s*(\d+)"
r"Downstream frame BIP error count\s*:\s*(\d+)"

# State LAN-портов
r"(\d+)\s+(\d+)\s+(GE|FE)\s+(\d+|-)+\s+(full|half|-)\s+(up|down)"

# Ethernet-ошибки
r"Received FCS error frames\s+:\s+(\d+)"
r"Received bad bytes\s+:\s+(\d+)"
r"Sent bad bytes\s+:\s+(\d+)"

# MAC-адреса
r"(ETH|WLAN)\s+(\d)+\s+([0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4})"

# Модель и версия
r"OntProductDescription\s+: EchoLife (\S+) GPON"
r"Equipment-ID\s*:\s*(\w+)"
r"Main Software Version\s*:\s*(\S*)"
```

### Работа с буфером обмена
```python
import pyperclip
memBuffer = pyperclip.paste()                              # чтение
ONT = memBuffer.replace('/', ' ').split()                   # парсинг F/S/P ONT
pyperclip.copy(result_text)                                # запись результата
```

## Диагностические пороги (оптика)
| Параметр | Норма | Проблема |
|---|---|---|
| ONT Rx (dBm) | > -26 | < -26 — низкий сигнал |
| OLT Rx (dBm) | > -32 | < -32 — низкий обратный сигнал |
| BIP-ошибки | < 10000 | > 10000 — значительные |

## Проблемные версии ПО
```python
BAD_VERSIONS = {
    "V1R003C00S108",
    "V1R006C00S130",
    "V1R006C00S205",
    "V1R006C00S201",
    "V1R006C01S201",
}
```

## Huawei OLT CLI команды
```python
COMMANDS = {
    "iface_gpon":         "interface gpon {frame}/{slot}",
    "ont_info":           "display ont info {frame} {slot} {port} {ont}",
    "info_by_serial":     "display ont info by-sn {serial}",
    "info_by_description":"display ont info by-desc {description}",
    "ont_version":        "display ont version {frame} {slot} {port} {ont}",
    "optical_info":       "display ont optical-info {port} {ont}",
    "ont_line_quality":   "{command} statistics ont-line-quality {port} {ont}",
    "eth_ports":          "display ont port state {port} {ont} eth-port all",
    "eth_errors":         "{command} statistics ont-eth {port} {ont} ont-port {lan_id}",
    "port_switch":        "ont port attribute {port} {ont} eth {lan_id} operational-state {state}",
    "remote_ping":        "ont remote-ping {port} {ont} ip-address {ip}",
    "mac_table":          "display mac-address ont {frame}/{slot}/{port} {ont}",
    "quit":               "quit",
}
```

## Типовые задачи

### Добавление новой диагностической команды
1. Добавить команду в `COMMANDS` в `GPON_class.py`
2. Добавить regex-шаблон в `PATTERNS`
3. Создать метод в классе `GPON`
4. Написать отдельный `.vbs`-скрипт (или добавить в `autodiagnostic_test`)

### Создание нового скрипта для SecureCRT
```python
# $language = "Python3"
# $interface = "1.0"

import pyperclip, time

crt.Screen.Synchronous = True

def main():
    memBuffer = pyperclip.paste()
    ONT = memBuffer.replace('/', ' ').split()
    frame, slot, port, ont = ONT

    crt.Screen.Send(f"команда {frame} {slot} {port} {ont}\r")

main()
```

### Загрузка конфигурации на ONT через FTP
```python
send_command("diagnose")
send_command(f"ont-load info configuration {config}.xml ftp {ftp_server} {user} {password}")
send_command(f"ont-load select {frame}/{slot} {port} {ont}")
send_command("ont-load start activemode next-startup")
# ждать Success/Fail/Loading
send_command("ont-load stop")
send_command("config")
```

## Git-репозиторий
- Проект находится в git-репозитории
- Основная ветка: (уточнить)
- Коммиты делать атомарными с русскими описаниями изменений
