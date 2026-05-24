# SecureCRT Backups — HUAWEI.md

## Hardware

- **OLT:** Huawei MA5600 / MA5608T / MA5800
- **ONT:** любой GPON ONT, адресуется как `F/S/P ONT-ID` (frame/slot/port + ont-id)
- **Протокол:** Telnet (через SecureCRT)

## CLI hierarchy

```
<user>             # enable
<enable>           # config
<config>           # interface gpon F/S
<config-gpon>      # display ont info ONT-ID port-ID
<config-gpon>      # quit
<config>           # quit
<enable>
```

Модели MA56xx и MA58xx могут иметь различия в синтаксисе — явно отмечать, если неизвестно.

## ONT addressing

Форматы адреса ONT:

| Формат | Пример |
|--------|--------|
| F/S/P ONT-ID | `0/0/0 0` |
| F S P ONT-ID | `0 0 0 0` |
| По SN | `display ont info by-sn ALCLF12345678` |
| По description | `display ont info by-desc fl_123456` |

В `Ont` класс: парсинг из строки вида `0/0/0 0` или `0 0 0 0`. F/S/P в свойствах `frame`, `slot`, `port`; `ont_id` отдельно. Метод `address` возвращает `"{self.frame}/{self.slot}/{self.port}"`.

## Pagination

```
---- More ( Press 'Q' to break ) ----
```

- `space` — следующая страница
- `q` / `Q` — остановить вывод
- `scroll 32` — отключить пагинацию (оптимально для `ont-info` и `optical-info`; в текущей реализации scroll отправляется через `send()`)

В `GPON.send(cmd, max_more)`:
- `max_more = -1` — scroll all (шлёт пробел до конца)
- `max_more = 0` — первая страница + `q`
- `max_more = N` — N страниц + `q`

## Diagnosis workflow

1. **Ввод**: SN из буфера обмена (или F/S/P ONT-ID)
2. `detect(buffer)` — распознаёт SN (16 hex цифр), адрес (4 токена), или description (1-16 символов)
3. `diagnose()` — полный цикл:
   - `display ont info {ont_id} {port_id}` → состояние, memory, CPU, temperature, SN, description, down cause, uptime
   - `display ont version {ont_id} {port_id}` → версия ПО, bad version check
   - `display ont optical-info {ont_id} {port_id}` → RX, TX, температура, напряжение, bias current
   - `display ont line-quality {ont_id} {port_id}` → FEC, CRC, errored seconds
   - `display ont port state {ont_id} {port_id}` → состояние LAN-портов (1-4)
   - `display mac-address ont {ont_id} {port_id}` → MAC-адреса за ONT
   - Ping от OLT до устройства

## Key commands

| Команда | Режим | Назначение |
|---------|-------|------------|
| `display ont info {oid} {pid}` | interface gpon | Базовая информация ONT |
| `display ont version {oid} {pid}` | interface gpon | Версия ПО ONT |
| `display ont optical-info {oid} {pid}` | interface gpon | Оптические параметры |
| `display ont line-quality {oid} {pid}` | interface gpon | FEC, CRC, ошибки |
| `display ont port state {oid} {pid}` | interface gpon | Статус LAN-портов |
| `display mac-address ont {oid} {pid}` | interface gpon | MAC-адреса |
| `display ont info by-sn {sn}` | interface gpon | Поиск ONT по SN |
| `display ont info by-desc {desc}` | interface gpon | Поиск ONT по description |
| `display current-configuration` | config | Текущая конфигурация |
| `display service-port` | config | Service-port |
| `ping {ip}` | enable | Проверка связи |
| `scroll 32` | enable | Отключить пагинацию |

## Patterns (GPON_class.py PATTERNS dict)

```python
PATTERNS = {
    "run_state":     r"Run state\s+:\s+(\S+)",
    "memory":        r"Memory[^:]*:\s*(<?\d+)%",
    "cpu":           r"CPU usage[^:]*:\s*(<?\d+)%",
    "temperature":   r"Temperature[^:]*:\s+(\d+)",
    "down_cause":    r"Down cause[^:]*:\s+(.+)",
    "last_up_time":  r"Last up time[^:]*:\s+(.+)",
    "last_down_time":r"Last down time[^:]*:\s+(.+)",
    "total_run_time":r"Total run time[^:]*:\s+(.+)",
    "sn":            r"ONT SN\s+:\s+(\S+)",
    "description":   r"Description\s+:\s+(\S+)",
    "rx_power":      r"Received optical power\(dBm\)\s*:\s*(-?\d+\.?\d*)",
    "tx_power":      r"Send optical power\(dBm\)\s*:\s*(-?\d+\.?\d*)",
    "tx_temp":       r"Current temperature\(C\)\s*:\s*(-?\d+\.?\d*)",
    "voltage":       r"Current voltage\(V\)\s*:\s*(-?\d+\.?\d*)",
    "bias":          r"Bias current\(mA\)\s*:\s*(-?\d+\.?\d*)",
    "ont_id":        r"F/S/P\s+ONT-ID\s+:\s+(\S+)\s+(\d+)",
}
```

Пороги (GPONConfig): RX > -8 warning, TX < 0 warning, bias > 30 warning, voltage 3.0-3.6.

## Safe-by-default

1. Всегда сначала `display`/show, потом config-changing команды.
2. Если команда может затронуть абонентов (shutdown port, reset, удаление ONT, service-port) — явно предупредить.
3. Не путать F/S/P, ONT-ID, port-ID, service-port.
4. Не выдумывать CLI-синтаксис; если сомнение — указать допущение.
