# $language = "Python3"
# $interface = "1.0"

import re
import pyperclip

# Константы, использующиеся в старом классе GPON_class_old
undoServPort = "undo service-port port"
ifaceGpon = "interface gpon "
ont_delete = "ont delete "


def inject_crt(obj):
    global crt
    crt = obj


COMMANDS = {
    "ont_info":
        "display ont info {frame} {slot} {port} {ont}",

    "ont_version":
        "display ont version {frame} {slot} {port} {ont}",

    "optical_info":
        "display ont optical-info {port} {ont}",

    "eth_ports":
        "display ont port state {port} {ont} eth-port all",

    "eth_errors":
        "{command} statistics ont-eth {port} {ont} ont-port {lan_id}",

    # Additional commands used by old diagnostics
    "ont_line_quality": "{command} statistics ont-line-quality {port} {ont}",
    "port_switch": "ont port attribute {port} {ont} eth {lan_id} operational-state {state}",
    "remote_ping": "ont remote-ping {port} {ont} ip-address {ip}"
}


PATTERNS = {

    "status":
        r"Run state\s+:\s+(\w+)",

    "serial":
        r"SN\s+:\s+(\S+)",

    "description":
        r"Description\s+:\s+(.+)",

    "distance":
        r"ONT distance\(m\)\s+:\s+(\d+)",

    "uptime":
        r"Last up time\s+:\s+(.+)",

    "downtime":
        r"Last down time\s+:\s+(.+)",

    "downcause":
        r"Last down cause\s+:\s+(.+)",

    "ont_model":
        r"ONT Type\s+:\s+(.+)",

    "soft_version":
        r"Main Software Version\s+:\s+(.+)",

    "ont_rx_power":
        r"Rx optical power\(dBm\)\s+:\s+(-?\d+\.\d+)",

    "olt_rx_power":
        r"OLT Rx ONT optical power\(dBm\)"
        r"\s+:\s+(-?\d+\.\d+)"
}


class Ont:

    def __init__(self, ont_select=None):

        if ont_select is None:

            buffer = pyperclip.paste()

            ont_select = (
                buffer
                .replace("/", " ")
                .split()
            )

        if len(ont_select) < 4:

            raise ValueError(
                "Некорректный формат буфера"
            )

        self.frame = ont_select[0]
        self.slot = ont_select[1]
        self.port = ont_select[2]
        self.ont = ont_select[3]

        self.sn = (
            ont_select[4]
            if len(ont_select) > 4
            else ""
        )

    # ---------------------------------------------------------------------
    # Методы, перенесённые из GPON_class_old для совместимости
    # ---------------------------------------------------------------------
    def delete_ont(self) -> None:
        """Удаление сервисных портов и самой ONT."""
        scr = crt.Screen
        if crt is None:
            raise RuntimeError("CRT не инициализирован.")
        try:
            # Удаляем сервис‑порт
            scr.Send(f"{undoServPort} {self.frame}/{self.slot}/{self.port} ont {self.ont}\r")
            scr.WaitForString("gemport", 5)
            scr.Send("\r")
            scr.WaitForString("(y/n)", 5)
            scr.Send("y\r")
            # Переходим в интерфейс GPON
            scr.Send(f"{ifaceGpon} {self.frame}/{self.slot}\r")
            # Удаляем ONT
            scr.Send(f"{ont_delete} {self.port} {self.ont}\r")
            scr.Send("q\r")
        except Exception as e:
            crt.Dialog.MessageBox(f"Ошибка при удалении ONT: {e}")

    def get_optic(self) -> None:
        """Получает уровень оптики ONT."""
        scr = crt.Screen
        if crt is None:
            raise RuntimeError("CRT не инициализирован.")
        scr.Send(f"{ifaceGpon} {self.frame}/{self.slot}\r")
        scr.Send(f"display ont optical-info {self.port} {self.ont}\r")
        scr.Send(" quit\r")

    def get_info(self) -> str:
        """Получает информацию об ONT (display ont info) с поддержкой постраничного вывода.

        Возвращает полный вывод команды как строку.
        """
        if crt is None:
            raise RuntimeError("CRT не инициализирован.")
        scr = crt.Screen
        command = f"display ont info {self.frame} {self.slot} {self.port} {self.ont}"
        scr.Send(command + "\r")
        output = ""
        while True:
            # Ожидаем либо окончание вывода (prompt "#"), либо сообщение о постраничном выводе "More",
            # либо возможность прервать "Press 'Q'".
            result = scr.ReadString(["Press 'Q'", "#", "More"], 1)
            output += result
            if "More" in result:
                # Пробел обычно продолжает вывод в SecureCRT
                scr.Send(" ")
                continue
            if "Press 'Q'" in result:
                scr.Send("q")
                break
            if "#" in result:
                break
        return output

    def set_serial(self, serial: str) -> None:
        """Устанавливает серийный номер ONT (используется в старом коде)."""
        scr = crt.Screen
        if crt is None:
            raise RuntimeError("CRT не инициализирован.")
        scr.Send(f"{ifaceGpon} {self.frame}/{self.slot}\r")
        self.sn = serial


