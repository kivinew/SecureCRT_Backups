#$language = "Python3"
#$interface = "1.0"

from __future__ import annotations

import re
import os
import sys
from typing import Any, Dict, List, Optional

import pyperclip

_g_crt: Any = None

PRESS_Q: str = "---- More ( Press 'Q' to break ) ----"

COMMANDS: Dict[str, str] = {
    "ont_info": "display ont info {frame} {slot} {port} {ont}",
    "ont_version": "display ont version {frame} {slot} {port} {ont}",
    "optical_info": "display ont optical-info {port} {ont}",
    "ont_line_quality": "{command} statistics ont-line-quality {port} {ont}",
    "eth_ports": "display ont port state {port} {ont} eth-port all",
    "eth_errors": "{command} statistics ont-eth {port} {ont} ont-port {lan_id}",
    "port_switch": "ont port attribute {port} {ont} eth {lan_id} operational-state {state}",
    "remote_ping": "ont remote-ping {port} {ont} ip-address {ip}",
    "ipconfig": "display ont ipconfig {port} {ont}",
    "find_by_serial": "display ont info by-sn {serial}",
    "find_by_description": "display ont info by-desc {description}",
    "mac_addresses": "display mac-address ont {frame}/{slot}/{port} {ont}",
    "undo_service_port": "undo service-port port {frame}/{slot}/{port} ont {ont}",
    "ont_delete": "ont delete {port} {ont}",
    "interface_gpon": "interface gpon {frame}/{slot}",
}

PATTERNS: Dict[str, str] = {
    "status": r"Run state\s*:\s*(.+)",
    "serial": r"(?i)SN\s*:\s*([\da-fA-F]{16})",
    "description": r"Description\s*:\s*(.+)",
    "distance": r"ONT distance\(m\)\s*:\s*(\d+)",
    "uptime": r"Last up time\s*:\s*([\d-]+\s[\d:+-]+)",
    "downtime": r"Last down time\s*:\s*([\d-]+\s[\d:+-]+)",
    "downcause": r"Last down cause\s*:\s*(\S+)",
    "ont_model": r"ONT Type\s*:\s*(.+)",
    "ont_model_alt": r"Equipment-ID\s*:\s*(\w+)",
    "soft_version": r"Main Software Version\s*:\s*(\S+)",
    "ont_rx_power": r"Rx optical power\(dBm\)\s*:\s*(-?\d+\.?\d*)",
    "olt_rx_power": r"OLT Rx ONT optical power\(dBm\)\s*:\s*(-?\d+\.?\d*)",
    "upstream_errors": r"Upstream frame BIP error count\s*:\s*(\d+)",
    "downstream_errors": r"Downstream frame BIP error count\s*:\s*(\d+)",
    "lan_ports": r"(\d+)\s+(\d+)\s+(GE|FE)\s+(\d+|-)+\s+(full|half|-)\s+(up|down)",
    "fcs_errors": r"Received FCS error frames\s*:\s*(\d+)",
    "rx_bad_bytes": r"Received bad bytes\s*:\s*(\d+)",
    "tx_bad_bytes": r"Sent bad bytes\s*:\s*(\d+)",
    "mac_entry": r"(ETH|WLAN)\s+(\d)+\s+([\da-fA-F]{4}-[\da-fA-F]{4}-[\da-fA-F]{4})",
    "ont_by_sn": r"F/S/P\s*:\s*(\d+)/(\d+)/(\d+).*ONT-ID\s*:\s*(\d+)",
    "ont_by_desc": r"(\d+)/\s*(\d+)/\s*(\d+)\s+(\d+)",
    "ip_output": r"IP address\s*:\s*(\d+\.\d+\.\d+\.\d+)",
}

DEFAULT_BAD_VERSIONS: frozenset[str] = frozenset({
    "V1R003C00S108",
    "V1R006C00S130",
    "V1R006C00S205",
    "V1R006C00S201",
    "V1R006C01S201",
})


def inject_crt(obj: Any) -> None:
    global _g_crt
    _g_crt = obj


