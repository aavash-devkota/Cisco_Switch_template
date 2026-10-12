#!/usr/bin/env python3
"""
Cisco Configuration Generator
A simple interactive CLI tool to generate Cisco switch configuration commands.
Uses Python 3 standard library only.
"""

import re
import os
import sys


def main():
    """Display main menu and dispatch to configuration modules."""
    config = {
        "hostname": "SWITCH",
        "enable_secret": None,
        "mgmt_vlan": None,
        "mgmt_ip": None,
        "mgmt_mask": None,
        "gateway": None,
        "domain_name": None,
        "username": None,
        "password": None,
        "ssh": False,
        "banner": None,
        "dns": None,
        "ntp": None,
        "vlans": [],
        "access_ports": [],
        "trunk_ports": [],
    }

    while True:
        print("\nCisco Configuration Generator")
        print("-----------------------------")
        print("1. Generate initial configuration")
        print("2. Configure VLANs")
        print("3. Configure access ports")
        print("4. Configure trunk ports")
        print("5. Generate complete switch configuration")
        print("0. Exit")

        choice = input("\nEnter choice (0-5): ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        elif choice == "1":
            config = get_initial_config(config)
            handle_output(generate_config("initial", config))
        elif choice == "2":
            config["vlans"] = get_vlans(config.get("vlans", []))
            handle_output(generate_config("vlans", config))
        elif choice == "3":
            config["access_ports"] = get_access_ports(config.get("access_ports", []))
            handle_output(generate_config("access", config))
        elif choice == "4":
            config["trunk_ports"] = get_trunk_ports(config.get("trunk_ports", []), config.get("access_ports", []))
            handle_output(generate_config("trunk", config))
        elif choice == "5":
            # Collect everything in one session, in a sensible order.
            config = get_initial_config(config)
            config["vlans"] = get_vlans(config.get("vlans", []))
            config["access_ports"] = get_access_ports(config.get("access_ports", []))
            config["trunk_ports"] = get_trunk_ports(
                config.get("trunk_ports", []), config.get("access_ports", [])
            )
            handle_output(generate_config("complete", config))
        else:
            print("Invalid choice. Please enter 0-5.")


def get_initial_config(config):
    """Collect initial device settings interactively."""
    print("\n--- Initial Configuration ---")

    # Hostname
    hostname = input("Enter hostname [default-SWITCH]: ").strip()
    if hostname:
        config["hostname"] = sanitize_string(hostname, max_len=64)
    else:
        config["hostname"] = "SWITCH"

    # Enable secret
    print("Enable secret (optional, leave blank for none):")
    secret = input("> ").strip()
    if secret:
        config["enable_secret"] = secret

    # Management VLAN
    while True:
        vlan_str = input("Management VLAN ID (e.g., 99, or blank to skip): ").strip()
        if not vlan_str:
            config["mgmt_vlan"] = None
            break
        if validate_vlan(vlan_str):
            config["mgmt_vlan"] = int(vlan_str)
            break
        print("Invalid VLAN ID. Must be 1-4094.")

    # Management IP and subnet mask
    while True:
        mgmt_ip = input("Management IP address (e.g., 192.168.1.1, or blank to skip): ").strip()
        if not mgmt_ip:
            config["mgmt_ip"] = None
            break
        if validate_ipv4(mgmt_ip):
            config["mgmt_ip"] = mgmt_ip
            break
        print("Invalid IPv4 address.")

    while True:
        mgmt_mask = input("Subnet mask (e.g., 255.255.255.0, or blank to skip): ").strip()
        if not mgmt_mask:
            config["mgmt_mask"] = None
            break
        if validate_ipv4(mgmt_mask):
            config["mgmt_mask"] = mgmt_mask
            break
        print("Invalid subnet mask IPv4 address.")

    # Default gateway
    while True:
        gateway = input("Default gateway (e.g., 192.168.1.254, or blank to skip): ").strip()
        if not gateway:
            config["gateway"] = None
            break
        if validate_ipv4(gateway):
            config["gateway"] = gateway
            break
        print("Invalid IPv4 address.")

    # Domain name
    print("Domain name (optional, leave blank to skip):")
    domain = input("> ").strip()
    if domain:
        config["domain_name"] = sanitize_string(domain, max_len=64)

    # Local administrator username and password, optionally
    print("Local administrator (optional, leave username blank to skip):")
    username = input("Username: ").strip()
    if username:
        config["username"] = sanitize_string(username, max_len=32)
        print("Password (leave blank for no password):")
        pwd = input("> ").strip()
        if pwd:
            config["password"] = pwd
        else:
            config["password"] = None
    else:
        config["username"] = None
        config["password"] = None

    # SSH configuration
    print("SSH configuration (optional):")
    ssh_input = input("Enable SSH? (y/n, default n): ").strip().lower()
    if ssh_input in ("y", "yes"):
        config["ssh"] = True

    # Login banner, optionally
    print("Login banner (optional, leave blank to skip):")
    banner = input("> ").strip()
    if banner:
        config["banner"] = sanitize_string(banner, max_len=128)

    # DNS and NTP servers, optionally
    print("DNS server (optional, leave blank to skip):")
    dns = input("> ").strip()
    if dns:
        if validate_ipv4(dns):
            config["dns"] = dns
        else:
            print("Warning: DNS IP appears invalid, skipping.")

    print("NTP server (optional, leave blank to skip):")
    ntp = input("> ").strip()
    if ntp:
        if validate_ipv4(ntp):
            config["ntp"] = ntp
        else:
            print("Warning: NTP IP appears invalid, skipping.")

    print("\nGenerated configuration may contain sensitive credentials.")
    print("Do not share or store publicly.\n")
    return config


def get_vlans(existing_vlans):
    """Allow users to define multiple VLANs in one session."""
    print("\n--- VLAN Configuration ---")
    print("Enter VLANs one at a time.")
    print("Leave VLAN ID blank to finish.")

    vlans = list(existing_vlans)

    while True:
        vlan_id_str = input("VLAN ID (or blank to finish): ").strip()
        if not vlan_id_str:
            break
        if not validate_vlan(vlan_id_str):
            print("Invalid VLAN ID. Must be an integer 1-4094.")
            continue
        vlan_id = int(vlan_id_str)
        # Reject duplicates
        if any(v["id"] == vlan_id for v in vlans):
            print(f"VLAN {vlan_id} already defined. Use a different ID.")
            continue
        # VLAN name with safety checks
        while True:
            name = input("VLAN name (e.g., USERS): ").strip()
            if not name:
                print("VLAN name cannot be blank. Try again.")
                continue
            # Sanitize: allow alphanumeric, spaces, dashes, underscores only
            name = re.sub(r"[^a-zA-Z0-9 _-]", "", name)
            name = name.strip()
            if not name:
                print("Name became empty after sanitization. Try a different name.")
                continue
            # Check for command injection patterns
            if re.search(r"[\(\);`|&]", name):
                print("Warning: Unsafe characters removed from VLAN name.")
                name = re.sub(r"[\(\);`|&]", "", name)
            break
        vlans.append({"id": vlan_id, "name": name})
        print(f"  Added VLAN {vlan_id} named '{name}'")

    return vlans


def get_access_ports(existing_aps):
    """Configure access ports with optional PortFast and BPDU Guard."""
    print("\n--- Access-Port Configuration ---")
    print("Interface selection examples:")
    print("  GigabitEthernet1/0/1")
    print("  GigabitEthernet1/0/1-12")
    print("  GigabitEthernet1/0/1-8,15")

    if existing_aps:
        print("Existing access port assignments:")
        for ap in existing_aps:
            print(f"  {ap['interface']} (VLAN {ap['vlan']})")

    while True:
        iface = input("\nInterface selection (or blank to finish): ").strip()
        if not iface:
            break
        # Parse interface using simple parser
        interfaces = parse_interfaces_simple(iface)
        if not interfaces:
            print("Invalid interface format. Try as shown above.")
            continue
        # Check for duplicates/overlaps with existing access ports
        for intf in interfaces:
            for existing in existing_aps:
                if intf == existing["interface"]:
                    print(f"Warning: {intf} already configured as access port. Skipping.")
        # Access VLAN
        while True:
            vlan_str = input("Access VLAN ID (1-4094): ").strip()
            if not vlan_str:
                print("Access VLAN is required.")
                continue
            if validate_vlan(vlan_str):
                access_vlan = int(vlan_str)
                break
            print("Invalid VLAN ID.")
        # Optional description
        print("Interface description (optional, leave blank for default):")
        desc = input("> ").strip()
        if desc:
            desc = sanitize_string(desc, max_len=64)
        else:
            desc = None
        # PortFast
        pfs_input = input("Enable PortFast? (y/n, default n): ").strip().lower()
        portfast = pfs_input in ("y", "yes")
        # BPDU Guard
        bpdu_input = input("Enable BPDU Guard? (y/n, default n): ").strip().lower()
        bpdu_guard = bpdu_input in ("y", "yes")

        # Explain intent
        if portfast or bpdu_guard:
            print("  Note: PortFast and BPDU Guard are intended for edge/end-user ports,")
            print("  not indiscriminately for network uplinks/trunks.")

        for intf in interfaces:
            existing_aps.append({
                "interface": intf,
                "vlan": access_vlan,
                "description": desc,
                "portfast": portfast,
                "bpdu_guard": bpdu_guard,
            })

        print(f"  Added access port(s): {', '.join(interfaces)} VLAN {access_vlan}")

    return existing_aps


def get_trunk_ports(existing_tps, existing_aps=None):
    """Configure trunk ports with allowed VLANs and native VLAN."""
    if existing_aps is None:
        existing_aps = []
    print("\n--- Trunk-Port Configuration ---")
    print("Interface selection examples:")
    print("  GigabitEthernet1/0/23-24")
    print("  GigabitEthernet1/0/1")

    if existing_tps:
        print("Existing trunk port assignments:")
        for tp in existing_tps:
            print(f"  {tp['interface']} (allowed VLANs: {tp['allowed_vlan']})")

    while True:
        iface = input("\nInterface selection (or blank to finish): ").strip()
        if not iface:
            break
        interfaces = parse_interfaces_simple(iface)
        if not interfaces:
            print("Invalid interface format.")
            continue
        # Check for duplicates/overlaps with existing ports
        all_assigned = set()
        for ap in existing_aps:
            all_assigned.add(ap["interface"])
        for tp in existing_tps:
            all_assigned.add(tp["interface"])
        for intf in interfaces:
            if intf in all_assigned:
                print(f"Warning: {intf} already assigned (access or trunk).")

        # Description
        print("Description (optional, leave blank):")
        desc = input("> ").strip()
        if desc:
            desc = sanitize_string(desc, max_len=64)
        else:
            desc = None
        # Allowed VLANs
        while True:
            allowed_str = input("Allowed VLAN IDs (comma-separated, e.g., 10,20,30): ").strip()
            if not allowed_str:
                print("Allowed VLANs are required.")
                continue
            vlan_ids = []
            valid = True
            for part in allowed_str.split(","):
                part = part.strip()
                if validate_vlan(part):
                    vlan_ids.append(int(part))
                else:
                    print(f"Invalid VLAN ID in '{part}', please re-enter.")
                    valid = False
                    break
            if valid and vlan_ids:
                break
        # Native VLAN
        while True:
            native_str = input("Native VLAN ID (or blank to skip): ").strip()
            if not native_str:
                native_vlan = None
                break
            if validate_vlan(native_str):
                native_vlan = int(native_str)
                # Warn if native VLAN not in allowed list
                if native_vlan not in vlan_ids:
                    print("Warning: Native VLAN not in allowed VLANs list.")
                break
            print("Invalid VLAN ID.")
        for intf in interfaces:
            existing_tps.append({
                "interface": intf,
                "description": desc,
                "allowed_vlan": vlan_ids,
                "native_vlan": native_vlan,
            })
        print(f"  Added trunk port(s): {', '.join(interfaces)} allowed VLANs {','.join(map(str, vlan_ids))} native VLAN {native_vlan if native_vlan else 'unspecified'}")

    return existing_tps


def validate_vlan(vlan_id):
    """Validate VLAN ID is an integer 1-4094."""
    try:
        vid = int(vlan_id)
        return 1 <= vid <= 4094
    except (ValueError, TypeError):
        return False


def validate_ipv4(addr):
    """Validate IPv4 address format."""
    parts = addr.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        try:
            num = int(part)
            if num < 0 or num > 255:
                return False
        except ValueError:
            return False
    return True


def sanitize_string(s, max_len=64):
    """Remove characters that could be used for CLI injection.
    Allows letters, digits, spaces, dots, dashes, and underscores."""
    s = re.sub(r"[^a-zA-Z0-9 ._-]", "", s)
    s = s[:max_len].strip()
    return s


def parse_interfaces_simple(iface_str):
    """
    Parse interface string into list of interface names.
    Formats accepted (GigabitEthernet only):
      - GigabitEthernet1/0/1
      - GigabitEthernet1/0/1-12 (range on last number: 1/0/1 through 1/0/12)
      - GigabitEthernet1/0/1-8,GigabitEthernet1/0/15 (range plus single, comma-separated)
    Returns list of interface strings or None if no valid interfaces parsed.
    """
    parts = iface_str.split(",")
    interfaces = []
    for part in parts:
        part = part.strip()
        if not part:
            continue  # skip empty parts (e.g., trailing comma)
        # Match GigabitEthernet<slot>/<port>/<subport>-<end>
        m = re.match(
            r"^GigabitEthernet(\d+)/(\d+)/(\d+)(?:-(\d+))?$",
            part,
            re.IGNORECASE,
        )
        if m:
            slot = int(m.group(1))
            port = int(m.group(2))
            sub_start = int(m.group(3))
            sub_end = int(m.group(4)) if m.group(4) else sub_start
            # Validate
            if slot < 1 or slot > 9999:
                print(f"  Invalid slot number in '{part}'")
                continue  # skip this part but continue with others
            if sub_start < 0 or sub_end > 9999 or sub_start > sub_end:
                print(f"  Invalid sub-number range in '{part}'")
                continue
            # Generate all interfaces in range (varying only the last number)
            for s in range(sub_start, sub_end + 1):
                interfaces.append(f"GigabitEthernet{slot}/{port}/{s}")
        else:
            print(f"  Unrecognized interface format: '{part}' - skipped")
            continue

    if not interfaces:
        return None
    return interfaces


def generate_initial_config_section(config):
    """Generate the initial configuration commands section."""
    lines = []
    hostname = config["hostname"]
    lines.append(f"hostname {hostname}")
    lines.append("")

    # Enable secret
    if config["enable_secret"]:
        lines.append(f"enable secret {config['enable_secret']}")
    else:
        lines.append("! No enable secret configured")
    lines.append("")

    # Management VLAN
    if config["mgmt_vlan"]:
        lines.append(f"vlan {config['mgmt_vlan']}")
        lines.append(" name MGMT")
        lines.append("!")
        lines.append("")

    # Management IP interface
    if config["mgmt_ip"] and config["mgmt_mask"] and config["mgmt_vlan"]:
        lines.append(f"interface vlan {config['mgmt_vlan']}")
        lines.append(f" ip address {config['mgmt_ip']} {config['mgmt_mask']}")
        lines.append(" no shutdown")
        lines.append("!")
        lines.append("")

    # Default gateway
    if config["gateway"]:
        lines.append(f"ip route 0.0.0.0 0.0.0.0 {config['gateway']}")

    # Domain name
    if config["domain_name"]:
        lines.append(f"ip domain name {config['domain_name']}")

    # Local admin
    if config["username"]:
        lines.append(f"username {config['username']} privilege 15 secret {config['password']}" if config["password"] else f"username {config['username']} privilege 15")
    if config["banner"]:
        lines.append(f"banner motd ^{config['banner']}^")
    if config["ssh"]:
        lines.append("line vty 0 4")
        lines.append(" transport input ssh")
        lines.append("!")

    lines.append("!")
    return "\n".join(lines)


def generate_vlans_section(vlans):
    """Generate VLAN configuration commands."""
    lines = []
    if not vlans:
        lines.append("! No VLANs configured")
        return "\n".join(lines)
    lines.append("! VLAN definitions")
    for v in vlans:
        lines.append(f"vlan {v['id']}")
        lines.append(f" name {v['name']}")
        lines.append("!")
    return "\n".join(lines)


def generate_access_ports_section(access_ports):
    """Generate access port configuration commands."""
    lines = []
    if not access_ports:
        lines.append("! No access ports configured")
        return "\n".join(lines)
    # Group by VLAN for interface range
    # Sort by interface for consistent output
    sorted_ports = sorted(access_ports, key=lambda x: x["interface"])
    # Try to create interface ranges
    # Simple approach: just list individual interfaces
    for ap in sorted_ports:
        intf = ap["interface"]
        vlan = ap["vlan"]
        desc = ap["description"]
        lines.append(f"interface {intf}")
        lines.append(" switchport mode access")
        lines.append(f" switchport access vlan {vlan}")
        if ap["portfast"]:
            lines.append(" spanning-tree portfast")
        if ap["bpdu_guard"]:
            lines.append(" spanning-tree bpduguard enable")
        if desc:
            lines.append(f" description {desc}")
        lines.append("!")
    return "\n".join(lines)


def generate_trunk_ports_section(trunk_ports):
    """Generate trunk port configuration commands."""
    lines = []
    if not trunk_ports:
        lines.append("! No trunk ports configured")
        return "\n".join(lines)
    for tp in trunk_ports:
        intf = tp["interface"]
        desc = tp["description"]
        allowed = ",".join(map(str, tp["allowed_vlan"]))
        native = tp["native_vlan"] if tp["native_vlan"] else "unspecified"
        lines.append(f"interface {intf}")
        if desc:
            lines.append(f" description {desc}")
        lines.append(" switchport mode trunk")
        lines.append(f" switchport trunk allowed vlan {allowed}")
        if tp["native_vlan"]:
            lines.append(f" switchport trunk native vlan {native}")
        lines.append("!")
    return "\n".join(lines)


def verification_commands(section, config):
    """Return verification commands relevant to the given section."""
    if section == "complete":
        cmds = ["show running-config", "show vlan brief"]
        referenced = sorted({ap["interface"] for ap in config["access_ports"]}
                            | {tp["interface"] for tp in config["trunk_ports"]})
        if referenced:
            cmds.append("show interfaces status | include " + "| ".join(referenced[:10]))
        cmds += ["show interfaces trunk", "show interfaces switchport"]
        return cmds
    if section == "initial":
        return ["show running-config", "show ip interface brief"]
    if section == "vlans":
        return ["show vlan brief", "show running-config"]
    if section == "access":
        return ["show interfaces status", "show interfaces switchport", "show running-config"]
    if section == "trunk":
        return ["show interfaces trunk", "show interfaces switchport", "show running-config"]
    return ["show running-config"]


def generate_config(section, config):
    """Build the copyable output block for a single module section.

    section is one of: 'initial', 'vlans', 'access', 'trunk', 'complete'.
    """
    if section == "complete":
        return generate_complete_config(config)

    titles = {
        "initial": "Initial Device Configuration",
        "vlans": "VLAN Configuration",
        "access": "Access-Port Configuration",
        "trunk": "Trunk-Port Configuration",
    }
    builders = {
        "initial": lambda: generate_initial_config_section(config),
        "vlans": lambda: generate_vlans_section(config["vlans"]),
        "access": lambda: generate_access_ports_section(config["access_ports"]),
        "trunk": lambda: generate_trunk_ports_section(config["trunk_ports"]),
    }

    lines = [
        "=" * 60,
        f"Cisco Switch Configuration - {titles[section]}",
        "=" * 60,
        "",
        builders[section](),
        "",
        "! --- Verification Commands ---",
    ]
    lines.extend(verification_commands(section, config))
    lines += ["", "=" * 60, "END OF CONFIGURATION", "=" * 60]
    return "\n".join(lines)


def generate_complete_config(config):
    """Generate the complete combined configuration."""
    lines = []
    hostname = config["hostname"]
    lines.append("=" * 60)
    lines.append(f"Cisco Switch Configuration Generated for {hostname}")
    lines.append("=" * 60)
    lines.append("")

    # 1. Initial device settings
    lines.append("! --- 1. Initial Device Settings ---")
    lines.append(f"hostname {hostname}")
    lines.append("")

    if config["enable_secret"]:
        lines.append(f"enable secret {config['enable_secret']}")
    lines.append("")

    if config["mgmt_vlan"]:
        lines.append(f"vlan {config['mgmt_vlan']}")
        lines.append(" name MGMT")
        lines.append("!")
        lines.append("")

    if config["mgmt_ip"] and config["mgmt_mask"]:
        lines.append(f"interface vlan {config['mgmt_vlan']}")
        lines.append(f" ip address {config['mgmt_ip']} {config['mgmt_mask']}")
        lines.append(" no shutdown")
        lines.append("!")
        lines.append("")

    if config["gateway"]:
        lines.append(f"ip route 0.0.0.0 0.0.0.0 {config['gateway']}")

    if config["domain_name"]:
        lines.append(f"ip domain name {config['domain_name']}")

    if config["username"]:
        pwd_part = f" secret {config['password']}" if config["password"] else ""
        lines.append(f"username {config['username']} privilege 15{pwd_part}")

    if config["banner"]:
        lines.append(f"banner motd ^{config['banner']}^")

    if config["ssh"]:
        lines.append("line vty 0 4")
        lines.append(" transport input ssh")

    lines.append("")
    lines.append("! --- 2. VLAN Definitions ---")
    lines.append(generate_vlans_section(config["vlans"]))
    lines.append("")

    # 3. Management configuration already included above
    # 4. Access-port configuration
    lines.append("! --- 4. Access-Port Configuration ---")
    lines.append(generate_access_ports_section(config["access_ports"]))
    lines.append("")

    # 5. Trunk-port configuration
    lines.append("! --- 5. Trunk-Port Configuration ---")
    lines.append(generate_trunk_ports_section(config["trunk_ports"]))
    lines.append("")

    # 6. Optional edge-port security settings
    lines.append("! --- 6. Edge-Port Security Settings ---")
    # Summary of PortFast/BPDU Guard usage
    has_portfast = any(ap["portfast"] for ap in config["access_ports"])
    has_bpdu = any(ap["bpdu_guard"] for ap in config["access_ports"])
    if has_portfast or has_bpdu:
        lines.append("! PortFast and BPDU Guard enabled on edge ports:")
        for ap in config["access_ports"]:
            if ap["portfast"] or ap["bpdu_guard"]:
                lines.append(f"! {ap['interface']}: PortFast={ap['portfast']}, BPDUGuard={ap['bpdu_guard']}")
    else:
        lines.append("! No PortFast or BPDU Guard configured (recommended for uplinks)")
    lines.append("")

    # 7. Verification commands
    lines.append("! --- 7. Verification Commands ---")
    # Build set of interfaces referenced
    referenced = set()
    for ap in config["access_ports"]:
        referenced.add(ap["interface"])
    for tp in config["trunk_ports"]:
        referenced.add(tp["interface"])
    for v in config["vlans"]:
        referenced.add(f"vlan {v['id']}")

    lines.append("show running-config")
    lines.append("show vlan brief")
    if referenced:
        lines.append(f"show interfaces status | include {'| '.join(sorted(referenced)[:10])}")
    lines.append("show interfaces trunk")
    lines.append("show interfaces switchport")
    lines.append("")

    lines.append("!" * 60)
    lines.append("END OF CONFIGURATION")
    lines.append("!" * 60)

    return "\n".join(lines)


def handle_output(complete_cfg):
    """Display configuration and handle save options."""
    print("\n" + "=" * 60)
    print("GENERATED CISCO CONFIGURATION")
    print("=" * 60)
    print(complete_cfg)
    print("=" * 60 + "\n")

    # Security warning
    print("WARNING: The generated configuration may contain sensitive credentials")
    print("(enable secret, passwords, usernames). Do not share or store publicly.\n")

    print("Save options:")
    print("  1. Display configuration again")
    print("  2. Save to .cfg file")
    print("  3. Save to .txt file")
    print("  4. Return to main menu")

    choice = input("\nChoose option (1-4): ").strip()
    if choice == "1":
        print("\n" + "=" * 60)
        print("GENERATED CISCO CONFIGURATION (again)")
        print("=" * 60)
        print(complete_cfg)
        print("=" * 60 + "\n")
    elif choice == "2":
        ext = ".cfg"
        default_name = "switch_config.cfg"
        filename = input(f"Enter filename [{default_name}]: ").strip()
        if not filename:
            filename = default_name
        if not filename.endswith(".cfg"):
            filename += ".cfg"
        if os.path.exists(filename):
            overwrite = input(f"File {filename} already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != "y":
                print("Save cancelled.")
                return
        try:
            with open(filename, "w") as f:
                f.write(complete_cfg)
            print(f"Configuration saved to {filename}")
        except IOError as e:
            print(f"Error saving file: {e}")
    elif choice == "3":
        ext = ".txt"
        default_name = "switch_config.txt"
        filename = input(f"Enter filename [{default_name}]: ").strip()
        if not filename:
            filename = default_name
        if not filename.endswith(".txt"):
            filename += ".txt"
        if os.path.exists(filename):
            overwrite = input(f"File {filename} already exists. Overwrite? (y/n): ").strip().lower()
            if overwrite != "y":
                print("Save cancelled.")
                return
        try:
            extract_to_txt(complete_cfg, filename)
            print(f"Clean configuration extracted to {filename}")
        except IOError as e:
            print(f"Error saving file: {e}")
        except Exception as e:
            print(f"Error extracting clean config: {e}")
    # choice 4: return to main menu (just fall through)


def extract_to_txt(cfg_content, output_path):
    """Extract only Cisco CLI commands (strip headers/comments, warnings, save menu text)
    and write to a clean .txt file suitable for copy/pasting to Cisco devices.
    """
    lines = []
    for line in cfg_content.splitlines():
        stripped = line.strip()
        # Skip UI elements
        if stripped.startswith("==="):
            continue
        if "GENERATED CISCO CONFIGURATION" in stripped:
            continue
        if stripped.startswith("WARNING:"):
            continue
        if stripped.startswith("Save options:"):
            continue
        if stripped in ("1. Display configuration again",
                        "2. Save to a .cfg file",
                        "3. Save to a .txt file",
                        "4. Return to the main menu"):
            continue
        if stripped == "Choose option (1-4):":
            continue
        if stripped == "END OF CONFIGURATION":
            continue
        if stripped.startswith("Cisco Switch Configuration"):
            continue
        lines.append(line)
    # Collapse excessive blank lines
    cleaned = []
    prev_blank = False
    for l in lines:
        is_blank = (l.rstrip() == "")
        if is_blank and prev_blank:
            continue
        cleaned.append(l)
        prev_blank = is_blank
    content = "\n".join(cleaned).strip() + "\n"
    with open(output_path, "w") as f:
        f.write(content)
    return output_path
    # choice 4: return to main menu (just fall through)


if __name__ == "__main__":
    main()