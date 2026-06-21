# $language = "Python3"
# $interface = "1.0"

import os
import re
import sys
import time
import traceback
import pyperclip

# ========================================================================
# Модуль GPON_class.py — содержит классы и утилиты для работы с GPON ONT
# ========================================================================

# ==================== ИНЪЕКЦИЯ CRT ====================

# Глобальная ссылка на объект crt (инициализируется из основного скрипта)
# crt = None

def inject_crt(obj):
    """Инъекция SecureCRT-объекта crt. Вызывать обязательно из основного скрипта после импорта этого модуля."""
    global crt
    crt = obj


def _ensure_crt():
    """Проверяет, что объект crt инициализирован."""
    if crt is None:
        raise RuntimeError("CRT не инициализирован.")

# ==================== КОНСТАНТЫ ====================

PRESS_Q: str = "---- More ( Press 'Q' to break ) ----"

# Команды головной станции Huawei
COMMANDS = {
    'ont_info': "display ont info {frame} {slot} {port} {ont}",
    'info_by_serial': "display ont info by-sn {serial}",
    'info_by_description': "display ont info by-desc {description}",
    'ont_version': "display ont version {frame} {slot} {port} {ont}",
    'optical_info': "display ont optical-info {port} {ont}",
    'ont_line_quality': "{command} statistics ont-line-quality {port} {ont}",
    'eth_ports': "display ont port state {port} {ont} eth-port all",
    'eth_errors': "{command} statistics ont-eth {port} {ont} ont-port {lan_id}",
    'port_switch': "ont port attribute {port} {ont} eth {lan_id} operational-state {state}",
    'remote_ping': "ont remote-ping {port} {ont} ip-address {ip}",
    'pressQ': "( Press 'Q' to break ) ----",
}

# Паттерны для парсинга вывода
PATTERNS = {
    "ont_by_sn": r"F\/S\/P\s*:\s(\d+)\/(\d+)\/(\d+).*ONT-ID\s*:\s(\d+)",
    "ont_by_desc": r"(\d+)\/\s*(\d+)\/\s*(\d+)\s+(\d+)",
    "status": r"Run state\s+:\s(\S+)",
    "serial": r"(?i)SN\s+:\s*([\da-f]{16})",
    "description": r"Description\s+:\s(\S+)",
    "uptime": r"Last up time\s+:\s*([\d-]+\s[\d:+-]+)",
    "downtime": r"Last down time\s+:\s*([\d-]+\s[\d:+-]+)",
    "downcause": r"Last down cause\s+:\s(\S+)",
    "distance": r" distance\(m\)\s*:\s*(\d+)",
    "soft_version": r"Main Software Version\s*:\s*(\S*)",
    "ont_model": r"OntProductDescription\s+: EchoLife (\S+) GPON",
    "ont_model2": r"Equipment-ID\s*:\s*(\w+)",
    "ont_rx_power": r"Rx optical power\(dBm\)\s*:\s*([-+]?\d+(?:\.\d+)?)",
    "olt_rx_power": r"OLT Rx ONT optical power\(dBm\)\s*:\s*([-+]?\d+(?:\.\d+)?)",
    "lan_ports": r"(\d+)\s+(\d+)\s+(GE|FE)\s+(\d+|-)+\s+(full|half|-)+\s+(up|down)",
    "upstream_errors": r"Upstream frame BIP error count\s*:\s*(\d+)",
    "downstream_errors": r"Downstream frame BIP error count\s*:\s*(\d+)",
    "eth_errors": {
        "fcs": r"Received FCS error frames\s*:\s*(\d+)",
        "received_bad_bytes": r"Received bad bytes\s*:\s*(\d+)",
        "sent_bad_bytes": r"Sent bad bytes\s*:\s*(\d+)",
    },
    "mac_addresses": r"(ETH|WLAN)\s+(\d+)\s+([0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4})",
    "register_info_status": r"Status\s*:\s*(\w+)",
    "register_info_age": r"Age\(s\)\s*:\s*(\d+)",
}

# Плохие версии ПО
BAD_VERSIONS = {
    "V1R003C00S108",
    "V1R006C00S130",
    "V1R006C00S205",
    "V1R006C00S201",
    "V1R006C01S201",
}