class GPONConfig:
    def __init__(self, **kwargs: Any) -> None:
        self.ping_ip: str = kwargs.get("ping_ip", "1.1.1.1")
        self.bad_versions: frozenset[str] = kwargs.get("bad_versions", DEFAULT_BAD_VERSIONS)
        self.ont_rx_threshold: float = kwargs.get("ont_rx_threshold", -26.0)
        self.olt_rx_threshold: float = kwargs.get("olt_rx_threshold", -32.0)
        self.error_threshold: int = kwargs.get("error_threshold", 10000)
        self.oui_db_path: str = kwargs.get("oui_db_path", "")
        self.lan_port_restart: bool = kwargs.get("lan_port_restart", True)
        self.ping_enabled: bool = kwargs.get("ping_enabled", True)
        self.timeout: int = kwargs.get("timeout", 10)
        self.scroll_lines: int = kwargs.get("scroll_lines", 26)


class Ont:
    frame: str
    slot: str
    port: str
    ont: str
    sn: str

    def __init__(self, ont_select: Optional[List[str]] = None) -> None:
        if ont_select is None:
            buffer: str = pyperclip.paste()
            ont_select = buffer.replace("/", " ").split()
        if ont_select is None or len(ont_select) < 4:
            raise ValueError("Неверный формат GPON адреса. Нужно: frame/slot/port ont")
        self.frame = str(ont_select[0])
        self.slot = str(ont_select[1])
        self.port = str(ont_select[2])
        self.ont = str(ont_select[3])
        self.sn = str(ont_select[4]).upper() if len(ont_select) > 4 else ""

    @classmethod
    def from_address(cls, address: str) -> Ont:
        return cls(address.replace("/", " ").split())

    def __str__(self) -> str:
        return f"{self.frame}/{self.slot}/{self.port}/{self.ont}"