class GPON:

    def __init__(self, ont):

        self.ont = ont

        self.data = {

            "status": "unknown",
            "serial": "",
            "description": "",
            "model": "",
            "version": "",

            "distance": "",

            "uptime": "",
            "downtime": "",
            "downcause": "",

            "ont_rx_power": "",
            "olt_rx_power": "",

            "troubleshooting": ""
        }

    def send(self, command):

        scr = crt.Screen

        scr.Send(command + "\r")

        output = ""

        while True:
            # Читаем строку, ожидая либо окончание вывода (prompt "#"),
            # либо сообщение о постраничном выводе "More".
            result = scr.ReadString(
                ["Press 'Q'", "#", "More"],
                1
            )

            output += result

            # Если встретилось сообщение о постраничном выводе, отправляем пробел
            # (обычно в SecureCRT это продолжает вывод) и продолжаем цикл.
            if "More" in result:
                # Некоторые устройства требуют именно пробел, иногда – Enter.
                scr.Send(" ")
                continue

            # Обычное завершение – пользователь может прервать нажатием Q.
            if "Press 'Q'" in result:
                scr.Send("q")
                break

            # Достигнут обычный командный промпт.
            if "#" in result:
                break

        return output

    # ---------------------------------------------------------------------
    # Внутренние методы диагностики (перенесены из старого скрипта)
    # ---------------------------------------------------------------------
    def parse(self, output, pattern):
        match = re.search(pattern, output)
        return match.group(1).strip() if match else None

    def get_ont_info(self):
        cmd = COMMANDS["ont_info"].format(
            frame=self.ont.frame,
            slot=self.ont.slot,
            port=self.ont.port,
            ont=self.ont.ont,
        )
        output = self.send(cmd)
        for field in ["status", "serial", "description", "distance", "uptime", "downtime", "downcause"]:
            value = self.parse(output, PATTERNS[field])
            if value:
                self.data[field] = value

    def get_version(self):
        cmd = COMMANDS["ont_version"].format(
            frame=self.ont.frame,
            slot=self.ont.slot,
            port=self.ont.port,
            ont=self.ont.ont,
        )
        output = self.send(cmd)
        model = self.parse(output, PATTERNS["ont_model"])
        version = self.parse(output, PATTERNS["soft_version"])
        if model:
            self.data["model"] = model
        if version:
            self.data["version"] = version

    def diagnose_optics(self):
        crt.Screen.Send(
            f"interface gpon {self.ont.frame}/{self.ont.slot}\r"
        )
        cmd = COMMANDS["optical_info"].format(port=self.ont.port, ont=self.ont.ont)
        output = self.send(cmd)
        ont_rx = self.parse(output, PATTERNS["ont_rx_power"])
        olt_rx = self.parse(output, PATTERNS["olt_rx_power"])
        self.data["ont_rx_power"] = ont_rx
        self.data["olt_rx_power"] = olt_rx
        if ont_rx:
            try:
                power = float(ont_rx)
                if power < -26:
                    self.data["troubleshooting"] += "Низкий уровень оптики ONT\n"
            except ValueError:
                pass

    def diagnose_lan(self):
        cmd = COMMANDS["eth_ports"].format(port=self.ont.port, ont=self.ont.ont)
        output = self.send(cmd)
        if "up" not in output:
            self.data["troubleshooting"] += "Нет активных LAN портов\n"

    def online_report(self):
        return f"""
ONT:
{self.ont.frame}/{self.ont.slot}/{self.ont.port}/{self.ont.ont}

SN:
{self.data["serial"]}

Описание:
{self.data["description"]}

Модель:
{self.data["model"]}

Прошивка:
{self.data["version"]}

Дистанция:
{self.data["distance"]}

RX ONT:
{self.data["ont_rx_power"]}

RX OLT:
{self.data["olt_rx_power"]}

Диагностика:

{self.data["troubleshooting"]}
"""

    def offline_report(self):
        return f"""
ONT OFFLINE

Последнее отключение:

{self.data["downtime"]}

Причина:

{self.data["downcause"]}
"""

    def diagnose(self):
        self.get_ont_info()
        if self.data["status"].lower() != "online":
            return self.offline_report()
        self.get_version()
        self.diagnose_optics()
        self.diagnose_lan()
        return self.online_report()

# ---------------------------------------------------------------------
# Точка входа при запуске из SecureCRT (используется условие "builtins")
# ---------------------------------------------------------------------
if __name__ == "builtins":
    try:
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