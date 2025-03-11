# $language = "Python3"
# $interface = "1.0"

import pyperclip
import re
import traceback

crt.Screen.Synchronous = True

# Строковые константы
COMMANDS = {
    'ont_info': "display ont info {frame} {slot} {port} {ont}",
    'ont_version': "display ont version {frame} {slot} {port} {ont}",
    'gpon_iface': "interface gpon {frame}/{slot}",
    'optical_info': "display ont optical-info {port} {ont}",
    'ont_line_quality': "statistics ont-line-quality {port} {ont}",
    'eth_ports': "display ont port state {port} {ont} eth-port all",
    'eth_errors': "display statistics ont-eth {port} {ont} ont-port {lan_id}"
}

# Словарь для хранения извлеченных данных
parsed_data = { 
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
    "eth_errors": []
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
        'bad_bytes': r"Received bad bytes\s+:\s+(\d+)",
        'sent_bad_bytes': r"Sent bad bytes\s+:\s+(\d+)"
    }
}

def check_prompt(expected_prompt):
    """Функция для проверки текущего приглашения"""
    crt.Screen.Send("\n")
    last_line = crt.Screen.ReadString("#") 
    if expected_prompt in last_line.strip():
        return True
    return False

def send_command(command):
    """Выполнение команды и возврат её вывода."""
    if "statistics" in command:
        crt.Send("display ")
    crt.Screen.Send(command + "\r")
    
    # Если команда требует постраничного вывода (например, "display ont info")
    if ("display ont info" in command) & (not "by-desc" in command):
        crt.Screen.Send("q")  # Отправляем 'q' для выхода из постраничного вывода.
    elif "optical-info" or "ont-eth" in command:
        crt.Screen.Send(' ')  # отправляем " " для полного вывода
    return read_output()

# Функция для чтения вывода
def read_output():
    output = ""
    while True:
        line = crt.Screen.ReadString("\n", 1)
        if not line:
            break
        output += line
    return output

def parse_output(output, pattern, transform=lambda x: x):
    """Функция для парсинга выводов с регулярными выражениями."""
    match = re.search(pattern, output)
    if match:
        return transform(match.group(1))
    return None

def parse_by_desc(output):
    """Парсит вывод команды display ont info by-desc и извлекает frame, slot, port и ont."""
    # Регулярное выражение для поиска строки с frame/slot/port и ont
    pattern = r"(\d+)/\s*(\d+)/\s*(\d+)\s+(\d+)"
    match = re.search(pattern, output)
    
    if match:
        frame = match.group(1)
        slot = match.group(2)
        port = match.group(3)
        ont = match.group(4)
        return frame, slot, port, ont
    else:
        raise ValueError("Не удалось найти данные ONT по дескрипшену!")  

def parse_lan_ports(output):
    """Парсинг состояния LAN портов."""
    lan_ports = []
    for match in re.finditer(PATTERNS['lan_ports'], output):
        lan_ports.append({
            "lan_id": match.group(2),
            "port_type": match.group(3),
            "speed": match.group(4),
            "duplex": match.group(5),
            "link_state": match.group(6),
        })
    return lan_ports

def parse_eth_errors(output):
    """Парсинг ошибок Ethernet."""
    eth_errors = {}
    for key, pattern in PATTERNS['eth_errors'].items():
        eth_errors[key] = parse_output(output, pattern, int) or 0
    return eth_errors