# ==================== КЛАСС ONT ====================

class Ont:
    """Класс для представления ONT и выполнения базовых операций."""

    def __init__(self, ontSelect: list = None):
        """Инициализация объекта ONT из списка параметров (frame, slot, port, ont).
        Если список не передан — читает из буфера обмена."""
        if ontSelect is None or len(ontSelect) < 4:
            memBuffer = pyperclip.paste()
            ontSelect = memBuffer.replace('/', ' ').split()
        if ontSelect is None or len(ontSelect) < 4:
            raise ValueError("Некорректное содержимое буфера")
        self.frame = ontSelect[0]
        self.slot = ontSelect[1]
        self.port = ontSelect[2]
        self.ont = ontSelect[3]
        self.sn = ontSelect[4] if len(ontSelect) > 4 else ""

    def _enter_interface(self) -> None:
        """Переход в контекст interface gpon для данной ONT."""
        crt.Screen.Send(f"interface gpon {self.frame}/{self.slot}\r")

    def delete_ont(self) -> None:
        """Удаление сервисных портов и самой ONT."""
        _ensure_crt()
        scr = crt.Screen
        scr.Send(f"{undoServPort} {self.frame}/{self.slot}/{self.port} ont {self.ont}\r")
        scr.WaitForString("gemport", 1)
        scr.Send("\r")
        scr.WaitForString("(y/n)", 5)
        scr.Send("y\r")
        scr.WaitForString("#", 10)
        self._enter_interface()
        scr.Send(f"{ont_delete} {self.port} {self.ont}\r")
        scr.Send("q\r")

    def get_optic(self) -> None:
        """Получает уровень оптики."""
        _ensure_crt()
        self._enter_interface()
        crt.Screen.Send(COMMANDS['optical_info'].format(port=self.port, ont=self.ont))
        crt.Screen.Send("\r quit\r")

    def get_info(self) -> None:
        """Получает информацию об ONT."""
        _ensure_crt()
        try:
            crt.Screen.Send(f"{ont_info} {self.frame} {self.slot} {self.port} {self.ont}\rq")
        except Exception as e:
            crt.Dialog.MessageBox(f"Ошибка при получении данных ONT: {e}")

    def set_serial(self, serial: str) -> None:
        """Устанавливает серийный номер ONT."""
        _ensure_crt()
        self._enter_interface()
        self.sn = serial

# ==================== КЛАСС Diagnose DIAGNOSTICS ====================

