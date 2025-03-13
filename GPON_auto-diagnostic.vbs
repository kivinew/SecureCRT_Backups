# $language = "Python3"
# $interface = "1.0"

# TODO:
# пинг 8.8.8.8
# mac-address ont

import pyperclip
import re
import traceback
from typing import Dict, List, Tuple, Optional

crt.Screen.Synchronous = True

# Строковые константы
COMMANDS = {
    'info_by_serial': "display ont info by-sn {serial}",
    'ont_info': "display ont info {frame} {slot} {port} {ont}",
    'ont_version': "display ont version {frame} {slot} {port} {ont}",
    'gpon_iface': "interface gpon {frame}/{slot}",
    'optical_info': "display ont optical-info {port} {ont}",
    'ont_line_quality': "{command} statistics ont-line-quality {port} {ont}",
    'eth_ports': "display ont port state {port} {ont} eth-port all",
    'eth_errors': "{command} statistics ont-eth {port} {ont} ont-port {lan_id}"
}

# Регулярные выражения для извлечения данных
PATTERNS = {
    'ont_info': r"(\d+)/\s*(\d+)/\s*(\d+)\s+(\d+)",
    'status': r"Run state\s+:\s+(\S+)",
    'serial': r"SN\s*:\s*([\w-]+)\s*\(",
    'uptime': r"Last up time\s*:\s*([\d-]+\s[\d:+-]+)",
    'downtime': r"Last down time\s*:\s*([\d-]+\s[\d:+-]+)",
    'down_cause': r"Last down cause\s+:\s+(dying-gasp|LOS)",
    'distance': r"ONT distance\(m\)\s*:\s*(\d+)",
    'ont_version': r"Main Software Version\s*:\s*(\S*)",
    'ont_model': r"OntProductDescription    : EchoLife (\S+) GPON",
    'ont_rx_power': r"Rx optical power\(dBm\)\s*:\s*([\d.-]+)",
    'olt_rx_power': r"OLT Rx ONT optical power\(dBm\)\s*:\s*([\d.-]+)",
    'lan_ports': r"(\d+)\s+(\d+)\s+(GE|FE)\s+(\d+|-)+\s+(full|half|-)\s+(up|down)",
    'upstream_errors': r"Upstream frame BIP error count\s*:\s*(\d+)",
    'downstream_errors': r"Downstream frame BIP error count\s*:\s*(\d+)",
    'eth_errors': {
        'fcs': r"Received FCS error frames\s+:\s+(\d+)",
        'received_bad_bytes': r"Received bad bytes\s+:\s+(\d+)",
        'sent_bad_bytes': r"Sent bad bytes\s+:\s+(\d+)"
    }
}

# Инициализация данных с типизацией
ParsedData = Dict[str, str | int | float | List[dict]]
parsed_data: ParsedData = {
    "status": "offline",
    "serial": "нет данных",
    "model": "нет данных",
    "version": "нет данных",
    "distance": "нет данных",
    "uptime": "нет данных",
    "downtime": "нет данных",
    "down_cause": "нет данных",
    "ont_rx_power": "нет данных",
    "olt_rx_power": "нет данных",
    "upstream_errors": "0",
    "downstream_errors": "0",
    "lan_ports": [],
    "eth_errors": {"fcs": 0, "received_bad_bytes": 0, "sent_bad_bytes": 0}
}

def send_command(command: str) -> str:
    """Выполнение команды и возврат её вывода."""
    crt.Screen.Send(command + "\r")
    if "display ont info" in command and "by-desc" not in command:
        crt.Screen.Send("q")  # Выход из постраничного вывода
    elif "optical-info" in command or "ont-eth" in command:
        crt.Screen.Send(" ")  # Полный вывод
    return read_output()

def read_output() -> str:
    """Чтение вывода терминала построчно с таймаутом."""
    output = ""
    while True:
        line = crt.Screen.ReadString("\n", 1)  # Таймаут 1 секунда
        if not line:
            break
        output += line
    return output

def parse_output(output: str, pattern: str, transform=lambda x: x) -> Optional[str | int | float]:
    """Парсинг вывода с использованием регулярных выражений."""
    match = re.search(pattern, output)
    return transform(match.group(1)) if match else None

def parse_by_desc(output: str) -> Tuple[str, str, str, str]:
    """Извлечение frame, slot, port и ont из вывода команды display ont info by-desc."""
    match = re.search(PATTERNS['ont_info'], output)
    if match:
        return match.groups()
    raise ValueError("Не удалось найти данные ONT по дескрипшену!")

def parse_lan_ports(output: str) -> List[Dict[str, str]]:
    """Парсинг состояния LAN портов."""
    return [
        {
            "lan_id": match.group(2),
            "port_type": match.group(3),
            "speed": match.group(4),
            "duplex": match.group(5),
            "link_state": match.group(6),
        }
        for match in re.finditer(PATTERNS['lan_ports'], output)
    ]

def parse_eth_errors(output: str) -> Dict[str, int]:
    """Парсинг ошибок Ethernet."""
    return {
        key: parse_output(output, pattern, int) or 0
        for key, pattern in PATTERNS['eth_errors'].items()
    }

