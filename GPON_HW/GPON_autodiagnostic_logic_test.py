# $language = "Python"
# $interface = "1.0"

# =====================================================================
# для выполнения диагностики и помещения результата в буфер обмена 
# необходимо выделить мышкой значение серийного номера, лицевого счёта 
# или ONT, например, значение "485754430068409E", "102147" или "0/ 0/0 2"
# =====================================================================
#
# TODO:
# проверка массовости
# парсинг результата ping 
# собщение об ошибках LAN портов
# =====================================================================

import os
import re
import sys
import time
import traceback

import pyperclip

from GPON_class import inject_crt, COMMANDS

# # --- обязательная инициализация crt для модуля ont_module ---
inject_crt(crt)
    
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# выкидываем старый модуль из кэша
if "GPON_class" in sys.modules:
    del sys.modules["GPON_class"]

# импортируем сам модуль
from GPON_class import COMMANDS  

crt.Screen.Synchronous = True

# Регулярные выражения
PATTERNS = {
    "ont_by_sn": r"F\/S\/P\s*:\s(\d+)\/(\d+)\/(\d+).*ONT-ID\s*:\s(\d+)",
    "ont_by_desc": r"(\d+)\/\s*(\d+)\/\s*(\d+)\s+(\d+)",
    "status": r"Run state\s+:\s+(\S+)",
    "serial": r"(?i)SN\s+:\s+([\da-f]{16})",
    "description": r"Description\s+:\s(\S+)",
    "uptime": r"Last up time\s*:\s*([\d-]+\s[\d:+-]+)",
    "downtime": r"Last down time\s*:\s*([\d-]+\s[\d:+-]+)",
    "downcause": r"Last down cause\s+:\s+(\S+)",
    "distance": r" distance\(m\)\s*:\s*(\d+)",
    "soft_version": r"Main Software Version\s*:\s*(\S*)",
    "ont_model": r"OntProductDescription\s+: EchoLife (\S+) GPON",
    "ont_model2": r"Equipment-ID\s*:\s*(\w+)",
    "ont_rx_power": r"Rx optical power\(dBm\)\s*:\s*([\d.-]+)",
    "olt_rx_power": r"OLT Rx ONT optical power\(dBm\)\s*:\s*([\d.-]+)",
    "lan_ports": r"(\d+)\s+(\d+)\s+(GE|FE)\s+(\d+|-)+\s+(full|half|-)\s+(up|down)",
    "upstream_errors": r"Upstream frame BIP error count\s*:\s*(\d+)",
    "downstream_errors": r"Downstream frame BIP error count\s*:\s*(\d+)",
    "eth_errors": {
        "fcs": r"Received FCS error frames\s+:\s+(\d+)",
        "received_bad_bytes": r"Received bad bytes\s+:\s+(\d+)",
        "sent_bad_bytes": r"Sent bad bytes\s+:\s+(\d+)",
    },
    "mac_addresses": r"(ETH|WLAN)\s+(\d)+\s+([0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4})",
    "ping_result": r"IP address of ping\s+:\s+\d+\.\d+\.\d+\.\d+\s+Transmit packets\s+:\s+\d+\s+Receive packets\s+:\s+\d+",
}

BAD_VERSIONS = {
    "V1R003C00S108",
    "V1R006C00S130",
    "V1R006C00S205",
    "V1R006C00S201",
    "V1R006C01S201",
}

parsed_data = {
    "status": "offline",
    "serial": "нет данных",
    "description": "нет данных",
    "model": "нет данных",
    "version": "нет данных",
    "distance": "нет данных",
    "uptime": "нет данных",
    "downtime": "нет данных",
    "downcause": "нет данных",
    "ont_rx_power": "нет данных",
    "olt_rx_power": "нет данных",
    "upstream_errors": 0,
    "downstream_errors": 0,
    "lan_ports": [],
    "eth_errors": {"fcs": 0, "received_bad_bytes": 0, "sent_bad_bytes": 0},
    "mac_addresses": "нет данных",
    "ping_result": "нет данных",
    "troubleshooting": "",
}


