# $language = "Python3"
# $interface = "1.0"

# =====================================================================
# TODO:
# диагностика по серийнику display ont info by-sn
# проверка версии ПО для моделей терминалов 245 и 245T
# проверка массовости
# при отсутствии линков на LAN портах, запись об ошибках LAN не нужна, но нужно сбросить ошибки
# mac-address ont
# =====================================================================
# для выполнения диагностики и помещения результата в буфер обмена 
# необходимо выделить мышкой значение лицевого счёта или ONT
# например, значение 102147 или 0/ 0/0 2
# =====================================================================

import pyperclip
import re
import traceback

crt.Screen.Synchronous = True

# Строковые константы
COMMANDS = {
    'ont_info': "display ont info {frame} {slot} {port} {ont}",
    'info_by_serial': "display ont info by-sn {serial}",
    'info_by_description': "display ont info by-desc {description}",
    'ont_version': "display ont version {frame} {slot} {port} {ont}",
    'optical_info': "display ont optical-info {port} {ont}",
    'ont_line_quality': "{command} statistics ont-line-quality {port} {ont}",
    'eth_ports': "display ont port state {port} {ont} eth-port all",
    'eth_errors': "{command} statistics ont-eth {port} {ont} ont-port {lan_id}"
}

# Регулярные выражения для извлечения данных
PATTERNS = {
    'ont_by_serial': r"F\/S\/P\s*:\s(\d+)\/(\d+)\/(\d+).*ONT-ID\s*:\s(\d+)",
    'ont_by_desc': r"(\d+)/\s*(\d+)/\s*(\d+)\s+(\d+)",
    'status': r"Run state\s+:\s+(\S+)",
    'serial': r"SN\s*:\s*([\w-]+)\s*\(",
    'description': r"Description\s+:\s((fl_|kes|)?\d{5,6})|(ONT_NO_DESCRIPTION)",
    'uptime': r"Last up time\s*:\s*([\d-]+\s[\d:+-]+)",
    'downtime': r"Last down time\s*:\s*([\d-]+\s[\d:+-]+)",
    'down_cause': r"Last down cause\s+:\s+(dying-gasp|LOS)",
    'distance': r" distance\(m\)\s*:\s*(\d+)",
    'soft_version': r"Main Software Version\s*:\s*(\S*)",
    'ont_model': r"OntProductDescription    : EchoLife (\S+) GPON",
    'ont_model2': r"Equipment-ID\s*:\s*(\w+)",
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

# Инициализация данных
parsed_data = {
    "status": "offline",
    "serial": "нет данных",
    "description": "нет данных",
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
    """Чтение вывода в терминал построчно с таймаутом."""
    output = ""
    while True:
        line = crt.Screen.ReadString("\n", 1)  # Таймаут 1 секунда
        if not line:
            break
        output += line
    return output

def parse_output(output: str, pattern: str, transform=lambda x: x) -> str:
    """Парсинг вывода с использованием регулярных выражений."""
    match = re.search(pattern, output)
    return transform(match.group(1)) if match else None

def parse_by_description(output: str) -> tuple:
    """Извлечение frame, slot, port и ont из вывода команды display ont info by-desc."""
    match = re.search(PATTERNS['ont_by_desc'], output)
    if match:
        return match.groups()
    raise ValueError("Не удалось найти данные ONT по дескрипшену!")

def parse_by_serial(output: str) -> tuple:
    """Извлечение frame, slot, port и ont из вывода команды display ont info by-desc."""
    match = re.search(PATTERNS['ont_by_serial'], output)
    if match:
        return match.groups()
    raise ValueError("Не удалось найти данные ONT по серийному номеру!")

def parse_lan_ports(output: str) -> list:
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

def parse_eth_errors(output: str) -> dict:
    """Парсинг ошибок Ethernet."""
    return {
        key: parse_output(output, pattern, int) or 0
        for key, pattern in PATTERNS['eth_errors'].items()
    }

def main() -> None:
    """Основная логика скрипта."""
    try:
        mem_buffer = pyperclip.paste().strip()
        # Если в буфере нет содержимого, то просто выводим команду "display ont info by-desc "
        if not mem_buffer:
            crt.Screen.Send("display ont info by-desc ")
            return

        # Выход из interface gpon, если нужно
        crt.Screen.Send("\n")
        last_line = crt.Screen.ReadString("#", 1)
        if "(config)" not in last_line.strip():
            crt.Screen.Send("quit\r")

        # Определение frame, slot, port, ont
        if re.match(r'^(kes|fl|fl_)?\d{5,6}$', mem_buffer):  # если в буфере обмена дескрипшен
            output = send_command(COMMANDS['info_by_description'].format(description=mem_buffer))
            frame, slot, port, ont = parse_by_description(output)
        elif re.match(r'^[A-Fa-f0-9]{16}$', mem_buffer):  # Если в буфере обмена серийный номер
            output_ont_by_serial = send_command(COMMANDS['info_by_serial'].format(serial=mem_buffer))
            for key in ['status', 'serial', 'description', 'uptime', 'downtime', 'down_cause']:
                frame, slot, port, ont = parse_by_serial(output_ont_by_serial)
                # parsed_data[key] = parse_output(output_ont_by_serial, PATTERNS[key]) or parsed_data[key]
        else:   # если в буфере адрес ONT или неподходящие данные
            ont_data = mem_buffer.replace('/', ' ').split()
            if len(ont_data) != 4:
                raise ValueError("Ошибка!\nСкопируй серийный номер, дескрипшен (5-6 цифр) или ONT")
            frame, slot, port, ont = ont_data

        # Инициализация буфера обмена
        clipboard_data = f"ONT = {frame}/{slot}/{port} {ont}\n"

        # Сбор базовой информации
        output_ont_info = send_command(COMMANDS['ont_info'].format(frame=frame, slot=slot, port=port, ont=ont))
        for key in ['status', 'serial', 'description', 'uptime', 'downtime', 'down_cause']:
            parsed_data[key] = parse_output(output_ont_info, PATTERNS[key]) or parsed_data[key]

        clipboard_data += (
            f"Description = {parsed_data['description']}\n"
            f"PON SN = {parsed_data['serial']}\n"
        )
        
        # Расшифровка причин недоступности терминала
        if parsed_data['status'] == 'offline':
            if 'нет данных' in parsed_data['down_cause']:
                parsed_data['down_cause'] = 'информация на головной станции не сохранилась.'
            elif 'dying-gasp' in parsed_data['down_cause']:
                parsed_data['down_cause'] += ' – отключение электропитания. Необходима проверка терминала и БП.'
            elif 'LOS' or 'LOSi/LOBi' in parsed_data['down_cause']:
                parsed_data['down_cause'] += ' – отсутствует оптический сигнал. Необходима проверка оптической линии.'
            elif 'LOFi' in parsed_data['down_cause']:
                parsed_data['down_cause'] += ' – низкий/отсутствует уровень оптического сигнала. Необходима проверка оптической линии.'
             
            parsed_data['distance'] = parse_output(output_ont_info, PATTERNS['distance'], int) or parsed_data['distance']
            clipboard_data += (
                f"Растояние от головной станции (м): {parsed_data['distance']}\n"
                f"Время последнего включения: {parsed_data['uptime']}\n"
                f"Время отключения: {parsed_data['downtime']}\n"
                f"Причина отключения — {parsed_data['down_cause']}"
                )
        else:
            parsed_data['distance'] = parse_output(output_ont_info, PATTERNS['distance'], int) or parsed_data['distance']
        
        # Парсинг модели терминала и версии ПО  
        if parsed_data['status'] == 'online':
            output_version = send_command(COMMANDS['ont_version'].format(frame=frame, slot=slot, port=port, ont=ont))
            # Парсинг версии с первым шаблоном
            soft_version = parse_output(output_version, PATTERNS['ont_model'])
            if not soft_version:  # Если версия не найдена, пробуем второй шаблон
                soft_version = parse_output(output_version, PATTERNS['ont_model2'])
            parsed_data['model'] = soft_version or parsed_data['model']
            parsed_data['version'] = parse_output(output_version, PATTERNS['soft_version']) or parsed_data['model']
            
            # Формирование строки базовой информации
            clipboard_data += (
                f"Модель терминала: '{parsed_data['model']}'\n"
                f"Версия ПО терминала: '{parsed_data['version']}'\n"
                f"Растояние от головной станции (м): {parsed_data['distance']}\n"
                f"Время последнего включения: {parsed_data['uptime']}\n"
                )
            
            # Переход в interface gpon
            crt.Screen.Send(f"interface gpon {frame}/{slot}\r")

            # Оптическая информация
            output_optical_info = send_command(COMMANDS['optical_info'].format(port=port, ont=ont))
            parsed_data['ont_rx_power'] = parse_output(output_optical_info, PATTERNS['ont_rx_power'], str) or parsed_data['ont_rx_power']
            parsed_data['olt_rx_power'] = parse_output(output_optical_info, PATTERNS['olt_rx_power'], str) or parsed_data['olt_rx_power']

            clipboard_data += (
                f"ONT Rx (оптический сигнал на терминале)(dBm): {parsed_data['ont_rx_power']}\n"
                f"OLT Rx (сигнал на головной станции)(dBm): {parsed_data['olt_rx_power']}\n"
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
            
            # Пинг до 8.8.8.8
            if '310' not in parsed_data['model']:
                send_command(f"ont remote-ping {port} {ont} ip-address 8.8.8.8\r")
            
            # Покидаем interface gpon
            send_command("quit")

        # Копирование в буфер
        pyperclip.copy(clipboard_data)

    except Exception as e:
        error_line = traceback.extract_tb(e.__traceback__)[-1].lineno
        msg = f"Ошибка в строке №{error_line}: {e}"
        crt.Dialog.MessageBox(msg)

main()