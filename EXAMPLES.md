# Examples: Cisco Configuration Generator

This file provides example inputs and their expected outputs.

---

## Example 1: Initial Configuration Only

**Menu option:** 1 - Generate initial configuration

**Input:**
```
1
SW-CORE
C1sco123
99
192.168.10.1
255.255.255.0
192.168.10.254
example.com
admin
AdminPass123
y
Authorized access only
8.8.8.8
192.168.10.250
4
0
```

**Generated output:**
```
============================================================
Cisco Switch Configuration - Initial Device Configuration
============================================================

hostname SW-CORE

enable secret C1sco123

vlan 99
 name MGMT
!

interface vlan 99
 ip address 192.168.10.1 255.255.255.0
 no shutdown
!

ip route 0.0.0.0 0.0.0.0 192.168.10.254
ip domain name example.com
username admin privilege 15 secret AdminPass123
banner motd ^Authorized access only^
line vty 0 4
 transport input ssh
!
!

! --- Verification Commands ---
show running-config
show ip interface brief

============================================================
END OF CONFIGURATION
============================================================
```

---

## Example 2: VLAN Configuration

**Menu option:** 2 - Configure VLANs

**Input:**
```
2
10
USERS
20
SERVERS
30
PRINTERS
99
MANAGEMENT
4
0
```

**Generated output:**
```
============================================================
Cisco Switch Configuration - VLAN Configuration
============================================================

! VLAN definitions
vlan 10
 name USERS
!
vlan 20
 name SERVERS
!
vlan 30
 name PRINTERS
!
vlan 99
 name MANAGEMENT
!

! --- Verification Commands ---
show vlan brief
show running-config

============================================================
END OF CONFIGURATION
============================================================
```

---

## Example 3: Access Port Configuration

**Menu option:** 3 - Configure access ports

**Input:**
```
3
GigabitEthernet1/0/1-12
10
USER_ACCESS_PORTS
y
y
4
0
```

**Generated output:**
```
============================================================
Cisco Switch Configuration - Access-Port Configuration
============================================================

interface GigabitEthernet1/0/1
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
 description USER_ACCESS_PORTS
!
interface GigabitEthernet1/0/2
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
 description USER_ACCESS_PORTS
!
interface GigabitEthernet1/0/3
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
 description USER_ACCESS_PORTS
!
interface GigabitEthernet1/0/4
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
 description USER_ACCESS_PORTS
!
interface GigabitEthernet1/0/5
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
 description USER_ACCESS_PORTS
!
interface GigabitEthernet1/0/6
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
 description USER_ACCESS_PORTS
!
interface GigabitEthernet1/0/7
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
 description USER_ACCESS_PORTS
!
interface GigabitEthernet1/0/8
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
 description USER_ACCESS_PORTS
!
interface GigabitEthernet1/0/9
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
 description USER_ACCESS_PORTS
!
interface GigabitEthernet1/0/10
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
 description USER_ACCESS_PORTS
!
interface GigabitEthernet1/0/11
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
 description USER_ACCESS_PORTS
!
interface GigabitEthernet1/0/12
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
 description USER_ACCESS_PORTS
!

! --- Verification Commands ---
show interfaces status
show interfaces switchport
show running-config

============================================================
END OF CONFIGURATION
============================================================
```

---

## Example 4: Trunk Port Configuration

**Menu option:** 4 - Configure trunk ports

**Input:**
```
4
GigabitEthernet1/0/23-24
SWITCH_UPLINKS
10,20,30,99
99
4
0
```

**Generated output:**
```
============================================================
Cisco Switch Configuration - Trunk-Port Configuration
============================================================

interface GigabitEthernet1/0/23
 description SWITCH_UPLINKS
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,99
 switchport trunk native vlan 99
!
interface GigabitEthernet1/0/24
 description SWITCH_UPLINKS
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,99
 switchport trunk native vlan 99
!

! --- Verification Commands ---
show interfaces trunk
show interfaces switchport
show running-config

============================================================
END OF CONFIGURATION
============================================================
```

---

## Example 5: Complete Switch Configuration

**Menu option:** 5 - Generate complete switch configuration

**Input (abridged, shown conceptually):**
1. Initial config (SW-CORE, enable secret optional/blank or set, mgmt vlan 99, mgmt IP, gateway, domain example.com, admin/adminpass, SSH enabled, banner, DNS/NTP optional)
2. VLANs: 10/USERS, 20/SERVERS, 99/MANAGEMENT
3. Access ports: GigabitEthernet1/0/1-8 on VLAN 10 with PortFast + BPDU Guard
4. Trunk ports: GigabitEthernet1/0/23-24 allowed 10,20,99 native 99
5. Save/display/return (option 4)

**Note:** When running interactively, the tool prompts you step-by-step through all sections. See the README for the full interactive flow.

---

**Tip:** You can pipe these inputs to the script for automated testing (as shown), or run interactively with `python3 ciscoconfig.py`.
