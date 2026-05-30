# GPON Diagnostics — Structure

## Flow Diagram

```
detect(buffer) ─┬─ SN (16 hex)     → find_by_serial()  → display ont info by-sn
                ├─ F/S/P ONT-ID    → Ont(tokens)        → (direct creation)
                └─ description     → find_by_description → display ont info by-desc
                                                    │
                                                    ▼
diagnose() ──── get_ont_info()  ─── display ont info F/S/P/O
                    │
                    ├── [online] ── get_version()  ─── display ont version F/S/P/O
                    │                  │
                    │                  ▼
                    │         diagnose_optics_and_lan()
                    │              │
                    │              ├─ interface gpon F/S
                    │              ├─ get_optics()              display ont optical-info P/O
                    │              ├─ get_line_quality()        display statistics ont-line-quality P/O
                    │              │                              └─ clear ... (if errors > 0)
                    │              ├─ get_lan_ports()            display ont port state P/O eth-port all
                    │              ├─ [for each UP port]:
                    │              │    ├─ restart_lan_port()    ont port attribute ... off/on
                    │              │    ├─ get_eth_errors()      display statistics ont-eth P/O ont-port N
                    │              │    └─ clear_eth_errors()    (if errors > 0)
                    │              ├─ quit
                    │              ├─ get_ipconfig()             display ont ipconfig P/O
                    │              ├─ ping_ont()                 ont remote-ping P/O ip-address X.X.X.X
                    │              └─ get_mac_addresses()        display mac-address ont F/S/P O
                    │
                    ├── [offline] ── diagnose_offline()  ── analyze downcause (LOFi/LOS/dying-gasp/LOKi)
                    │
                    └── _build_report_online() / _build_report_offline()
                         └── pyperclip.copy(result)
```

## Commands (COMMANDS dict)

| Key | Huawei CLI Command | Purpose |
|-----|-------------------|---------|
| `ont_info` | `display ont info {f} {s} {p} {ont}` | Basic ONT info |
| `ont_version` | `display ont version {f} {s} {p} {ont}` | Firmware version & model |
| `optical_info` | `display ont optical-info {p} {ont}` | Optical power levels |
| `ont_line_quality` | `{cmd} statistics ont-line-quality {p} {ont}` | Line quality (display/clear) |
| `eth_ports` | `display ont port state {p} {ont} eth-port all` | LAN port states |
| `eth_errors` | `{cmd} statistics ont-eth {p} {ont} ont-port {lan_id}` | Ethernet errors (display/clear) |
| `port_switch` | `ont port attribute {p} {ont} eth {lan_id} operational-state {state}` | Enable/disable LAN port |
| `remote_ping` | `ont remote-ping {p} {ont} ip-address {ip}` | Ping from OLT to ONT |
| `ipconfig` | `display ont ipconfig {p} {ont}` | ONT IP address |
| `find_by_serial` | `display ont info by-sn {serial}` | Find ONT by serial number |
| `find_by_description` | `display ont info by-desc {desc}` | Find ONT by description |
| `mac_addresses` | `display mac-address ont {f}/{s}/{p} {ont}` | MAC addresses behind ONT |
| `undo_service_port` | `undo service-port port {f}/{s}/{p} ont {ont}` | Remove service-port |
| `ont_delete` | `ont delete {p} {ont}` | Delete ONT |
| `interface_gpon` | `interface gpon {f}/{s}` | Enter GPON interface mode |

## Patterns (PATTERNS dict)

| Key | Regex | Field |
|-----|-------|-------|
| `status` | `Run state\s*:\s*(.+)` | ONT status (online/offline) |
| `serial` | `(?i)SN\s*:\s*([\da-fA-F]{16})` | Serial number (16 hex) |
| `description` | `Description\s*:\s*(.+)` | ONT description |
| `distance` | `ONT distance\(m\)\s*:\s*(\d+)` | Distance in meters |
| `uptime` | `Last up time\s*:\s*([\d-]+\s[\d:+-]+)` | Last up time |
| `downtime` | `Last down time\s*:\s*([\d-]+\s[\d:+-]+)` | Last down time |
| `downcause` | `Last down cause\s*:\s*(\S+)` | Last down cause |
| `ont_model` | `ONT Type\s*:\s*(.+)` | ONT model (primary) |
| `ont_model_alt` | `Equipment-ID\s*:\s*(\w+)` | ONT model (fallback) |
| `soft_version` | `Main Software Version\s*:\s*(\S+)` | Software version |
| `ont_rx_power` | `Rx optical power\(dBm\)\s*:\s*(-?\d+\.?\d*)` | ONT Rx power (dBm) |
| `olt_rx_power` | `OLT Rx ONT optical power\(dBm\)\s*:\s*(-?\d+\.?\d*)` | OLT Rx power (dBm) |
| `upstream_errors` | `Upstream frame BIP error count\s*:\s*(\d+)` | Upstream BIP errors |
| `downstream_errors` | `Downstream frame BIP error count\s*:\s*(\d+)` | Downstream BIP errors |
| `lan_ports` | `(\d+)\s+(\d+)\s+(GE\|FE)\s+(\d+\|-)+\s+(full\|half\|-)\s+(up\|down)` | LAN port states |
| `fcs_errors` | `Received FCS error frames\s*:\s*(\d+)` | FCS errors |
| `rx_bad_bytes` | `Received bad bytes\s*:\s*(\d+)` | Bad receive bytes |
| `tx_bad_bytes` | `Sent bad bytes\s*:\s*(\d+)` | Bad transmit bytes |
| `mac_entry` | `(ETH\|WLAN)\s+(\d)+\s+([\da-fA-F]{4}-[\da-fA-F]{4}-[\da-fA-F]{4})` | MAC address entry |
| `ont_by_sn` | `F/S/P\s*:\s*(\d+)/(\d+)/(\d+).*ONT-ID\s*:\s*(\d+)` | ONT address from SN search |
| `ont_by_desc` | `(\d+)/\s*(\d+)/\s*(\d+)\s+(\d+)` | ONT address from description |
| `ip_output` | `IP address\s*:\s*(\d+\.\d+\.\d+\.\d+)` | ONT IP address |

