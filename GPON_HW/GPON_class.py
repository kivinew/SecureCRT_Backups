# $language = "Python3"
# $interface = "1.0"

import re
import pyperclip

crt = None

PRESS_Q = "---- More ( Press 'Q' to break ) ----"
PROMPT = "#"

ifaceGpon = "interface gpon "
undoServPort = "undo service-port port"
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
        "{command} statistics ont-eth "
        "{port} {ont} ont-port {lan_id}",

    "find_by_serial":
        "display ont info by-sn {serial}",

    "find_by_description":
        "display ont info by-desc {description}"
}


PATTERNS = {

    "status":
        r"Run state\s*:\s*(.+)",

    "serial":
        r"SN\s*:\s*(\S+)",

    "description":
        r"Description\s*:\s*(.+)",

    "distance":
        r"ONT distance\(m\)\s*:\s*(\d+)",

    "uptime":
        r"Last up time\s*:\s*(.+)",

    "downtime":
        r"Last down time\s*:\s*(.+)",

    "downcause":
        r"Last down cause\s*:\s*(.+)",

    "ont_model":
        r"ONT Type\s*:\s*(.+)",

    "soft_version":
        r"Main Software Version\s*:\s*(.+)",

    "ont_rx_power":
        r"Rx optical power\(dBm\)\s*:\s*(-?\d+\.\d+)",

    "olt_rx_power":
        r"OLT Rx ONT optical power\(dBm\)"
        r"\s*:\s*(-?\d+\.\d+)"
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
                "Неверный формат GPON адреса"
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

    @classmethod
    def from_address(cls, address):

        parsed = (
            address
            .replace("/", " ")
            .split()
        )

        return cls(parsed)

    def delete_ont(self):

        scr = crt.Screen

        scr.Send(
            f"{undoServPort} "
            f"{self.frame}/"
            f"{self.slot}/"
            f"{self.port} "
            f"ont "
            f"{self.ont}\r"
        )

        scr.WaitForString(
            "gemport",
            5
        )

        scr.Send("\r")

        scr.WaitForString(
            "(y/n)",
            5
        )

        scr.Send("y\r")

        scr.Send(
            f"{ifaceGpon}"
            f"{self.frame}/"
            f"{self.slot}\r"
        )

        scr.Send(
            f"{ont_delete} "
            f"{self.port} "
            f"{self.ont}\r"
        )

        scr.Send(
            "quit\r"
        )


class GPON:

    def __init__(self, ont=None):

        self.ont = ont

        self.data = {

            "status": "",

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

    def _wait_prompt(self):

        """Ждём настоящий prompt, игнорируя # внутри данных."""

        scr = crt.Screen

        while True:

            idx = scr.WaitForString(
                "#",
                5
            )

            if idx == 0:

                continue

            cur = scr.CurrentRow

            try:

                line = scr.Get(
                    cur,
                    1,
                    cur,
                    200
                ).strip()

                if line.endswith("#"):

                    return

            except:

                pass

    def send(self, command, max_more=0):

        """Отправка команды и сбор вывода с обработкой пагинации.

        max_more:
            -1 — листать до конца (пробелы)
            0  — сразу q (первая страница)
            N  — N пробелов, затем q
        """
        scr = crt.Screen

        scr.Send(command + "\r")

        output = ""
        more_count = 0

        while True:

            row_before = scr.CurrentRow

            index = scr.WaitForStrings(
                [
                    "---- More ( Press 'Q' to break ) ----",
                    "#"
                ],
                5
            )

            if index == 0:

                for r in range(
                    row_before,
                    scr.CurrentRow + 1
                ):

                    line = scr.Get(
                        r,
                        1,
                        r,
                        200
                    ).strip()

                    if line:

                        output += line + "\n"

                break

            for r in range(
                row_before,
                scr.CurrentRow + 1
            ):

                line = scr.Get(
                    r,
                    1,
                    r,
                    200
                ).strip()

                if line:

                    output += line + "\n"

            if index == 1:

                if max_more == -1:

                    scr.Send(" ")

                    continue

                if more_count < max_more:

                    scr.Send(" ")

                    more_count += 1

                    continue

                scr.Send("q")

                self._wait_prompt()

                break

            if index == 2:

                if self._is_real_prompt():

                    break

                continue

        return output

    def _is_real_prompt(self):

        """Текущая строка заканчивается на # — значит это prompt."""

        try:

            line = crt.Screen.Get(
                crt.Screen.CurrentRow,
                1,
                crt.Screen.CurrentRow,
                200
            ).strip()

            return line.endswith("#")

        except:

            return False

    def parse(
        self,
        output,
        pattern
    ):

        match = re.search(
            pattern,
            output
        )

        if match:

            return (
                match
                .group(1)
                .strip()
            )

        return None

    def parse_ont(
        self,
        output
    ):

        match = re.search(

            r"(\d+)/(\d+)/(\d+)\s+(\d+)",

            output
        )

        if not match:

            return None

        return Ont([

            match.group(1),

            match.group(2),

            match.group(3),

            match.group(4)
        ])

    def find_by_serial(
        self,
        serial
    ):

        cmd = COMMANDS[
            "find_by_serial"
        ].format(
            serial=serial
        )

        output = self.send(
            cmd,
            max_more=0
        )

        return self.parse_ont(
            output
        )

    def find_by_description(
        self,
        description
    ):

        cmd = COMMANDS[
            "find_by_description"
        ].format(
            description=description
        )

        output = self.send(
            cmd,
            max_more=0
        )

        return self.parse_ont(
            output
        )

    def get_ont_info(self):

        cmd = COMMANDS[
            "ont_info"
        ].format(

            frame=self.ont.frame,

            slot=self.ont.slot,

            port=self.ont.port,

            ont=self.ont.ont
        )

        output = self.send(
            cmd,
            max_more=1
        )

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

                self.data[
                    field
                ] = value

    def get_version(self):

        cmd = COMMANDS[
            "ont_version"
        ].format(

            frame=self.ont.frame,

            slot=self.ont.slot,

            port=self.ont.port,

            ont=self.ont.ont
        )

        scr = crt.Screen

        scr.Send(
            cmd + "\r"
        )

        self._wait_prompt()

    def diagnose_online(self):

        scr = crt.Screen

        # Вход в interface gpon
        scr.Send(
            f"interface gpon "
            f"{self.ont.frame}/"
            f"{self.ont.slot}\r"
        )

        self._wait_prompt()

        # Оптика — листать до конца
        out_optics = self.send(
            COMMANDS["optical_info"].format(
                port=self.ont.port,
                ont=self.ont.ont
            ),
            max_more=-1
        )

        # LAN — листать до конца
        out_lan = self.send(
            COMMANDS["eth_ports"].format(
                port=self.ont.port,
                ont=self.ont.ont
            ),
            max_more=-1
        )

        # Выход из interface gpon
        scr.Send("quit\r")

        self._wait_prompt()

        ont_rx = self.parse(
            out_optics,
            PATTERNS["ont_rx_power"]
        )

        olt_rx = self.parse(
            out_optics,
            PATTERNS["olt_rx_power"]
        )

        self.data["ont_rx_power"] = ont_rx or ""
        self.data["olt_rx_power"] = olt_rx or ""

        if ont_rx:

            try:

                power = float(ont_rx)

                if power < -26:

                    self.data[
                        "troubleshooting"
                    ] += "Низкий уровень оптики\n"

            except:

                pass

        if "up" not in out_lan:

            self.data[
                "troubleshooting"
            ] += "Нет активных LAN портов\n"

    def diagnose(self):

        self.get_ont_info()

        if (

            "online"

            not in

            self.data[
                "status"
            ].lower()

        ):

            return self.offline_report()

        self.get_version()

        self.diagnose_online()

        return self.online_report()

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