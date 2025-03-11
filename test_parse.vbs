# $language = "Python3"
# $interface = "1.0"

import pyperclip
import re

crt.Screen.Synchronous = True

# Строковые константы
pressQ = "( Press 'Q' to break ) ----"
macAddress = "mac-address ont "
ifaceGpon = "interface gpon "
ontInfo = "ont info "
ontVersion = "ont version "
wanInfo = "ont wan-info "
opticalInfo = "ont optical-info "
registerInfo = "ont register-info "
ethPorts = "ont port state "
ontLineQuality = "statistics ont-line-quality "

# Словарь для хранения извлеченных данных
parsed_data = {
    "status": "offline",
    "version": "нет данных",
    "distance": "нет данных",
    "ont_rx_power": "нет данных",
    "olt_rx_power": "нет данных",
    "uptime": "нет данных",
    "downtime": "нет данных",
    "down_cause": "нет данных",
    "lan_port": "нет данных",
    "optic_errors": "нет данных"
}

# Функция чтения вывода
def read_output():
    output = ""
    while True:
        line = crt.Screen.ReadString("\n", 1)  # Читаем строку
        if not line:
            break
        output += line
    return output

# парсим ont version
def parse_version_info(output):
    ont_version_match = re.search(r"Main Software Version\s*:\s*(\S*)", output)
    if ont_version_match:
        parsed_data["version"] = ont_version_match.group(1)

# парсим состояние терминала и расстояние до OLT
def parse_ont_info(output):
    # состояние терминала
    state = re.search(r"Run state\s+:\s+(\S+)", output)
    parsed_data["status"] = state.group(1)
    # время последнего включения
    ont_uptime_match = re.search(r"Last up time\s*:\s*([\d-]+\s[\d:+-]+)", output)
    if ont_uptime_match:
        parsed_data["uptime"] = ont_uptime_match.group(1)
    # время последнего выключения
    ont_downtime_match = re.search(r"Last down time\s*:\s*([\d-]+\s[\d:+-]+)", output)
    if ont_downtime_match:
        parsed_data["downtime"] = ont_downtime_match.group(1)
    # причина последней недоступности
    down_cause_match = re.search(r"Last down cause\s+:\s+(dying-gasp|LOS)", output)
    if down_cause_match:
        parsed_data["down_cause"] = down_cause_match.group(1)
    # значения расстояния до OLT
    ont_distance_match = re.search(r"ONT distance\(m\)\s*:\s*(\d+)", output)
    if ont_distance_match:
        parsed_data["distance"] = ont_distance_match.group(1)

# Парсинг значений оптики
def parse_optical_info(output):
    # Парсим Rx optical power
    rx_power_match = re.search(r"Rx optical power\(dBm\)\s*:\s*([\d.-]+)", output)
    if rx_power_match:
        parsed_data["ont_rx_power"] = rx_power_match.group(1)
    # Парсим OLT Rx ONT optical power
    olt_rx_power_match = re.search(r"OLT Rx ONT optical power\(dBm\)\s*:\s*([\d.-]+)", output)
    if olt_rx_power_match:
        parsed_data["olt_rx_power"] = olt_rx_power_match.group(1)

# парсим логи register-info
def parse_log_info(output):
    pass
    # ont_uptime_match = re.search(r"UpTime\s*:\s*([\d-]+\s[\d:+-]+)", output)
    # if ont_uptime_match:
    #     parsed_data["uptime"] = ont_uptime_match.group(1)
    # ont_downtime_match = re.search(r"DownTime\s*:\s*([\d-]+\s[\d:+-]+)", output)
    # if ont_downtime_match:
    #     parsed_data["downtime"] = ont_downtime_match.group(1)

# Парсим состояние портов
def parse_lan_ports(output):
    lan_port_matches = re.finditer(r"(\d+)\s+(\d+)\s+(GE|FE)\s+(\d+|-)+\s+(full|half|-)\s+(up|down)", output)
    lan_port = []
    for match in lan_port_matches:
        lan_port.append({
            "port_id": match.group(2),
            "port_type": match.group(3),
            "speed": match.group(4),
            "duplex": match.group(5),
            "link_state": match.group(6)
        })
    parsed_data["lan_port"] = lan_port

# Парсинг ошибок оптики
def parse_optic_errors(output):
    # Парсим ошибки оптики
    optic_errors_match = re.search(r"Downstream frame BIP error count \s*:\s(\d*)", output)
    if optic_errors_match:
        parsed_data["optic_errors"] = optic_errors_match.group(1)

