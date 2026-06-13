# SecureCRT Automation Scripts Collection

## Overview

This repository contains a collection of automation scripts designed for network equipment management using SecureCRT. The scripts primarily focus on GPON (Gigabit Passive Optical Network) hardware management, diagnostics, and configuration, but also include tools for other network equipment vendors.

## Contents

### VBS Scripts (SecureCRT Automation)
The majority of scripts are VBS files designed to run within SecureCRT for automating telnet/SSH sessions with network equipment:

- **GPON_HW/** - Core GPON hardware management scripts:
  - `GPON_delete_ont.vbs` - Delete ONT (Optical Network Terminal) configurations
  - `GPON_find_MAC.vbs` - Find MAC addresses on GPON equipment
  - `GPON_OOP_set_serial.vbs` - Set serial numbers using OOP approach
  - `GPON_OOP_optic.vbs` - Manage optical parameters
  - `GPON_autodiagnostic_test.vbs` - Run automated diagnostics
  - `GPON_IP_config.vbs` - Configure IP settings
  - `GPON_wan_info.vbs` - Retrieve WAN information
  - And many others for specific GPON operations

- **BDCOM/** - BDCOM equipment specific scripts
- **Juniper/** - Juniper equipment scripts
- **General utilities** - MAC address discovery, configuration enabling, etc.

### Python Scripts
- `ONT_SPLIT.py` - Process ONT information from log files
- `GPON_info_by_description.py` - Retrieve GPON info by description
- `GPON_info_by_SN.py` - Retrieve GPON info by serial number
- `tpconf_bin_xml.py` - TP-Link configuration binary/XML converter
- `qtMain.py` - Simple Qt GUI application template

### Supporting Files
- `oui.txt` - IEEE OUI (Organizationally Unique Identifier) database for MAC address vendor lookup
- `GPON_DIAG_STRUCT.md` - Documentation of GPON diagnostic structures
- `README.md` - Brief repository overview
- `LICENSE` - MIT license

## Key Features

1. **Automated Equipment Management** - Scripts automate repetitive tasks like ONT provisioning, deletion, and diagnostics
2. **Vendor Support** - Primary focus on GPON equipment with additional support for BDCOM, Juniper, and others
3. **Diagnostic Capabilities** - Comprehensive diagnostic scripts for optical parameters, WAN status, and equipment health
4. **Configuration Management** - Scripts for IP configuration, VLAN settings, and service provisioning
5. **MAC Address Utilities** - Tools for discovering and working with MAC addresses on network equipment

## Usage

### VBS Scripts
Most VBS scripts are designed to run within SecureCRT:
1. Open SecureCRT
2. Establish a connection to your network equipment
3. Navigate to Scripts -> Run...
4. Select the desired VBS script
5. Follow any on-screen prompts (scripts often require copying specific parameters like MAC addresses)

### Python Scripts
Python scripts can be run directly:
```bash
python ONT_SPLIT.py
python GPON_info_by_description.py
```

## Dependencies

- **SecureCRT** - Required for VBS script execution
- **Python 3.x** - Required for Python scripts
- **PyQt6** - Required for `qtMain.py` GUI application
- **Network Access** - Telnet/SSH access to target network equipment

## Script Conventions

Many scripts include common header comments:
```
# Обязательная часть для работы с подключаемым модулем GPON_class
# Основной цикл работы SecureCRT-скрипта.
```

These indicate dependencies on shared modules like `GPON_class` or `GPON_class_new.py`.

## oui.txt Database

The `oui.txt` file contains MAC address vendor information that can be used to identify equipment manufacturers from MAC addresses. It includes many robotics and automation companies, suggesting the collection may have been used in environments with automated equipment or robotics networks.

## Maintenance

This collection appears to be actively maintained with:
- Regular updates to diagnostic scripts
- Both legacy (`GPON_class.py`) and new (`GPON_class_new.py`) implementations
- Mixed VBS and Python implementations for different use cases

## Security Note

As with any network automation tools, ensure proper authorization before running these scripts on production network equipment.