def send_command(command: str, delay: float = 0.1) -> str:
    """Отправка команды на OLT и возврат полного вывода."""
    crt.Screen.Send(command + "\r \r")
    time.sleep(0.2)

    if "display ont info" in command and "by-desc" not in command:
        crt.Screen.Send("q")
        time.sleep(delay)
    elif "optical-info" in command or "ont-eth" in command:
        crt.Screen.Send(" ")
        time.sleep(delay)

    return read_output()


def read_output() -> str:
    """Чтение вывода до паузы по строкам."""
    output = ""
    while True:
        line = crt.Screen.ReadString("\n", 1)
        if not line:
            break
        output += line
    return output


def parse_output(output: str, pattern: str, transform=lambda x: x):
    """Поиск по regex и опциональное преобразование."""
    match = re.search(pattern, output)
    return transform(match.group(1)) if match else None


def parse_by_description(output: str) -> tuple:
    """Парсит F/S/P/ONT из вывода display ont info by-desc."""
    match = re.search(PATTERNS["ont_by_desc"], output)
    if not match:
        raise ValueError("Не удалось найти данные ONT по дескрипшену!")
    return match.groups()


def parse_by_serial(output: str) -> tuple:
    """Парсит F/S/P/ONT из вывода display ont info by-sn."""
    match = re.search(PATTERNS["ont_by_sn"], output)
    if not match:
        raise ValueError("Не удалось найти данные ONT по серийному номеру!")
    return match.groups()


def parse_lan_ports(output: str) -> list:
    """Возвращает список LAN-портов с их параметрами."""
    return [
        {
            "lan_id": m.group(2),
            "port_type": m.group(3),
            "speed": m.group(4),
            "duplex": m.group(5),
            "link_state": m.group(6),
        }
        for m in re.finditer(PATTERNS["lan_ports"], output)
    ]


def parse_eth_errors(output: str) -> dict:
    """Извлекает счётчики ошибок Ethernet."""
    return {
        key: parse_output(output, pattern, int) or 0
        for key, pattern in PATTERNS["eth_errors"].items()
    }


def parse_mac_addresses(output: str) -> list:
    """Парсит MAC-адреса устройств, подключённых к ONT."""
    return [
        {
            "port_type": m.group(1),
            "port_number": m.group(2),
            "mac": m.group(3),
        }
        for m in re.finditer(PATTERNS["mac_addresses"], output)
    ]


def load_mac_database(file_path: str) -> dict:
    """Загружает базу OUI -> vendor из файла oui.txt."""
    mac_db = {}
    pattern = re.compile(
        r"^([0-9A-Fa-f]{2}[-]?[0-9A-Fa-f]{2}[-]?[0-9A-Fa-f]{2})\s+\(hex\)\s+(.+)"
        r"|^([0-9A-Fa-f]{6})\s+\(base 16\)\s+(.+)"
    )

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            match = pattern.match(line.strip())
            if not match:
                continue
            oui = (match.group(1) or match.group(3)).replace("-", "").upper()
            vendor = (match.group(2) or match.group(4)).strip()
            mac_db[oui] = vendor.split()[0] if vendor else ""
    return mac_db


def get_vendor(mac_address: str, mac_db: dict) -> str:
    """Возвращает вендора по MAC-адресу, если он есть в базе."""
    cleaned_mac = re.sub(r"[^a-fA-F0-9]", "", mac_address).upper()
    return mac_db.get(cleaned_mac[:6], "n/a")


# ==============================
#   Блоки диагностики ONLINE
# ==============================