## Data Structure (self.data)

```python
self.data = {
    "status": "",              # Run state (online/offline)
    "serial": "",              # PON SN (16 hex)
    "description": "",         # Description
    "model": "",               # ONT model
    "version": "",             # Software version
    "distance": "",            # Distance in meters
    "uptime": "",              # Last up time
    "downtime": "",            # Last down time
    "downcause": "",           # Last down cause
    "ont_rx_power": "",        # Rx optical power (dBm)
    "olt_rx_power": "",        # OLT Rx ONT power (dBm)
    "upstream_errors": 0,      # Upstream BIP errors
    "downstream_errors": 0,    # Downstream BIP errors
    "lan_ports": [],           # List[Dict] of LAN port states
    "eth_errors": {"fcs": 0, "rx_bad": 0, "tx_bad": 0},
    "mac_devices": [],         # List[Dict] of MAC addresses
    "ip_address": "",          # ONT IP address
    "troubleshooting": "",     # Accumulated recommendations
}
```

## GPONConfig Defaults

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `ping_ip` | `1.1.1.1` | IP for remote ping |
| `bad_versions` | `frozenset({...})` | 5 problematic firmware versions |
| `ont_rx_threshold` | `-26.0` | ONT Rx warning threshold (dBm) |
| `olt_rx_threshold` | `-32.0` | OLT Rx warning threshold (dBm) |
| `error_threshold` | `10000` | Error count threshold |
| `oui_db_path` | `""` | OUI database path |
| `lan_port_restart` | `True` | Restart LAN ports during diag |
| `ping_enabled` | `True` | Perform remote ping |
| `timeout` | `10` | Screen wait timeout (sec) |
| `scroll_lines` | `26` | Lines per page scroll |

## Diagnostic Steps Detail

### detect(buffer)
1. Check clipboard (`pyperclip.paste()`)
2. Match SN (16 hex, starts with `48575443`/HWTC) → `find_by_serial()`
3. Match 4 tokens (F/S/P ONT-ID) → create `Ont` directly
4. Match 1-16 chars (description) → `find_by_description()`

### get_ont_info()
- Command: `display ont info {f} {s} {p} {ont}`
- max_more: `0` (first page + q)
- Parses: status, serial, description, distance, uptime, downtime, downcause
- If not online → `diagnose_offline()` + `_build_report_offline()`

### get_version()
- Command: `display ont version {f} {s} {p} {ont}`
- max_more: `0`
- Parses: model (ONT Type → Equipment-ID fallback), version

### get_optics()
- Command: `display ont optical-info {p} {ont}`
- max_more: `-1` (scroll all)
- Parses: ont_rx_power, olt_rx_power

### get_line_quality()
- Command: `display statistics ont-line-quality {p} {ont}`
- max_more: `0`
- Parses: upstream_errors, downstream_errors
- If errors > 0 → add to troubleshooting + clear counters

### get_lan_ports()
- Command: `display ont port state {p} {ont} eth-port all`
- max_more: `-1`
- Parses: List[{lan_id, port_type, speed, duplex, link_state}]

### Per active LAN port
1. `restart_lan_port(lan_id)` — if `config.lan_port_restart`
2. `get_eth_errors(lan_id)` — `display statistics ont-eth {p} {ont} ont-port {lan_id}`
3. Parses: fcs_errors, rx_bad_bytes, tx_bad_bytes
4. If errors > 0 → add to eth_problems list + clear counters

### get_ipconfig()
- Condition: `config.ping_enabled AND "310" not in model`
- Command: `display ont ipconfig {p} {ont}`
- max_more: `0`
- Parses: ip_address

### ping_ont()
- Condition: same as get_ipconfig()
- Command: `ont remote-ping {p} {ont} ip-address {config.ping_ip}`
- max_more: `-1` (visual only, no parsing)

### get_mac_addresses()
- Command: `display mac-address ont {f}/{s}/{p} {ont}`
- max_more: `-1`
- Parses: List[{port_type, port_number, mac}]

### diagnose_offline()
- Analyzes downcause:
  - `LOFi` → low/absent optical signal
  - `LOS` → no optical signal
  - `dying-gasp` → power loss
  - `LOKi` → signal loss from ONT
  - No digits in downtime → "no record available"

### _build_report_online()
Formatted output: ONT address → description → SN → status → uptime → model → version → distance → optics → LAN ports → IP → MACs → recommendations

### _build_report_offline()
Formatted output: ONT address → description → SN → offline status → downtime → uptime → distance → downcause → recommendations

## Key Files

| File | Role |
|------|------|
| `GPON_HW/GPON_class.py` | Core: Ont, GPON, GPONConfig, COMMANDS, PATTERNS |
| `GPON_HW/GPON_autodiagnostic_test.vbs` | SecureCRT entry point for full diag |
| `GPON_HW/GPON_HW_full_diag.vbs` | Legacy VBScript direct commands |
| `GPON_HW/qtMain_complete.py` | PyQt6 GUI (calls GPON.diagnose()) |
| `GPON_HW/test_gpont_integration.py` | Integration tests |
| `HUAWEI.md` | Huawei GPON CLI reference |
| `SECURECRT.md` | SecureCRT scripting rules |
