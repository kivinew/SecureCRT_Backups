# $language = "Python3"
# $interface = "1.0"

import pyperclip

# Глобальный объект crt будет внедрён из основного скрипта
crt = None

def inject_crt(obj):
    """Вызывается из основного скрипта: inject_crt(crt)."""
    global crt
    crt = obj

COMMANDS = {
    "ont_info": "display ont info {frame} {slot} {port} {ont}",
    "info_by_serial": "display ont info by-sn {serial}",
    "info_by_description": "display ont info by-desc {description}",
    "ont_version": "display ont version {frame} {slot} {port} {ont}",
    "optical_info": "display ont optical-info {port} {ont}",
    "ont_line_quality": "{command} statistics ont-line-quality {port} {ont}",
    "eth_ports": "display ont port state {port} {ont} eth-port all",
    "eth_errors": "{command} statistics ont-eth {port} {ont} ont-port {lan_id}",
    "port_switch": "ont port attribute {port} {ont} eth {lan_id} operational-state {state}",
    "remote_ping": "ont remote-ping {port} {ont} ip-address {ip}",
    "mac_table": "display mac-address ont {frame}/{slot}/{port} {ont}",
    "iface_gpon": "interface gpon {frame}/{slot}",
    "undo_service_port": "undo service-port port {frame}/{slot}/{port} ont {ont}",
    "ont_delete": "ont delete {port} {ont}",
}

class Ont:
    """Обёртка над ONT: хранит F/S/P/ONT и даёт методы опроса/управления."""

    def __init__(self, frame, slot, port, ont, sn=""):
        if crt is None:
            raise RuntimeError("CRT не инициализирован. Сначала вызови inject_crt(crt).")
        self.frame = str(frame)
        self.slot = str(slot)
        self.port = str(port)
        self.ont = str(ont)
        self.sn = sn

    # ---------- фабрики ----------

    @classmethod
    def from_fspo(cls, frame, slot, port, ont, sn=""):
        return cls(frame, slot, port, ont, sn=sn)

    @classmethod
    def from_clipboard(cls):
        mem = pyperclip.paste().strip()
        parts = mem.replace("/", " ").split()
        if len(parts) < 4:
            raise ValueError("В буфере нет F/S/P/ONT (ожидается 4 значения).")
        return cls(*parts[:4], sn=parts[4] if len(parts) > 4 else "")

    # (по-хорошему сюда можно ещё from_serial / from_description,
    #  но т.к. логика поиска уже есть в твоём detect_ont, оставим её во втором модуле.)

    # ---------- низкоуровневые помощники ----------

    def _send(self, cmd: str, delay_ms: int = 200):
        scr = crt.Screen
        scr.Send(cmd + "\r")
        crt.Sleep(delay_ms)

    def _read_all(self, timeout: int = 1) -> str:
        scr = crt.Screen
        out = ""
        while True:
            line = scr.ReadString("\n", timeout)
            if not line:
                break
            out += line
        return out

    def _send_and_read(self, cmd: str, delay_ms: int = 200) -> str:
        self._send(cmd, delay_ms)
        return self._read_all()

    # ---------- высокоуровневые методы опроса ----------

    def get_info(self) -> str:
        cmd = COMMANDS["ont_info"].format(
            frame=self.frame, slot=self.slot, port=self.port, ont=self.ont
        )
        return self._send_and_read(cmd)

    def get_version(self) -> str:
        cmd = COMMANDS["ont_version"].format(
            frame=self.frame, slot=self.slot, port=self.port, ont=self.ont
        )
        return self._send_and_read(cmd)

    def get_optical_info(self) -> str:
        self._send(COMMANDS["iface_gpon"].format(frame=self.frame, slot=self.slot))
        out = self._send_and_read(
            COMMANDS["optical_info"].format(port=self.port, ont=self.ont)
        )
        self._send("quit")
        return out

    def get_line_quality(self, clear: bool = False) -> str:
        cmd = COMMANDS["ont_line_quality"].format(
            command="clear" if clear else "display",
            port=self.port,
            ont=self.ont,
        )
        return self._send_and_read(cmd)

    def get_eth_ports(self) -> str:
        cmd = COMMANDS["eth_ports"].format(port=self.port, ont=self.ont)
        return self._send_and_read(cmd)

    def switch_port(self, lan_id: int, state: str):
        cmd = COMMANDS["port_switch"].format(
            port=self.port, ont=self.ont, lan_id=lan_id, state=state
        )
        self._send(cmd)

    def get_eth_errors(self, lan_id: int, clear: bool = False) -> str:
        cmd = COMMANDS["eth_errors"].format(
            command="clear" if clear else "display",
            port=self.port,
            ont=self.ont,
            lan_id=lan_id,
        )
        return self._send_and_read(cmd)

    def get_mac_table(self) -> str:
        cmd = COMMANDS["mac_table"].format(
            frame=self.frame, slot=self.slot, port=self.port, ont=self.ont
        )
        return self._send_and_read(cmd)

    def remote_ping(self, ip: str) -> str:
        cmd = COMMANDS["remote_ping"].format(port=self.port, ont=self.ont, ip=ip)
        return self._send_and_read(cmd)

    # ---------- управление ----------

    def delete(self):
        scr = crt.Screen
        # удаление service-port
        scr.Send(
            COMMANDS["undo_service_port"].format(
                frame=self.frame, slot=self.slot, port=self.port, ont=self.ont
            )
            + "\r"
        )
        scr.WaitForString("gemport", 5)
        scr.Send("\r")
        scr.WaitForString("(y/n)", 5)
        scr.Send("y\r")
        # удаление ONT
        scr.Send(COMMANDS["iface_gpon"].format(frame=self.frame, slot=self.slot) + "\r")
        scr.Send(COMMANDS["ont_delete"].format(port=self.port, ont=self.ont) + "\r")
        scr.Send("q\r")