def diagnose_optics(frame, slot, port, ont, clipboard_data: str) -> str:
    """Диагностика оптики (уровни сигналов + BIP-ошибки)."""
    # Оптическая информация
    output_optical_info = send_command(
        COMMANDS["optical_info"].format(port=port, ont=ont), 1
    )

    ont_rx = parse_output(output_optical_info, PATTERNS["ont_rx_power"], str)
    olt_rx = parse_output(output_optical_info, PATTERNS["olt_rx_power"], str)
    parsed_data["ont_rx_power"] = ont_rx or parsed_data["ont_rx_power"]
    parsed_data["olt_rx_power"] = olt_rx or parsed_data["olt_rx_power"]

    if parsed_data["ont_rx_power"] == "-":
        parsed_data["ont_rx_power"] = "нет данных"
    if parsed_data["olt_rx_power"] == "-":
        parsed_data["olt_rx_power"] = "нет данных"

    clipboard_data += (
        f"ONT Rx (оптический сигнал на терминале)(dBm): {parsed_data['ont_rx_power']}\n"
        f"OLT Rx (сигнал на головной станции)(dBm): {parsed_data['olt_rx_power']}\n"
    )

    # Анализ уровней сигнала
    ont_rx = parsed_data["ont_rx_power"]
    olt_rx = parsed_data["olt_rx_power"]

    if ont_rx != "нет данных" and olt_rx != "нет данных":
        ont_rx_val = float(ont_rx)
        olt_rx_val = float(olt_rx)
        if ont_rx_val < -26.0:
            parsed_data["troubleshooting"] += (
                "Низкий уровень входящего сигнала (ONT RX). "
                "Необходима проверка оптической линии."
            )
        elif olt_rx_val < -32.0:
            parsed_data["troubleshooting"] += (
                "Низкий уровень обратного сигнала (OLT RX). "
                "Необходима проверка оптической линии."
            )
    else:
        parsed_data["troubleshooting"] += (
            "Не удалось определить уровень оптического сигнала! "
            "Необходима диагностика терминала."
        )

    # Ошибки оптики
    output_optical_errors = send_command(
        COMMANDS["ont_line_quality"].format(command="display", port=port, ont=ont)
    )

    parsed_data["upstream_errors"] = (
        parse_output(output_optical_errors, PATTERNS["upstream_errors"], int) or 0
    )
    parsed_data["downstream_errors"] = (
        parse_output(output_optical_errors, PATTERNS["downstream_errors"], int) or 0
    )

    optic_errors = parsed_data["upstream_errors"] + parsed_data["downstream_errors"]

    if optic_errors:
        prefix = (
            "Обнаружено значительное количество ошибок оптики: "
            if optic_errors > 10000
            else "Незначительное количество ошибок оптики: "
        )
        clipboard_data += (
            f"{prefix}"
            f"Upstream: {parsed_data['upstream_errors']}. "
            f"Downstream: {parsed_data['downstream_errors']}.\n"
            "Выполнен сброс счётчиков ошибок.\n"
        )
        send_command(
            COMMANDS["ont_line_quality"].format(
                command="clear", port=port, ont=ont
            )
        )

    return clipboard_data


def diagnose_lan_and_eth(port, ont, clipboard_data: str) -> str:
    """Диагностика LAN-портов и ошибок Ethernet."""
    output_lan_ports = send_command(COMMANDS["eth_ports"].format(port=port, ont=ont))
    parsed_data["lan_ports"] = parse_lan_ports(output_lan_ports)

    ethernet_counters = []
    has_eth_errors = False

    for port_state in parsed_data["lan_ports"]:
        if port_state["link_state"] != "up":
            continue

        lan_id = port_state["lan_id"]
        clipboard_data += (
            f"LAN{lan_id}: Type={port_state['port_type']}, "
            f"Speed={port_state['speed']} Mbps, Duplex={port_state['duplex']}, "
            f"Link State={port_state['link_state']}\n"
        )

        # Перезапуск порта
        send_command(
            COMMANDS["port_switch"].format(
                port=port, ont=ont, lan_id=lan_id, state="off"
            )
        )
        send_command(
            COMMANDS["port_switch"].format(
                port=port, ont=ont, lan_id=lan_id, state="on"
            )
        )

        # Ошибки Ethernet
        output_eth_errors = send_command(
            COMMANDS["eth_errors"].format(
                command="display", port=port, ont=ont, lan_id=lan_id
            )
        )
        parsed_data["eth_errors"] = parse_eth_errors(output_eth_errors)
        errors = parsed_data["eth_errors"]

        if any(errors.values()):
            has_eth_errors = True
            ethernet_counters.append(
                f"Обнаружены ошибки на порту LAN{lan_id}: "
                f"FCS = {errors['fcs']}. "
                f"Input = {errors['received_bad_bytes']}. "
                f"Output = {errors['sent_bad_bytes']}.\n"
            )
            send_command(
                COMMANDS["eth_errors"].format(
                    command="clear", port=port, ont=ont, lan_id=lan_id
                )
            )

    if has_eth_errors:
        clipboard_data += "".join(ethernet_counters) + "Выполнен сброс счётчиков ошибок.\n"
        parsed_data["troubleshooting"] += "Обратить внимание на состояние патчкордов.\n"
    else:
        clipboard_data += "Ошибок портов LAN нет.\n"

    return clipboard_data


