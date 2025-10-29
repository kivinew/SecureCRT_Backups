# commands.py
# модуль для скрипта GPON_auto_diagnostic.vbs
# содержит команды головной станции Huawei

COMMANDS = {
    'ont_info': "display ont info {frame} {slot} {port} {ont}",
    'info_by_serial': "display ont info by-sn {serial}",
    'info_by_description': "display ont info by-desc {description}",
    'ont_version': "display ont version {frame} {slot} {port} {ont}",
    'optical_info': "display ont optical-info {port} {ont}",
    'ont_line_quality': "{command} statistics ont-line-quality {port} {ont}",
    'eth_ports': "display ont port state {port} {ont} eth-port all",
    'eth_errors': "{command} statistics ont-eth {port} {ont} ont-port {lan_id}",
    'port_off': "ont port attribute {port} {ont} eth {lan_id} operational-state {state}",
    'remote_ping': "ont remote-ping {port} {ont} ip-address {ip}"
}