def main() -> None:
    """Основная логика скрипта."""
    try:
        mem_buffer = pyperclip.paste().strip()
        if not mem_buffer:
            crt.Dialog.MessageBox("Буфер обмена пуст.")
            return

        # Выход из interface gpon, если нужно
        crt.Screen.Send("\n")
        last_line = crt.Screen.ReadString("#", 1)
        if "(config)" not in last_line.strip():
            crt.Screen.Send("quit\r")

        # Определение frame, slot, port, ont
        if re.match(r'^\d+$', mem_buffer):
            output = send_command(f"display ont info by-desc {mem_buffer}")
            frame, slot, port, ont = parse_by_desc(output)
        else:
            ont_data = mem_buffer.replace('/', ' ').split()
            if len(ont_data) != 4:
                raise ValueError("Некорректный формат адреса ONT.")
            frame, slot, port, ont = ont_data

        # Инициализация буфера обмена
        clipboard_data = f"ONT = {frame}/{slot}/{port} {ont}\n"

        # Сбор базовой информации
        output_ont_info = send_command(COMMANDS['ont_info'].format(frame=frame, slot=slot, port=port, ont=ont))
        for key in ['status', 'serial', 'uptime', 'downtime', 'down_cause']:
            parsed_data[key] = parse_output(output_ont_info, PATTERNS[key]) or parsed_data[key]
        parsed_data['distance'] = parse_output(output_ont_info, PATTERNS['distance'], int) or parsed_data['distance']

        output_version = send_command(COMMANDS['ont_version'].format(frame=frame, slot=slot, port=port, ont=ont))
        parsed_data['version'] = parse_output(output_version, PATTERNS['ont_version']) or parsed_data['version']
        parsed_data['model'] = parse_output(output_version, PATTERNS['ont_model']) or parsed_data['model']

        # Переход в interface gpon
        crt.Screen.Send(f"interface gpon {frame}/{slot}\r")

        # Оптическая информация
        output_optical_info = send_command(COMMANDS['optical_info'].format(port=port, ont=ont))
        parsed_data['ont_rx_power'] = parse_output(output_optical_info, PATTERNS['ont_rx_power'], float) or parsed_data['ont_rx_power']
        parsed_data['olt_rx_power'] = parse_output(output_optical_info, PATTERNS['olt_rx_power'], float) or parsed_data['olt_rx_power']

        # Формирование строки базовой информации
        clipboard_data += (
            f"PON SN = {parsed_data['serial']}\n"
            f"Модель терминала: '{parsed_data['model']}'\n"
            f"Версия ПО терминала: '{parsed_data['version']}'\n"
            f"Растояние от головной станции (м): {parsed_data['distance']}\n"
            f"ONT Rx (оптический сигнал на терминале)(dBm): {parsed_data['ont_rx_power']}\n"
            f"OLT Rx (сигнал на головной станции)(dBm): {parsed_data['olt_rx_power']}\n"
            f"Время последнего включения: {parsed_data['uptime']}\n"
        )

        # Ошибки оптики
        output_optical_errors = send_command(COMMANDS['ont_line_quality'].format(command='display', port=port, ont=ont))
        parsed_data['upstream_errors'] = parse_output(output_optical_errors, PATTERNS['upstream_errors'], int) or 0
        parsed_data['downstream_errors'] = parse_output(output_optical_errors, PATTERNS['downstream_errors'], int) or 0
        optic_errors = parsed_data['upstream_errors'] + parsed_data['downstream_errors']
        if optic_errors:
            prefix = "Обнаружено значительное количество ошибок оптики: " if optic_errors > 10000 else "Незначительное количество ошибок оптики: "
            clipboard_data += (
                f"{prefix}"
                f"Upstream: {parsed_data['upstream_errors']}. "
                f"Downstream: {parsed_data['downstream_errors']}.\n"
                "Выполнен сброс счётчиков ошибок.\n"
            )
            send_command(COMMANDS['ont_line_quality'].format(command='clear', port=port, ont=ont))
        else:
            clipboard_data += "Ошибок оптики нет.\n"

        # LAN порты и ошибки Ethernet
        output_lan_ports = send_command(COMMANDS['eth_ports'].format(port=port, ont=ont))
        parsed_data['lan_ports'] = parse_lan_ports(output_lan_ports)
        ethernet_counters = ""
        has_eth_errors = False

        for port_state in parsed_data['lan_ports']:
            if port_state['link_state'] == 'up':
                clipboard_data += (
                    f"LAN{port_state['lan_id']}: Type={port_state['port_type']}, "
                    f"Speed={port_state['speed']} Mbps, Duplex={port_state['duplex']}, "
                    f"Link State={port_state['link_state']}\n"
                )
                output_eth_errors = send_command(COMMANDS['eth_errors'].format(command='display', port=port, ont=ont, lan_id=port_state['lan_id']))
                parsed_data['eth_errors'] = parse_eth_errors(output_eth_errors)
                errors = parsed_data['eth_errors']
                if any(errors.values()):
                    has_eth_errors = True
                    ethernet_counters += (
                        f"Обнаружены ошибки на порту LAN{port_state['lan_id']}: "
                        f"FCS = {errors['fcs']}. "
                        f"Input = {errors['received_bad_bytes']}. "
                        f"Output = {errors['sent_bad_bytes']}.\n"
                    )
                    send_command(COMMANDS['eth_errors'].format(command='clear', port=port, ont=ont, lan_id=port_state['lan_id']))
        
        clipboard_data += ethernet_counters + "Выполнен сброс счётчиков ошибок.\n" if has_eth_errors else "Ошибок портов LAN нет.\n"
        
        # Покидаем interface gpon
        send_command("quit")

        # Копирование в буфер
        pyperclip.copy(clipboard_data)

    except Exception as e:
        error_line = traceback.extract_tb(e.__traceback__)[-1].lineno
        msg = f"Ошибка в строке {error_line}: {e}"
        crt.Dialog.MessageBox(msg)

main()