def collect_mac_info(frame, slot, port, ont, clipboard_data: str) -> str:
    """Сбор MAC-адресов и вендоров устройств на ONT."""
    mac_output = send_command(f"display mac-address ont {frame}/{slot}/{port} {ont}\r")

    try:
        mac_db_path = os.path.join(script_dir, "oui.txt")
        mac_db = load_mac_database(mac_db_path)
    except Exception as e:
        print(f"Ошибка инициализации: {e}", file=sys.stderr)
        mac_db = {}

    parsed_data["mac_addresses"] = parse_mac_addresses(mac_output)
    seen_macs = set()

    for device in parsed_data["mac_addresses"]:
        mac = device["mac"]
        if mac in seen_macs:
            continue
        seen_macs.add(mac)
        vendor = get_vendor(mac, mac_db)
        port_label = "LAN" if device["port_type"] == "ETH" else device["port_type"]
        clipboard_data += f"{port_label}{device['port_number']} {mac} — {vendor}\n"

    return clipboard_data


def fill_common_ont_fields(output_ont_info: str) -> None:
    """Обновление стандартных полей parsed_data по выводу ont info."""
    for key in ("status", "distance", "serial", "description", "uptime", "downtime", "downcause"):
        parsed_data[key] = parse_output(output_ont_info, PATTERNS[key]) or parsed_data[key]


def handle_offline(clipboard_data: str) -> str:
    """Обработка OFFLINE-состояния ONT."""
    downtime = parsed_data["downtime"]
    downcause = parsed_data["downcause"]

    if not any(ch.isdigit() for ch in downtime):
        parsed_data["downtime"] = "нет данных"
        parsed_data["downcause"] = "нет данных" if "-" in downcause else downcause
        parsed_data["troubleshooting"] += (
            "Интернет не работает. Запись о причине недоступности терминала отсутствует."
        )
    elif "LOFi" in downcause:
        parsed_data["downcause"] += " —  низкий/отсутствует уровень оптического сигнала."
        parsed_data["troubleshooting"] += (
            "Интернет не работает. Необходима проверка оптической линии."
        )
    elif "LOS" in downcause:
        parsed_data["downcause"] += " — отсутствует оптический сигнал."
        parsed_data["troubleshooting"] += (
            "Интернет не работает. Необходима проверка оптической линии."
        )
    elif "dying-gasp" in downcause:
        parsed_data["downcause"] += " — отключение эл.питания."
        parsed_data["troubleshooting"] += (
            "Интернет не работает. Необходима проверка терминала и БП."
        )
    else:
        raise Exception("Сбой диагностики!")

    clipboard_data += (
        f"Отключён: {parsed_data['downtime']}\n"
        f"Время последнего включения: {parsed_data['uptime']}\n"
        f"Растояние от головной станции (м): {parsed_data['distance']}\n"
        f"Причина недоступности — {parsed_data['downcause']}\n"
        f"\n{parsed_data['troubleshooting']}"
    )
    return clipboard_data


def handle_online(frame, slot, port, ont, clipboard_data: str) -> str:
    """Полная диагностика ONLINE-ONT."""
    # Модель и версия
    output_version = send_command(
        COMMANDS["ont_version"].format(frame=frame, slot=slot, port=port, ont=ont)
    )

    model = parse_output(output_version, PATTERNS["ont_model"])
    if not model:
        model = parse_output(output_version, PATTERNS["ont_model2"])

    parsed_data["model"] = model or parsed_data["model"]
    parsed_data["version"] = (
        parse_output(output_version, PATTERNS["soft_version"]) or parsed_data["model"]
    )

    version = parsed_data["version"]
    bad_mark = " !!!" if version in BAD_VERSIONS else ""

    clipboard_data += (
        f"Включён: {parsed_data['uptime']}\n"
        f"Модель терминала: '{parsed_data['model']}'\n"
        f"Версия ПО терминала: '{version}'{bad_mark}\n"
        f"Растояние от головной станции (м): {parsed_data['distance']}\n"
    )

    if version in BAD_VERSIONS:
        parsed_data["troubleshooting"] += "Необходимо обновление ПО терминала. "

    # Переход в interface gpon
    crt.Screen.Send(f"interface gpon {frame}/{slot}\r")

    # Оптика
    clipboard_data = diagnose_optics(frame, slot, port, ont, clipboard_data)

    # LAN и Ethernet
    clipboard_data = diagnose_lan_and_eth(port, ont, clipboard_data)

    # Пинг с ONT
    if "310" not in parsed_data["model"]:
        send_command(f"display ont ipconfig {port} {ont}")
        send_command(f"ont remote-ping {port} {ont} ip-address 1.1.1.1")

    # Выход из interface gpon
    send_command("quit")

    # MAC-адреса и вендоры
    clipboard_data = collect_mac_info(frame, slot, port, ont, clipboard_data)

    # Итог по проблемам
    if not parsed_data["troubleshooting"]:
        clipboard_data += "\nНарушений не выявлено."
    else:
        clipboard_data += f"\n{parsed_data['troubleshooting']}Нарушений оптики нет."

    return clipboard_data