def main():
    # Поместить выделенный фрагмент в буфер
    memBuffer = pyperclip.paste()

    # Разбить содержимое буфера в список
    ONT = memBuffer.replace('/', ' ').split()

    frame = ONT[0]
    slot  = ONT[1]
    port  = ONT[2]
    ont   = ONT[3]

    if memBuffer:
        # Выводим и парсим информацию об ONT:
        #   Проверяем доступен ли терминал и расстояние до гол.станции
        crt.Screen.Send(f"display {ontInfo} {frame} {slot} {port} {ont}\r")
        output_ont_info = read_output()
        crt.Screen.Send("q")
        parse_ont_info(output_ont_info)

        #   Входим в interface gpon
        crt.Screen.Send(f"{ifaceGpon} {frame}/{slot}\r")

        if parsed_data['status'] == 'online':
            # Проверяем версию ПО терминала
            crt.Screen.Send(f"display {ontVersion} {frame} {slot} {port} {ont}\r")
            output_version = read_output()
            parse_version_info(output_version)

            #   Состояние LAN портов терминала
            crt.Screen.Send(f"display {ethPorts} {port} {ont} eth-port all\r")
            output_lan_ports = read_output()
            parse_lan_ports(output_lan_ports)


            #   Проверяем пинг до 8.8.8.8
            crt.Screen.Send(f"ont remote-ping {port} {ont} ip-address 8.8.8.8\r")

            #   Уровень оптического сигнала
            crt.Screen.Send(f"display {opticalInfo} {port} {ont}\r")
            crt.Screen.Send(" ")
            output_optic = read_output()
            parse_optical_info(output_optic)

        #   Логи
        crt.Screen.Send(f"display {registerInfo} {port} {ont}\r ")
        crt.Screen.Send(" ")
        crt.Screen.Send(" ")
        output_log_info = read_output()
        parse_log_info(output_log_info)


        #   Ошибки оптики
        crt.Screen.Send(f"display {ontLineQuality} {port} {ont}\r")
        crt.Screen.Send(f"clear {ontLineQuality} {port} {ont}\r")
        output_optic_errors = read_output()
        parse_optic_errors(output_optic_errors)

        #   Выход из interface gpon
        crt.Screen.Send("quit\r")

        if parsed_data['status'] == 'online':
            # Формируем строку для буфера обмена
            clipboard_data = (
                f"Версия ПО терминала: {parsed_data['version']}\n"
                f"Растояние от головной станции (м): {parsed_data['distance']}\n"
                f"ONT Rx (оптический сигнал на терминале)(dBm): {parsed_data['ont_rx_power']}\n"
                f"OLT Rx (сигнал на головной станции)(dBm): {parsed_data['olt_rx_power']}\n"
                f"Время последнего включения: {parsed_data['uptime']}\n"
            )

            # прибавлюю к строке состояние LAN портов
            for port_state in parsed_data.get("lan_port", []):
                if port_state['link_state'] == 'up':  # Проверяем состояние порта
                    clipboard_data += (f"Port {port_state['port_id']}: Speed={port_state['speed']} Mbps, "
                    f"Duplex={port_state['duplex']}, Link State={port_state['link_state']}\n")
        
            # Добавляем ошибки оптики только если значение не равно нулю
            optic_errors = int(parsed_data.get('optic_errors', 0))
            if optic_errors != 0:
                clipboard_data += (
                    f"Ошибки оптики: {optic_errors}. "
                    "Выполнен сброс счётчика ошибок.\n\n"
                )
            else:
                clipboard_data += "Ошибок оптики нет.\n\n"
        
            try:
                # Рекомендация в случае низкого уровня оптического сигнала
                ont_laser = float(parsed_data['ont_rx_power'])
                olt_laser = float(parsed_data['olt_rx_power'])
                if ont_laser < -26.9 or olt_laser < -32:
                    clipboard_data += "Низкий уровень оптического сигнала. Необходима проверка оптической линии.\n"
            except (KeyError, ValueError) as e:
                # Обработка случаев, когда ключ отсутствует или значение не числовое
                clipboard_data += "Ошибка при проверке уровня оптического сигнала: данные отсутствуют или некорректны.\n"
        else:
            clipboard_data = (
                f"Терминал недоступен.\nПоследнее включение: {parsed_data['uptime']}\n"
                f"Отключен: {parsed_data['downtime']}\n"
                )
            if parsed_data['down_cause'] == 'dying-gasp':
                clipboard_data += f"Причина недоступности терминала - отключение электропитания."
            elif parsed_data['down_cause'] == 'LOS':
                clipboard_data += f"Причина недоступности терминала - отсутствие оптического сигнала."
        
        if output_ont_info:
            crt.Dialog.MessageBox(str(parsed_data))
            
            # Помещаем данные в буфер обмена
            pyperclip.copy(clipboard_data)

main()