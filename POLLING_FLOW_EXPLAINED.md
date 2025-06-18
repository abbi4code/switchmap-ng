# 🚀 Switchmap-NG Polling Flow Explained

## 📖 Overview

This document explains how switchmap-ng polls network devices and collects SNMP data, based on your questions about MIB vs OID, data flow, and system information collection.

## 🔧 Key Concepts

### **MIB vs OID**
- **OID (Object Identifier)**: Just the numeric address like `.1.3.6.1.2.1.1.1.0`
- **MIB (Management Information Base)**: Complete "dictionary" containing:
  - OIDs + human-readable names + data types + descriptions
  - Example: `sysDescr` = `.1.3.6.1.2.1.1.1.0` + "returns STRING" + "system description"

### **Device Vendor Handling**
- **Generic MIBs**: Universal for ALL devices (SNMPv2-MIB, IF-MIB, ENTITY-MIB)
- **Vendor-Specific MIBs**: Cisco/Juniper specific features in separate directories
- System data (name, description, uptime) comes from **SNMPv2-MIB** (universal standard)

## 🌊 Complete Data Flow

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────────┐
│   poll.py       │───▶│   poller.py      │───▶│   snmp_info.Query      │
│   device()      │    │   Poll.query()   │    │   everything()         │
└─────────────────┘    └──────────────────┘    └─────────────────────────┘
                                                            │
                                                            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Individual MIB Queries                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐ │
│  │   system()      │  │   layer1()      │  │   layer2() / layer3()   │ │
│  │                 │  │                 │  │                         │ │
│  │ • SNMPv2-MIB    │  │ • IF-MIB        │  │ • BRIDGE-MIB            │ │
│  │ • ENTITY-MIB    │  │ • IF-64-MIB     │  │ • CISCO-MIBs            │ │
│  │ • Vendor MIBs   │  │ • Vendor MIBs   │  │ • JUNIPER-MIBs          │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Accumulated Data Structure                           │
│  {                                                                      │
│    "misc": {...},                                                       │
│    "system": {"SNMPv2-MIB": {"sysName": {0: "device.com"}, ...}},      │
│    "layer1": {"IF-MIB": {...}},                                        │
│    "layer2": {"BRIDGE-MIB": {...}}                                     │
│  }                                                                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    device.py Processing                                 │
│  udevice.Device(snmp_data).process()                                   │
│  • Normalizes data structure                                           │
│  • Adds zone information                                               │
│  • Prepares for database insertion                                     │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Database/API Update                                  │
│  rest.post(API_POLLER_POST_URI, data, config)                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## 🖥️ System Data Collection (The Part You Asked About)

### Where System Info Comes From:
**File**: `switchmap/poller/snmp/mib/generic/mib_snmpv2.py`

**Standard OIDs polled for ALL devices**:
```python
# Universal system information OIDs
".1.3.6.1.2.1.1.1.0"  # sysDescr - Device description
".1.3.6.1.2.1.1.2.0"  # sysObjectID - Device type identifier  
".1.3.6.1.2.1.1.3.0"  # sysUpTime - Uptime in centiseconds
".1.3.6.1.2.1.1.4.0"  # sysContact - Contact information
".1.3.6.1.2.1.1.5.0"  # sysName - Device hostname/name
".1.3.6.1.2.1.1.6.0"  # sysLocation - Physical location
```

### How It Works:
1. **SNMPv2-MIB query** runs for every device (universal support)
2. **Individual OID polling**: Each OID is polled one by one with `snmp_object.get()`
3. **Data accumulation**: Results stored in nested dictionary structure
4. **Final structure**: `data["system"]["SNMPv2-MIB"]["sysName"][0] = "device.example.com"`

## 🧪 Debug Prints Added

I've added debug prints throughout the polling flow to help you visualize:

### **Files Modified**:
1. **`poll.py`** - Shows device polling progress
2. **`poller.py`** - Shows SNMP object creation
3. **`snmp_info.py`** - Shows MIB query execution
4. **`mib_snmpv2.py`** - Shows actual OID polling

### **Debug Script Created**:
- **`debug_polling_flow.py`** - Run this to see the complete flow

## 🚀 How to See It in Action

1. **Run the debug script**:
```bash
cd /home/abhishek/files/gsoc/switchmap-ng
python3 debug_polling_flow.py
```

2. **Or poll a specific device**:
```bash
# Replace 'your-device-hostname' with actual hostname from config
python3 -c "from switchmap.poller import poll; poll.cli_device('your-device-hostname')"
```

## 📊 Expected Debug Output Flow

```
🚀 [POLL.PY] Starting polling for 1 zones
📍 [POLL.PY] Zone: default has 2 hosts
🎯 [POLL.PY] Total devices to poll: 2
🔥 [POLL.PY] Starting poll for device.example.com in zone default
📡 [POLL.PY] Creating SNMP poller for device.example.com
🔧 [POLLER.PY] Initializing SNMP poller for device.example.com
🔑 [POLLER.PY] Got SNMP credentials for device.example.com: True
✅ [POLLER.PY] Creating SNMP interaction object for device.example.com
⚡ [POLL.PY] Querying SNMP data from device.example.com
📡 [POLLER.PY] Starting query for device.example.com
🔍 [POLLER.PY] Creating snmp_info.Query object for device.example.com
🚀 [POLLER.PY] Calling everything() to gather all MIB data for device.example.com
🔧 [SNMP_INFO.PY] Created Query object for device.example.com
🌟 [SNMP_INFO.PY] Starting everything() for device.example.com
🖥️  [SNMP_INFO.PY] Gathering system data for device.example.com
🖥️  [SNMP_INFO.PY] Starting system() queries for device.example.com
🔍 [SNMP_INFO.PY] Found 3 system MIB classes for device.example.com
  🧪 [SNMP_INFO.PY] Testing MIB 1/3: Snmpv2Query for device.example.com
  ✅ [SNMP_INFO.PY] MIB Snmpv2Query is SUPPORTED for device.example.com
    🖥️  [SNMPv2-MIB] Starting system data collection for device.example.com
    📡 [SNMPv2-MIB] Polling sysDescr (.1.3.6.1.2.1.1.1.0) for device.example.com
    ✅ [SNMPv2-MIB] Got sysDescr: Cisco IOS Software, Version 15.1...
    📡 [SNMPv2-MIB] Polling sysName (.1.3.6.1.2.1.1.5.0) for device.example.com
    ✅ [SNMPv2-MIB] Got sysName: device.example.com...
    📊 [SNMPv2-MIB] System data summary for device.example.com:
      - sysName: device.example.com
      - sysDescr: Cisco IOS Software, Version 15.1...
      - sysUpTime: 12345678 centiseconds
✅ [POLL.PY] Got SNMP data from device.example.com
🖥️  [POLL.PY] System Info for device.example.com:
    - Name: device.example.com
    - Description: Cisco IOS Software, Version 15.1...
    - Uptime: 12345678
🔧 [POLL.PY] Processing device data for device.example.com
🚀 [POLL.PY] Posting data to API for device.example.com
✅ [POLL.PY] Successfully posted data for device.example.com
```

## 🎯 Key Points Answered

1. **System data source**: SNMPv2-MIB with standard OIDs (same for all vendors)
2. **Not polling "one by one"**: But iterating through MIB classes, testing support, then accumulating
3. **Vendor differences**: Handled by different MIB directories (`cisco/`, `juniper/`, `generic/`)
4. **Data accumulation**: Each MIB adds to the same data structure
5. **Processing flow**: Raw SNMP → Accumulated dict → Processed dict → Database

This debug system will help you visualize exactly how your prototype differs from the production system! 