def detect_ont(mem_buffer: str):
    """Определение frame/slot/port/ont по буферу обмена и заполнение parsed_data."""
    mem_buffer = mem_buffer.strip()

    # SN
    if re.fullmatch(r"(?i)(48575443|hwtc)[\da-z]{8}", mem_buffer):
        output_ont_info = send_command(
            COMMANDS["info_by_serial"].format(serial=mem_buffer.upper())
        )
        if output_ont_info:
            frame, slot, port, ont = parse_by_serial(output_ont_info)
            fill_common_ont_fields(output_ont_info)
            return frame, slot, port, ont, output_ont_info

    # F/S/P ONT
    ont_data = mem_buffer.replace("/", " ").split()
    if len(ont_data) == 4:
        frame, slot, port, ont = ont_data
        output_ont_info = send_command(
            COMMANDS["ont_info"].format(frame=frame, slot=slot, port=port, ont=ont)
        )
        fill_common_ont_fields(output_ont_info)
        return frame, slot, port, ont, output_ont_info

    # Description
    if 4 < len(mem_buffer) <= 16:
        output = send_command(
            COMMANDS["info_by_description"].format(description=mem_buffer)
        )
        frame, slot, port, ont = parse_by_description(output)
        output_ont_info = send_command(
            COMMANDS["ont_info"].format(frame=frame, slot=slot, port=port, ont=ont)
        )
        fill_common_ont_fields(output_ont_info)
        return frame, slot, port, ont, output_ont_info

    raise ValueError(
        "Несоответствующее запросу содержимое буфера обмена!\n"
        f"(длина {len(mem_buffer)})\n"
        "Необходимо скопировать серийный номер, "
        "номер лицевого счёта или ONT (пример: 0/1/1 10)"
    )


def main() -> None:
    """Основная функция: определение ONT, диагностика и вывод в буфер обмена."""
    try:
        mem_buffer = pyperclip.paste().strip()

        if not mem_buffer:
            crt.Screen.Send("\rdisplay ont info by-desc ")
            return

        # Выходим из подрежима конфигурации, если нужно
        crt.Screen.Send("\n")
        last_line = crt.Screen.ReadString("#", 1)
        if "(config)" not in last_line.strip():
            crt.Screen.Send("quit\r")

        frame, slot, port, ont, _ = detect_ont(mem_buffer)

        clipboard_data = (
            f"ONT = {frame}/{slot}/{port}/{ont}\n"
            f"Дескрипшн (лицевой счёт) = {parsed_data['description']}\n"
            f"PON SN = {parsed_data['serial']}\n"
            f"Терминал {'доступен' if parsed_data['status'] == 'online' else 'недоступен'}.\n"
        )

        if parsed_data["status"] == "offline":
            clipboard_data = handle_offline(clipboard_data)
        elif parsed_data["status"] == "online":
            clipboard_data = handle_online(frame, slot, port, ont, clipboard_data)

        pyperclip.copy(clipboard_data)

    except Exception as e:
        error_line = traceback.extract_tb(e.__traceback__)[-1].lineno
        msg = f"Ошибка в строке № {error_line}:\n{e}"
        crt.Dialog.MessageBox(msg)
        crt.Screen.Send("display ont info ")


main()