def main():
    memBuffer = pyperclip.paste().strip()
    if not memBuffer:
        crt.Dialog.MessageBox("Буфер обмена пуст.")
        return

    try:
        
        #   Выход из interface gpon
        if not check_prompt("(config)"):
            crt.Screen.Send(f"quit\r")
        
        # Проверка типа введённых данных
        if re.match(r'^\d+$', memBuffer):
            # crt.Screen.Send(f"display ont info by-desc {memBuffer}\r")
            output = send_command(f"display ont info by-desc {memBuffer}")
            frame, slot, port, ont = parse_by_desc(output)
        else:
            ONT = memBuffer.replace('/', ' ').split()
            if len(ONT) != 4:
                raise ValueError("Некорректный формат адреса ONT.")
            frame, slot, port, ont = ONT

        #   Заполняем данные для буфера
        #   указываем адрес ONT
        clipboard_data = f'ONT = "{frame}/{slot}/{port} {ont}\n"'


        # Выполняем команды ont_info и ont_version
        output_ont_info = send_command(COMMANDS['ont_info'].format(frame=frame, slot=slot, port=port, ont=ont))
        parsed_data['status'] = parse_output(output_ont_info, PATTERNS['status']) or parsed_data['status']
        parsed_data['serial'] = parse_output(output_ont_info, PATTERNS['serial']) or parsed_data['serial']
        parsed_data['uptime'] = parse_output(output_ont_info, PATTERNS['uptime']) or parsed_data['uptime']
        parsed_data['downtime'] = parse_output(output_ont_info, PATTERNS['downtime']) or parsed_data['downtime']
        parsed_data['down_cause'] = parse_output(output_ont_info, PATTERNS['down_cause']) or parsed_data['down_cause']
        parsed_data['distance'] = parse_output(output_ont_info, PATTERNS['distance'], int) or parsed_data['distance']

        # Собираем версию и модель
        output_version = send_command(COMMANDS['ont_version'].format(frame=frame, slot=slot, port=port, ont=ont))
        parsed_data['version'] = parse_output(output_version, PATTERNS['ont_version']) or parsed_data['version']
        parsed_data['model'] = parse_output(output_version, PATTERNS['ont_model']) or parsed_data['model']

        #   Переходим в interface gpon
        crt.Screen.Send(f"interface gpon {frame}/{slot}\r")

        #   Парсинг уровней оптического сигнала
        output_optical_info = send_command(COMMANDS['optical_info'].format(port=port, ont=ont))
        parsed_data['ont_rx_power'] = parse_output(output_optical_info, PATTERNS['ont_rx_power'], float) or parsed_data['ont_rx_power']
        parsed_data['olt_rx_power'] = parse_output(output_optical_info, PATTERNS['olt_rx_power'], float) or parsed_data['olt_rx_power']

        #   Формируем строку для буфера обмена
        clipboard_data += (
            f"PON SN = {parsed_data['serial']}\n"
            f"Модель терминала: '{parsed_data['model']}'\n"
            f"Версия ПО терминала: '{parsed_data['version']}'\n"
            f"Растояние от головной станции (м): {parsed_data['distance']}\n"
            f"ONT Rx (оптический сигнал на терминале)(dBm): {parsed_data['ont_rx_power']}\n"
            f"OLT Rx (сигнал на головной станции)(dBm): {parsed_data['olt_rx_power']}\n"
            f"Время последнего включения: {parsed_data['uptime']}\n"
        )

        #   Парисинг ошибок оптики
        output_optical_errors = send_command(COMMANDS['ont_line_quality'].format(port=port, ont=ont))
        parsed_data['upstream_errors'] = parse_output(output_optical_errors, PATTERNS['upstream_errors'], int) or parsed_data['upstream_errors']
        parsed_data['downstream_errors'] = parse_output(output_optical_errors, PATTERNS['downstream_errors'], int) or parsed_data['downstream_errors']
        
        #   Парсинг LAN портов
        output_lan_ports = send_command(COMMANDS['eth_ports'].format(port=port, ont=ont))
        parsed_data['lan_ports'] = parse_lan_ports(output_lan_ports)
        for port_state in parsed_data.get("lan_ports", []):
            if port_state['link_state'] == 'up':  # Проверяем состояние порта
                # прибавляю к буферу состояние активных LAN портов
                clipboard_data += (f"LAN{port_state['lan_id']}: Type= {port_state['port_type']}, Speed={port_state['speed']} Mbps, "
                f"Duplex={port_state['duplex']}, Link State={port_state['link_state']}\n")

                #   Обработка ошибок Ethernet
                output_eth_errors = send_command(COMMANDS['eth_errors'].format(port=port, ont=ont, lan_id=port_state['lan_id']))
                parsed_data['eth_errors'] = parse_eth_errors(output_eth_errors)

        crt.Dialog.MessageBox(str(parsed_data['eth_errors']))


        #   Добавляем ошибки оптики только если значение не равно нулю
        errors = int(parsed_data['upstream_errors']) + int(parsed_data['downstream_errors'])
        if errors != 0:
            if errors > 10000:
                clipboard_data += "Обнаружено значительное количество ошибок оптики: "
            else:
                clipboard_data += "Незначительное количество ошибок оптики: "
            clipboard_data += (
                f"Upstream: {parsed_data['upstream_errors']}. "
                f"Downstream: {parsed_data['downstream_errors']}."
                "\nВыполнен сброс счётчиков ошибок.\n"
            )
            #   сбрасываю ошибки оптики
            crt.Screen.Send(f"clear {ontLineQuality} {port} {ont}\r")
        else:
            clipboard_data += "Ошибок оптики нет.\n"
        
        # Формируем строку для буфера обмена
        pyperclip.copy(clipboard_data)

    except ValueError as e:
        error_line = traceback.extract_tb(e.__traceback__)[-1].lineno
        crt.Dialog.MessageBox(f"Ошибка в строке {error_line}: {e}")
    except Exception as e:
        error_line = traceback.extract_tb(e.__traceback__)[-1].lineno
        crt.Dialog.MessageBox(f"Неизвестная ошибка в строке {error_line}: {e}")

main()