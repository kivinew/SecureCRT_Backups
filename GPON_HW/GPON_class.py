# $language = "Python3"
# $interface = "1.0"

import re
import pyperclip

crt = None


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
        "{command} statistics ont-eth "
        "{port} {ont} ont-port {lan_id}"
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

            result = scr.ReadString(
                ["---- More ----", "#"],
                2
            )

            output += result

            if "---- More ----" in result:

                scr.Send(" ")

            elif "#" in result:

                break

        return output

    def parse(self, output, pattern):

        match = re.search(
            pattern,
            output
        )

        if match:

            return match.group(1).strip()

        return None

    def get_ont_info(self):

        cmd = COMMANDS["ont_info"].format(
            frame=self.ont.frame,
            slot=self.ont.slot,
            port=self.ont.port,
            ont=self.ont.ont
        )

        output = self.send(cmd)

        fields = [

            "status",
            "serial",
            "description",
            "distance",
            "uptime",
            "downtime",
            "downcause"
        ]

        for field in fields:

            value = self.parse(
                output,
                PATTERNS[field]
            )

            if value:

                self.data[field] = value

    def get_version(self):

        cmd = COMMANDS["ont_version"].format(
            frame=self.ont.frame,
            slot=self.ont.slot,
            port=self.ont.port,
            ont=self.ont.ont
        )

        output = self.send(cmd)

        model = self.parse(
            output,
            PATTERNS["ont_model"]
        )

        version = self.parse(
            output,
            PATTERNS["soft_version"]
        )

        if model:
            self.data["model"] = model

        if version:
            self.data["version"] = version

    def diagnose_optics(self):

        crt.Screen.Send(
            f"interface gpon "
            f"{self.ont.frame}/"
            f"{self.ont.slot}\r"
        )

        cmd = COMMANDS[
            "optical_info"
        ].format(
            port=self.ont.port,
            ont=self.ont.ont
        )

        output = self.send(cmd)

        ont_rx = self.parse(
            output,
            PATTERNS["ont_rx_power"]
        )

        olt_rx = self.parse(
            output,
            PATTERNS["olt_rx_power"]
        )

        self.data["ont_rx_power"] = ont_rx
        self.data["olt_rx_power"] = olt_rx

        if ont_rx:

            power = float(ont_rx)

            if power < -26:

                self.data[
                    "troubleshooting"
                ] += (
                    "Низкий уровень "
                    "оптики ONT\n"
                )

    def diagnose_lan(self):

        cmd = COMMANDS[
            "eth_ports"
        ].format(
            port=self.ont.port,
            ont=self.ont.ont
        )

        output = self.send(cmd)

        if "up" not in output:

            self.data[
                "troubleshooting"
            ] += (
                "Нет активных "
                "LAN портов\n"
            )

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

        if (
            self.data["status"]
            .lower()
            != "online"
        ):

            return self.offline_report()

        self.get_version()

        self.diagnose_optics()

        self.diagnose_lan()

        return self.online_report()