class GPON:
    ont: Optional[Ont]
    config: GPONConfig
    data: Dict[str, Any]
    _mac_db: Optional[Dict[str, str]]

    def __init__(self, ont: Optional[Ont] = None, config: Optional[GPONConfig] = None) -> None:
        self.ont = ont
        self.config = config or GPONConfig()
        self.data: Dict[str, Any] = {
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
            "upstream_errors": 0,
            "downstream_errors": 0,
            "lan_ports": [],
            "eth_errors": {"fcs": 0, "rx_bad": 0, "tx_bad": 0},
            "mac_devices": [],
            "ip_address": "",
            "troubleshooting": "",
        }
        self._mac_db: Optional[Dict[str, str]] = None

    # --- low-level I/O ---

    def _read_rows(self, start: int, end: int) -> str:
        scr = _g_crt.Screen
        out: str = ""
        for r in range(start, end + 1):
            try:
                line: str = scr.Get(r, 1, r, 500).strip()
                if line:
                    out += line + "\n"
            except:
                pass
        return out

    def _wait_prompt(self) -> None:
        scr = _g_crt.Screen
        for _ in range(5):
            if scr.WaitForString("#", self.config.timeout) == 0:
                continue
            _g_crt.Sleep(50)
            try:
                if scr.Get(scr.CurrentRow, 1, scr.CurrentRow, 200).strip().endswith("#"):
                    return
            except:
                pass

    def _is_real_prompt(self) -> bool:
        try:
            line: str = _g_crt.Screen.Get(_g_crt.Screen.CurrentRow, 1, _g_crt.Screen.CurrentRow, 200).strip()
            return line.endswith("#")
        except:
            return False

    def send(self, command: str, max_more: int = 0) -> str:
        scr = _g_crt.Screen
        scr.Send(command + "\r")
        output = ""
        more_count = 0
        last_row = scr.CurrentRow

        while True:
            result = scr.WaitForStrings([PRESS_Q, "#"], self.config.timeout)
            _g_crt.Sleep(100)

            chunk = self._read_rows(last_row + 1, scr.CurrentRow)
            last_row = scr.CurrentRow
            output += chunk

            if result == 0:
                break

            if result == 1:
                if max_more == -1 or more_count < max_more:
                    scr.Send(" ")
                    more_count += 1
                else:
                    scr.Send("q")
                    self._wait_prompt()
                    output += self._read_rows(last_row + 1, scr.CurrentRow)
                    break

            if result == 2:
                if not chunk:
                    continue
                if self._is_real_prompt():
                    break

        return output

    # --- parsing helpers ---

    def parse(self, output: str, pattern: str) -> Optional[str]:
        match = re.search(pattern, output)
        return match.group(1).strip() if match else None

    def parse_int(self, output: str, pattern: str) -> int:
        val = self.parse(output, pattern)
        return int(val) if val else 0

    def parse_ont(self, output: str) -> Optional[Ont]:
        fsp = re.search(r"F/S/P\s*:\s*([\d/]+)", output)
        oid = re.search(r"ONT-ID\s*:\s*(\d+)", output)
        if fsp and oid:
            parts = fsp.group(1).split("/")
            if len(parts) == 3:
                return Ont([parts[0], parts[1], parts[2], oid.group(1)])
        desc = re.search(PATTERNS["ont_by_desc"], output)
        if desc:
            return Ont(list(desc.groups()))
        return None

    def parse_lan_ports(self, output: str) -> List[Dict[str, str]]:
        return [
            {"lan_id": m.group(2), "port_type": m.group(3),
             "speed": m.group(4), "duplex": m.group(5), "link_state": m.group(6)}
            for m in re.finditer(PATTERNS["lan_ports"], output)
        ]

    def parse_mac_addresses(self, output: str) -> List[Dict[str, str]]:
        return [
            {"port_type": m.group(1), "port_number": m.group(2), "mac": m.group(3)}
            for m in re.finditer(PATTERNS["mac_entry"], output)
        ]

    # --- MAC OUI database ---

    def _load_mac_db(self) -> None:
        if self._mac_db is not None:
            return
        self._mac_db = {}
        path = self.config.oui_db_path
        if not path:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "oui.txt")
        if not os.path.exists(path):
            return
        pat = re.compile(
            r"^([\da-fA-F]{2}[-]?[\da-fA-F]{2}[-]?[\da-fA-F]{2})\s+\(hex\)\s+(.+)"
            r"|^([\da-fA-F]{6})\s+\(base 16\)\s+(.+)"
        )
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                m = pat.match(line.strip())
                if not m:
                    continue
                oui = (m.group(1) or m.group(3)).replace("-", "").upper()
                vendor = (m.group(2) or m.group(4)).strip()
                self._mac_db[oui] = vendor.split()[0] if vendor else ""

    def get_vendor(self, mac: str) -> str:
        self._load_mac_db()
        cleaned = re.sub(r"[^a-fA-F0-9]", "", mac).upper()
        return self._mac_db.get(cleaned[:6], "n/a")

    # --- ONT detection from clipboard ---

    # --- ONT detection from clipboard ---

    def detect(self, buffer: str) -> Optional[Ont]:
        buffer = buffer.strip()
        if not buffer:
            return None
        if re.fullmatch(r"(?i)(48575443|hwtc)[\da-f]{8}", buffer):
            return self.find_by_serial(buffer.upper())
        tokens = buffer.replace("/", " ").split()
        if len(tokens) == 4:
            self.ont = Ont(tokens)
            return self.ont
        if 1 <= len(buffer) <= 16:
            return self.find_by_description(buffer)
        raise ValueError(f"Не удалось распознать: {buffer}")

    def find_by_serial(self, serial: str) -> Optional[Ont]:
        cmd = COMMANDS["find_by_serial"].format(serial=serial)
        output = self.send(cmd, max_more=0)
        ont = self.parse_ont(output)
        if ont:
            self.ont = ont
        return ont

    def find_by_description(self, description: str) -> Optional[Ont]:
        cmd = COMMANDS["find_by_description"].format(description=description)
        output = self.send(cmd, max_more=0)
        ont = self.parse_ont(output)
        if ont:
            self.ont = ont
        return ont

    # --- data collection methods ---

    def get_ont_info(self) -> None:
        if not self.ont:
            return
        cmd = COMMANDS["ont_info"].format(
            frame=self.ont.frame, slot=self.ont.slot,
            port=self.ont.port, ont=self.ont.ont
        )
        output = self.send(cmd, max_more=0)
        for field in ("status", "serial", "description", "distance", "uptime", "downtime", "downcause"):
            val = self.parse(output, PATTERNS[field])
            if val:
                self.data[field] = val

    def get_version(self) -> None:
        if not self.ont:
            return
        cmd = COMMANDS["ont_version"].format(
            frame=self.ont.frame, slot=self.ont.slot,
            port=self.ont.port, ont=self.ont.ont
        )
        output = self.send(cmd, max_more=0)
        model = self.parse(output, PATTERNS["ont_model"])
        if not model:
            model = self.parse(output, PATTERNS["ont_model_alt"])
        if model:
            self.data["model"] = model
        ver = self.parse(output, PATTERNS["soft_version"])
        if ver:
            self.data["version"] = ver

    def get_optics(self) -> None:
        if not self.ont:
            return
        cmd = COMMANDS["optical_info"].format(port=self.ont.port, ont=self.ont.ont)
        output = self.send(cmd, max_more=-1)
        rx = self.parse(output, PATTERNS["ont_rx_power"])
        tx = self.parse(output, PATTERNS["olt_rx_power"])
        self.data["ont_rx_power"] = rx if rx and rx != "-" else ""
        self.data["olt_rx_power"] = tx if tx and tx != "-" else ""

    def get_line_quality(self) -> None:
        if not self.ont:
            return
        cmd = COMMANDS["ont_line_quality"].format(command="display", port=self.ont.port, ont=self.ont.ont)
        output = self.send(cmd, max_more=0)
        up = self.parse_int(output, PATTERNS["upstream_errors"])
        down = self.parse_int(output, PATTERNS["downstream_errors"])
        self.data["upstream_errors"] = up
        self.data["downstream_errors"] = down
        total = up + down
        if total:
            self.data["troubleshooting"] += f"Ошибки оптики: upstream {up}, downstream {down}. "
            cmd_clear = COMMANDS["ont_line_quality"].format(command="clear", port=self.ont.port, ont=self.ont.ont)
            self.send(cmd_clear, max_more=0)
            self.data["troubleshooting"] += "Счётчики сброшены.\n"

    def get_lan_ports(self) -> None:
        if not self.ont:
            return
        cmd = COMMANDS["eth_ports"].format(port=self.ont.port, ont=self.ont.ont)
        output = self.send(cmd, max_more=-1)
        self.data["lan_ports"] = self.parse_lan_ports(output)

    def get_eth_errors(self, lan_id: str) -> Dict[str, int]:
        if not self.ont:
            return {"fcs": 0, "rx_bad": 0, "tx_bad": 0}
        cmd = COMMANDS["eth_errors"].format(command="display", port=self.ont.port, ont=self.ont.ont, lan_id=lan_id)
        output = self.send(cmd, max_more=0)
        return {
            "fcs": self.parse_int(output, PATTERNS["fcs_errors"]),
            "rx_bad": self.parse_int(output, PATTERNS["rx_bad_bytes"]),
            "tx_bad": self.parse_int(output, PATTERNS["tx_bad_bytes"]),
        }

    def clear_eth_errors(self, lan_id: str) -> None:
        if not self.ont:
            return
        cmd = COMMANDS["eth_errors"].format(command="clear", port=self.ont.port, ont=self.ont.ont, lan_id=lan_id)
        self.send(cmd, max_more=0)

    def restart_lan_port(self, lan_id: str) -> None:
        if not self.ont:
            return
        self.send(COMMANDS["port_switch"].format(port=self.ont.port, ont=self.ont.ont, lan_id=lan_id, state="off"), 0)
        self.send(COMMANDS["port_switch"].format(port=self.ont.port, ont=self.ont.ont, lan_id=lan_id, state="on"), 0)

    def get_mac_addresses(self) -> None:
        if not self.ont:
            return
        cmd = COMMANDS["mac_addresses"].format(
            frame=self.ont.frame, slot=self.ont.slot,
            port=self.ont.port, ont=self.ont.ont
        )
        output = self.send(cmd, max_more=-1)
        self.data["mac_devices"] = self.parse_mac_addresses(output)

    def get_ipconfig(self) -> None:
        if not self.ont:
            return
        cmd = COMMANDS["ipconfig"].format(port=self.ont.port, ont=self.ont.ont)
        output = self.send(cmd, max_more=0)
        ip = self.parse(output, PATTERNS["ip_output"])
        if ip:
            self.data["ip_address"] = ip

    def ping_ont(self) -> None:
        if not self.ont or not self.config.ping_enabled:
            return
        cmd = COMMANDS["remote_ping"].format(port=self.ont.port, ont=self.ont.ont, ip=self.config.ping_ip)
        self.send(cmd, max_more=-1)

    # --- ONT deletion ---

    def delete_ont(self) -> None:
        if not self.ont:
            raise RuntimeError("ONT не задана.")
        scr = _g_crt.Screen
        scr.Send(f"{COMMANDS['undo_service_port'].format(frame=self.ont.frame, slot=self.ont.slot, port=self.ont.port, ont=self.ont.ont)}\r")
        scr.WaitForString("gemport", 5)
        scr.Send("\r")
        scr.WaitForString("(y/n)", 5)
        scr.Send("y\r")
        scr.Send(f"{COMMANDS['interface_gpon'].format(frame=self.ont.frame, slot=self.ont.slot)}\r")
        scr.Send(f"{COMMANDS['ont_delete'].format(port=self.ont.port, ont=self.ont.ont)}\r")
        scr.Send("q\r")

    # --- diagnostics orchestration ---

    def diagnose_optics_and_lan(self) -> None:
        if not self.ont:
            return
        self.send(COMMANDS["interface_gpon"].format(frame=self.ont.frame, slot=self.ont.slot), max_more=0)

        self.get_optics()
        self.get_line_quality()
        self.get_lan_ports()

        has_any_up = False
        eth_problems: List[str] = []
        for port in self.data["lan_ports"]:
            if port["link_state"] != "up":
                continue
            has_any_up = True
            if self.config.lan_port_restart:
                self.restart_lan_port(port["lan_id"])
            errors = self.get_eth_errors(port["lan_id"])
            if any(errors.values()):
                eth_problems.append(port["lan_id"])
                self.clear_eth_errors(port["lan_id"])

        if not has_any_up:
            self.data["troubleshooting"] += "Нет активных LAN-портов.\n"
        if eth_problems:
            self.data["troubleshooting"] += f"Ошибки Ethernet на портах: {', '.join(eth_problems)}. Счётчики сброшены.\n"

        self.send("quit", max_more=0)

        if self.config.ping_enabled and "310" not in self.data["model"]:
            self.get_ipconfig()
            self.ping_ont()

        self.get_mac_addresses()

    def diagnose_offline(self) -> None:
        dt: str = self.data["downtime"]
        dc: str = self.data["downcause"]
        if not any(ch.isdigit() for ch in dt):
            self.data["downtime"] = "нет данных"
            self.data["downcause"] = "нет данных" if "-" in dc else dc
            self.data["troubleshooting"] += "Запись о причине недоступности отсутствует.\n"
        elif "LOFi" in dc:
            self.data["troubleshooting"] += "Низкий/отсутствует уровень оптического сигнала.\n"
        elif "LOS" in dc:
            self.data["troubleshooting"] += "Отсутствует оптический сигнал.\n"
        elif "dying-gasp" in dc:
            self.data["troubleshooting"] += "Отключение электропитания терминала.\n"
        elif "LOKi" in dc:
            self.data["troubleshooting"] += "Пропадание сигнала от ONT.\n"

    def diagnose(self) -> str:
        if not self.ont:
            return "ONT не найдена."
        self.get_ont_info()
        if "online" not in self.data["status"].lower():
            self.diagnose_offline()
            return self._build_report_offline()
        self.get_version()
        self.diagnose_optics_and_lan()
        return self._build_report_online()

    # --- reports ---

    def _build_report_offline(self) -> str:
        lines: List[str] = [
            f"ONT = {self.ont}",
            f"Дескрипшн = {self.data['description']}",
            f"PON SN = {self.data['serial']}",
            "Терминал недоступен.",
            f"Отключён: {self.data['downtime']}",
            f"Последнее включение: {self.data['uptime']}",
            f"Расстояние (м): {self.data['distance']}",
            f"Причина: {self.data['downcause']}",
        ]
        if self.data["troubleshooting"]:
            lines.append(f"Рекомендации:\n{self.data['troubleshooting']}")
        return "\n".join(lines)

    def _build_report_online(self) -> str:
        lines: List[str] = [
            f"ONT = {self.ont}",
            f"Дескрипшн = {self.data['description']}",
            f"PON SN = {self.data['serial']}",
            "Терминал доступен.",
            f"Включён: {self.data['uptime']}",
            f"Модель: {self.data['model']}",
        ]
        ver: str = self.data["version"]
        bad: str = " !!!" if ver in self.config.bad_versions else ""
        lines.append(f"Версия ПО: '{ver}'{bad}")
        if bad:
            lines.append("(!) Требуется обновление ПО.")
        lines.append(f"Расстояние (м): {self.data['distance']}")

        rx: str = self.data["ont_rx_power"]
        tx: str = self.data["olt_rx_power"]
        lines.append(f"ONT Rx (дБм): {rx}")
        lines.append(f"OLT Rx (дБм): {tx}")
        if rx:
            try:
                if float(rx) < self.config.ont_rx_threshold:
                    lines.append("(!) Низкий уровень ONT Rx")
            except:
                pass
        if tx:
            try:
                if float(tx) < self.config.olt_rx_threshold:
                    lines.append("(!) Низкий уровень OLT Rx")
            except:
                pass

        for p in self.data["lan_ports"]:
            if p["link_state"] == "up":
                lines.append(f"LAN{p['lan_id']}: {p['port_type']} {p['speed']} Mbps {p['duplex']}")

        if self.data["ip_address"]:
            lines.append(f"IP ONT: {self.data['ip_address']}")

        seen: set[str] = set()
        for dev in self.data["mac_devices"]:
            mac: str = dev["mac"]
            if mac in seen:
                continue
            seen.add(mac)
            label: str = "LAN" if dev["port_type"] == "ETH" else dev["port_type"]
            lines.append(f"{label}{dev['port_number']} {mac} — {self.get_vendor(mac)}")

        if self.data["troubleshooting"]:
            lines.append(f"\nРекомендации:\n{self.data['troubleshooting']}")
        else:
            lines.append("\nНарушений не выявлено.")

        return "\n".join(lines)


if __name__ == "builtins":
    inject_crt(crt)
    try:
        gpon = GPON()
        gpon.send(f"scroll {gpon.config.scroll_lines}", max_more=0)
        ont = gpon.detect(pyperclip.paste().strip())
        if ont:
            gpon.get_ont_info()
            gpon.get_version()
        pyperclip.copy(
            f"ONT: {ont}\n"
            f"SN: {gpon.data['serial']}\n"
            f"Description: {gpon.data['description']}\n"
            f"Status: {gpon.data['status']}\n"
            f"Model: {gpon.data['model']}\n"
            f"Version: {gpon.data['version']}\n"
            f"Distance: {gpon.data['distance']} m\n"
            f"Uptime: {gpon.data['uptime']}\n"
            f"Downtime: {gpon.data['downtime']}\n"
            f"Down cause: {gpon.data['downcause']}"
        )
    except Exception as e:
        pyperclip.copy(f"Ошибка: {e}")