class GPONDiagnostics:
    """Комплексная диагностика GPON ONT."""

    def __init__(self):
        self.parsed_data = self._init_parsed_data()
        self.modes = self._parse_arguments()
        self.mac_db = self._load_mac_database()

    def _init_parsed_data(self) -> dict:
        return {
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

    def _parse_arguments(self) -> dict:
        modes = {
            "no_actions": False,
            "optics_only": False,
            "register_only": False,
            "delete": False,
        }
        try:
            if crt.Arguments.Count > 0:
                for i in range(crt.Arguments.Count):
                    arg = crt.Arguments[i]
                    if arg == "-n":
                        modes["no_actions"] = True
                    elif arg == "-o":
                        modes["optics_only"] = True
                    elif arg == "-r":
                        modes["register_only"] = True
                    elif arg == "-d":
                        modes["delete"] = True
        except:
            pass
        return modes

    def _load_mac_database(self) -> dict:
        mac_db = {}
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            mac_db_path = os.path.join(script_dir, "oui.txt")
            pattern = re.compile(
                r"^([0-9A-Fa-f]{2}[-]?[0-9A-Fa-f]{2}[-]?[0-9A-Fa-f]{2})\s+\(hex\)\s+(.+)"
                r"|^([0-9A-Fa-f]{6})\s+\(base 16\)\s+(.+)"
            )
            with open(mac_db_path, "r", encoding="utf-8") as file:
                for line in file:
                    match = pattern.match(line.strip())
                    if not match:
                        continue
                    oui = (match.group(1) or match.group(3)).replace("-", "").upper()
                    vendor = (match.group(2) or match.group(4)).strip()
                    mac_db[oui] = vendor.split()[0] if vendor else ""
        except:
            pass
        return mac_db

    # Маппинг: подстрока команды → символ(ы), отправляемые после команды
    _POST_COMMAND_KEYS = (
        ("display ont info", "q"),
        ("optical-info", " "),
        ("wan-info", " "),
        ("port state", "\r"),
        ("remote-ping", "\r"),
        ("ont-port", "  "),
        ("register-info", "   "),
    )

    @staticmethod
    def send_command(command: str, delay: float = 0.1) -> str:
        _ensure_crt()
        crt.Screen.Send(command + "\r")
        time.sleep(0.2)

        for key, send_val in Diagnose._POST_COMMAND_KEYS:
            if key in command and not (key == "display ont info" and "by-desc" in command):
                crt.Screen.Send(send_val)
                break

        time.sleep(delay)
        return Diagnose.read_output()

    @staticmethod
    def read_output() -> str:
        _ensure_crt()
        output = ""
        while True:
            line = crt.Screen.ReadString("\n", 1)
            if not line:
                break
            output += line
        return output

    def _enter_interface(self, frame, slot) -> None:
        """Переход в контекст interface gpon."""
        self.send_command(f"interface gpon {frame}/{slot}")

    def _quit_interface(self) -> None:
        """Выход из контекста interface."""
        self.send_command("quit")

    @staticmethod
    def parse_output(output: str, pattern: str, transform=lambda x: x):
        match = re.search(pattern, output)
        return transform(match.group(1)) if match else None

    def _parse_by_serial(self, output: str) -> tuple:
        match = re.search(PATTERNS["ont_by_sn"], output)
        if not match:
            raise ValueError("Не удалось найти данные ONT по серийному номеру!")
        return match.groups()

    def _parse_by_description(self, output: str) -> tuple:
        match = re.search(PATTERNS["ont_by_desc"], output)
        if not match:
            raise ValueError("Не удалось найти данные ONT по дескрипшену!")
        return match.groups()

    def _fill_common_ont_fields(self, output_ont_info: str) -> None:
        for key in ("status", "distance", "serial", "description", "uptime", "downtime", "downcause"):
            self.parsed_data[key] = self.parse_output(output_ont_info, PATTERNS[key]) or self.parsed_data[key]

    def _get_vendor(self, mac_address: str) -> str:
        cleaned_mac = re.sub(r"[^a-fA-F0-9]", "", mac_address).upper()
        return self.mac_db.get(cleaned_mac[:6], "n/a")

    def detect_ont(self, mem_buffer: str) -> tuple:
        mem_buffer = mem_buffer.strip()

        if re.fullmatch(r"(?i)(48575443|hwtc)[\da-z]{8}", mem_buffer):
            output_ont_info = self.send_command(COMMANDS["info_by_serial"].format(serial=mem_buffer.upper()))
            if output_ont_info:
                frame, slot, port, ont = self._parse_by_serial(output_ont_info)
                self._fill_common_ont_fields(output_ont_info)
                return frame, slot, port, ont, output_ont_info

        ont_data = mem_buffer.replace("/", " ").split()
        if len(ont_data) == 4:
            frame, slot, port, ont = ont_data
            output_ont_info = self.send_command(COMMANDS["ont_info"].format(frame=frame, slot=slot, port=port, ont=ont))
            self._fill_common_ont_fields(output_ont_info)
            return frame, slot, port, ont, output_ont_info

        if 4 < len(mem_buffer) <= 16:
            output = self.send_command(COMMANDS["info_by_description"].format(description=mem_buffer))
            frame, slot, port, ont = self._parse_by_description(output)
            output_ont_info = self.send_command(COMMANDS["ont_info"].format(frame=frame, slot=slot, port=port, ont=ont))
            self._fill_common_ont_fields(output_ont_info)
            return frame, slot, port, ont, output_ont_info

        raise ValueError(
            "Несоответствующее запросу содержимое буфера обмена!\n"
            f"(длина {len(mem_buffer)})\nНеобходимо скопировать серийный номер, "
            "номер лицевого счёта или ONT (пример: 0/1/1 10)"
        )

    def _update_optic_value(self, output: str, key: str) -> None:
        """Парсит и нормализует значение оптической мощности."""
        val = self.parse_output(output, PATTERNS[key], str)
        if val == "-":
            val = "нет данных"
        self.parsed_data[key] = val or self.parsed_data[key]

    def diagnose_optics(self, frame, slot, port, ont, clipboard_data: str) -> str:
        output_optical_info = self.send_command(COMMANDS["optical_info"].format(port=port, ont=ont), 1)

        for key in ("ont_rx_power", "olt_rx_power"):
            self._update_optic_value(output_optical_info, key)

        clipboard_data += (
            f"ONT Rx (сигнал на терминале)(dBm): {self.parsed_data['ont_rx_power']}\n"
            f"OLT Rx (сигнал на головной станции)(dBm): {self.parsed_data['olt_rx_power']}\n"
        )

        ont_rx_val = self.parsed_data["ont_rx_power"]
        olt_rx_val = self.parsed_data["olt_rx_power"]

        if ont_rx_val != "нет данных" and olt_rx_val != "нет данных":
            try:
                if float(ont_rx_val) < -26.0:
                    self.parsed_data["troubleshooting"] += "Низкий уровень входящего сигнала (ONT RX). Необходима проверка оптической линии."
                elif float(olt_rx_val) < -32.0:
                    self.parsed_data["troubleshooting"] += "Низкий уровень обратного сигнала (OLT RX). Необходима проверка оптической линии."
            except ValueError:
                self.parsed_data["troubleshooting"] += "Не удалось определить уровень оптического сигнала! Необходима диагностика терминала."
        else:
            self.parsed_data["troubleshooting"] += "Не удалось определить уровень оптического сигнала! Необходима диагностика терминала."

        for cmd in ("display", "clear"):
            output = self.send_command(COMMANDS["ont_line_quality"].format(command=cmd, port=port, ont=ont))
            if cmd == "display":
                self.parsed_data["upstream_errors"] = self.parse_output(output, PATTERNS["upstream_errors"], int) or 0
                self.parsed_data["downstream_errors"] = self.parse_output(output, PATTERNS["downstream_errors"], int) or 0

        optic_errors = self.parsed_data["upstream_errors"] + self.parsed_data["downstream_errors"]

        if optic_errors:
            prefix = (
                "Обнаружено значительное количество ошибок оптики: "
                if optic_errors > 10000
                else "Незначительное количество ошибок оптики: "
            )
            clipboard_data += (
                f"{prefix}Upstream: {self.parsed_data['upstream_errors']}. "
                f"Downstream: {self.parsed_data['downstream_errors']}.\n"
            )
            clipboard_data += "Выполнен сброс счётчиков ошибок.\n"

        return clipboard_data

    def diagnose_lan_and_eth(self, port, ont, clipboard_data: str) -> str:
        output_lan_ports = self.send_command(COMMANDS["eth_ports"].format(port=port, ont=ont))
        self.parsed_data["lan_ports"] = [
            {
                "lan_id": m.group(2),
                "port_type": m.group(3),
                "speed": m.group(4),
                "duplex": m.group(5),
                "link_state": m.group(6),
            }
            for m in re.finditer(PATTERNS["lan_ports"], output_lan_ports)
        ]

        has_eth_errors = False
        for port_state in self.parsed_data["lan_ports"]:
            if port_state["link_state"] != "up":
                continue

            lan_id = port_state["lan_id"]
            clipboard_data += (
                f"LAN{lan_id}: Type={port_state['port_type']}, Speed={port_state['speed']} Mbps, "
                f"Duplex={port_state['duplex']}, Link State={port_state['link_state']}\n"
            )

            if not self.modes["no_actions"]:
                for state in ("off", "on"):
                    self.send_command(
                        COMMANDS["port_switch"].format(port=port, ont=ont, lan_id=lan_id, state=state)
                    )

            for cmd in ("display", "clear"):
                output_eth_errors = self.send_command(
                    COMMANDS["eth_errors"].format(command=cmd, port=port, ont=ont, lan_id=lan_id)
                )
                if cmd == "display":
                    eth_err = {
                        key: self.parse_output(output_eth_errors, pattern, int) or 0
                        for key, pattern in PATTERNS["eth_errors"].items()
                    }

            if any(eth_err.values()):
                has_eth_errors = True
                clipboard_data += (
                    f"Обнаружены ошибки на порту LAN{lan_id}: "
                    f"FCS={eth_err['fcs']}, Input={eth_err['received_bad_bytes']}, "
                    f"Output={eth_err['sent_bad_bytes']}.\n"
                )

        if has_eth_errors:
            clipboard_data += "Выполнен сброс счётчиков ошибок.\n"
            self.parsed_data["troubleshooting"] += "Обратить внимание на состояние патчкордов.\n"
        else:
            clipboard_data += "Ошибок портов LAN нет.\n"

        return clipboard_data

    def collect_mac_info(self, frame, slot, port, ont, clipboard_data: str) -> str:
        mac_output = self.send_command(f"display mac-address ont {frame}/{slot}/{port} {ont}\r")

        mac_pattern = re.compile(PATTERNS["mac_addresses"])
        seen_macs = set()

        for match in mac_pattern.finditer(mac_output):
            port_type, port_number, mac = match.group(1), match.group(2), match.group(3)

            if mac in seen_macs:
                continue
            seen_macs.add(mac)

            vendor = self._get_vendor(mac)
            port_label = "LAN" if port_type == "ETH" else port_type
            clipboard_data += f"{port_label}{port_number} {mac} — {vendor}\n"

        return clipboard_data

    def handle_offline(self, clipboard_data: str) -> str:
        downtime = self.parsed_data["downtime"]
        downcause = self.parsed_data["downcause"]

        if not any(ch.isdigit() for ch in downtime):
            self.parsed_data["downtime"] = "нет данных"
            self.parsed_data["downcause"] = "нет данных" if "-" in downcause else downcause
            self.parsed_data["troubleshooting"] += "Интернет не работает. Запись о причине недоступности терминала отсутствует."
        elif "LOFi" in downcause:
            self.parsed_data["downcause"] += " — низкий/отсутствует уровень оптического сигнала."
            self.parsed_data["troubleshooting"] += "Интернет не работает. Необходима проверка оптической линии."
        elif "LOS" in downcause:
            self.parsed_data["downcause"] += " — отсутствует оптический сигнал."
            self.parsed_data["troubleshooting"] += "Интернет не работает. Необходима проверка оптической линии."
        elif "dying-gasp" in downcause:
            self.parsed_data["downcause"] += " — отключение эл.питания."
            self.parsed_data["troubleshooting"] += "Интернет не работает. Необходима проверка терминала и БП."
        else:
            raise Exception("Сбой диагностики!")

        clipboard_data += (
            f"Отключён: {self.parsed_data['downtime']}\n"
            f"Время последнего включения: {self.parsed_data['uptime']}\n"
            f"Расстояние от головной станции (м): {self.parsed_data['distance']}\n"
            f"Причина недоступности — {self.parsed_data['downcause']}\n\n"
            f"{self.parsed_data['troubleshooting']}"
        )
        return clipboard_data

    def handle_online(self, frame, slot, port, ont, clipboard_data: str) -> str:
        output_version = self.send_command(
            COMMANDS["ont_version"].format(frame=frame, slot=slot, port=port, ont=ont)
        )
        model = self.parse_output(output_version, PATTERNS["ont_model"]) or self.parse_output(output_version, PATTERNS["ont_model2"])
        self.parsed_data["model"] = model or self.parsed_data["model"]
        self.parsed_data["version"] = self.parse_output(output_version, PATTERNS["soft_version"]) or self.parsed_data["version"]

        version = self.parsed_data["version"]
        bad_mark = " !!!" if version in BAD_VERSIONS else ""

        clipboard_data += (
            f"Включён: {self.parsed_data['uptime']}\n"
            f"Модель терминала: '{self.parsed_data['model']}'\n"
            f"Версия ПО терминала: '{version}'{bad_mark}\n"
            f"Расстояние: {self.parsed_data['distance']} м\n"
        )

        if version in BAD_VERSIONS:
            self.parsed_data["troubleshooting"] += "Необходимо обновление ПО терминала. "

        self._enter_interface(frame, slot)

        clipboard_data = self.diagnose_optics(frame, slot, port, ont, clipboard_data)
        clipboard_data = self.diagnose_lan_and_eth(port, ont, clipboard_data)

        if "310" not in self.parsed_data["model"]:
            self.send_command(f"display ont ipconfig {port} {ont}")
            self.send_command(f"display ont wan-info {port} {ont}")
            self.send_command(f"ont remote-ping {port} {ont} ip-address 77.88.8.8")

        self._quit_interface()
        clipboard_data = self.collect_mac_info(frame, slot, port, ont, clipboard_data)

        if not self.parsed_data["troubleshooting"]:
            clipboard_data += "\nНарушений не выявлено."
        elif "Необходима" in self.parsed_data["troubleshooting"]:
            clipboard_data += f"\n{self.parsed_data['troubleshooting']}"
        else:
            clipboard_data += f"\n{self.parsed_data['troubleshooting']}Нарушений оптики нет."

        return clipboard_data

    def diagnose_optics_only(self, frame, slot, port, ont, clipboard_data: str) -> str:
        self._enter_interface(frame, slot)
        clipboard_data = self.diagnose_optics(frame, slot, port, ont, clipboard_data)
        self._quit_interface()
        return clipboard_data

    def diagnose_register_only(self, frame, slot, port, ont, clipboard_data: str) -> str:
        self._enter_interface(frame, slot)
        output = self.send_command(COMMANDS.get("register_info", f"display ont register-info {port} {ont}"))
        self._quit_interface()

        status_match = re.search(PATTERNS["register_info_status"], output)
        age_match = re.search(PATTERNS["register_info_age"], output)

        status = status_match.group(1) if status_match else "неизвестно"
        age = age_match.group(1) if age_match else "нет данных"

        clipboard_data += f"Статус регистрации: {status}\nВремя с последней регистрации (с): {age}\n"
        return clipboard_data

    def run(self) -> None:
        try:
            mem_buffer = pyperclip.paste().strip()

            if not mem_buffer:
                crt.Screen.Send("\rdisplay ont info by-desc ")
                return

            crt.Screen.Send("\n")
            last_line = crt.Screen.ReadString("#", 1)
            if "(config)" not in last_line.strip():
                crt.Screen.Send("quit\r")

            frame, slot, port, ont, _ = self.detect_ont(mem_buffer)

            clipboard_data = (
                f"ONT = {frame}/{slot}/{port}/{ont}\n"
                f"Дескрипшн (лицевой счёт) = {self.parsed_data['description']}\n"
                f"PON SN = {self.parsed_data['serial']}\n"
            )

            if self.modes["delete"]:
                ont_obj = Ont([frame, slot, port, ont])
                ont_obj.delete_ont()
                clipboard_data = f"ONT {frame}/{slot}/{port}/{ont} успешно удалён.\n"
            elif self.modes["register_only"]:
                clipboard_data = self.diagnose_register_only(frame, slot, port, ont, clipboard_data)
            elif self.modes["optics_only"]:
                clipboard_data = self.diagnose_optics_only(frame, slot, port, ont, clipboard_data)
            else:
                clipboard_data += f"Терминал {'доступен' if self.parsed_data['status'] == 'online' else 'недоступен'}.\n"

                if self.parsed_data["status"] == "offline":
                    clipboard_data = self.handle_offline(clipboard_data)
                elif self.parsed_data["status"] == "online":
                    clipboard_data = self.handle_online(frame, slot, port, ont, clipboard_data)

            pyperclip.copy(clipboard_data)

        except Exception as e:
            error_line = traceback.extract_tb(e.__traceback__)[-1].lineno
            crt.Dialog.MessageBox(f"Ошибка в строке № {error_line}:\n{e}")
            crt.Screen.Send("display ont info ")


# ==================== ТОЧКА ВХОДА ====================

if __name__ == "builtins":
    try:
        crt.Screen.Send("scroll 32\n")
        memBuffer = pyperclip.paste()
        ontSelect = memBuffer.replace('/', ' ').split()
        ont = Ont(ontSelect)
        ont.get_info()
    except pyperclip.PyperclipException as e:
        crt.Dialog.MessageBox(f"Ошибка чтения буфера обмена:\r{e}")
    except ValueError as e:
        crt.Dialog.MessageBox(f"Ошибка при получении данных об ONT: {e}")
    except Exception as e:
        crt.Dialog.MessageBox(f"Ошибка при выполнении:\r{e}")

