Cisco Configuration Generator
==============================

A simple interactive CLI tool to generate Cisco switch configuration commands.
Uses Python 3 standard library only.

--------------------------------

Installation
------------

No installation required. Ensure you have Python 3 installed, then run:

    python3 ciscoconfig.py

--------------------------------

Usage
-----

When executed, a menu will be displayed:

    Cisco Configuration Generator
    -----------------------------
    1. Generate initial configuration
    2. Configure VLANs
    3. Configure access ports
    4. Configure trunk ports
    5. Generate complete switch configuration
    0. Exit

Select an option (0-5) and follow the prompts. You can return to the main
menu or exit at any time by entering "0".

--------------------------------

Menu Options

1. Generate initial configuration
   Collects hostname, enable secret, management VLAN/IP, gateway, domain
   name, local admin credentials, SSH, and login banner settings.

2. Configure VLANs
   Allows defining multiple VLANs in one session. For each VLAN, enter the
   VLAN ID (1-4094) and name. Duplicate VLAN IDs are rejected.

3. Configure access ports
   Configure access ports with optional description, PortFast, and BPDU Guard.
   Interface formats accepted:
      GigabitEthernet1/0/1
      GigabitEthernet1/0/1-12
      GigabitEthernet1/0/1-8,15

4. Configure trunk ports
   Configure trunk ports with allowed VLANs and optional native VLAN.
   Interface formats accepted:
      GigabitEthernet1/0/23-24
      GigabitEthernet1/0/1

5. Generate complete switch configuration
   Collects all parameters in one session and generates a complete
   configuration combining initial settings, VLANs, management, access
   ports, trunk ports, edge-port security, and verification commands.

0. Exit
   Terminates the program.

--------------------------------

Input Validation

- VLAN IDs: Must be integers 1-4094. Duplicates are rejected.
- IPv4 addresses and subnet masks: Each octet must be 0-255.
- Interface syntax: GigabitEthernet<slot>/<port>/<subport>, with optional
  range on the last number (e.g., 1/0/1-12).
- VLAN names: Sanitized to remove characters that could inject CLI commands.
- Descriptions and names: Stripped of semicolons, parentheses, backticks,
  and other CLI-special characters to prevent injection.
- Duplicate interface detection: Access and trunk port assignments are
  checked for overlaps.

--------------------------------

Sensitive Credentials Warning

The generated configuration may contain sensitive credentials including:
enable secret, usernames, and passwords. A warning is displayed before and
after generating the configuration. Do not share or store the generated
configuration publicly.

--------------------------------

Output Options

After generating a complete configuration (option 5), you will be asked:

  1. Display the configuration again
  2. Save it to a .cfg file
  3. Save it to a .txt file
  4. Return to the main menu

If saving to a file, the tool will not overwrite an existing file without
confirmation.

--------------------------------

Examples
--------

Example 1: Initial configuration only

    Cisco Configuration Generator
    -----------------------------
    1. Generate initial configuration
    2. Configure VLANs
    3. Configure access ports
    4. Configure trunk ports
    5. Generate complete switch configuration
    0. Exit

    Enter choice (0-5): 1

    --- Initial Configuration ---
    Enter hostname [default-SWITCH]: SW-CORE
    Enable secret (optional, leave blank for none): <leave blank>
    Management VLAN ID (e.g., 99, or blank to skip): 99
    Management IP address (e.g., 192.168.1.1, or blank to skip): 192.168.1.1
    Subnet mask (e.g., 255.255.255.0, or blank to skip): 255.255.255.0
    Default gateway (e.g., 192.168.1.254, or blank to skip): 192.168.1.254
    Domain name (optional, leave blank to skip): example.com
    Local administrator (optional, leave username blank to skip): admin
    Password (leave blank for no password): <leave blank>
    SSH configuration (Enable SSH? (y/n, default n)): n
    Login banner (optional, leave blank to skip): <leave blank>
    DNS server (optional, leave blank to skip): <leave blank>
    NTP server (optional, leave blank to skip): <leave blank>

    Generated configuration may contain sensitive credentials.
    Do not share or store publicly.

    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    GENERATED CISCO CONFIGURATION
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    =...
    (generated commands)....
    =...
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    WARNING: The generated configuration may contain sensitive credentials
    (enable secret, passwords, usernames). Do not share or store publicly.

    Save options:
      1. Display configuration again
      2. Save to .cfg file
      3. Save to .txt file
      4. Return to main menu

Example 2: Full configuration with VLANs, access ports, and trunks

    Cisco Configuration Generator
    -----------------------------
    1. Generate initial configuration
    2. Configure VLANs
    3. Configure access ports
    4. Configure trunk ports
    5. Generate complete switch configuration
    0. Exit

    Enter choice (0-5): 5

    --- Initial Configuration ---
    (provide initial config settings)

    --- VLAN Configuration ---
    VLAN ID (or blank to finish): 10
    VLAN name (e.g., USERS): USERS
    VLAN ID (or blank to finish): 20
    VLAN name (e.g., SERVERS): SERVERS
    VLAN ID (or blank to finish): <blank>

    --- Access-Port Configuration ---
    Interface selection (or blank to finish): GigabitEthernet1/0/1-8
    Access VLAN ID (1-4094): 10
    Interface description (optional, leave blank for default): USER_ACCESS_PORTS
    Enable PortFast? (y/n, default n): y
    Enable BPDU Guard? (y/n, default n): y

    !!! Note: PortFast and BPDU Guard are intended for edge/end-user ports,
    not indiscriminately for network uplinks/trunks.

    --- Trunk-Port Configuration ---
    Interface selection (or blank to finish): GigabitEthernet1/0/23-24
    Description (optional, leave blank): SWITCH_UPLINKS
    Allowed VLAN IDs (comma-separated, e.g., 10,20,30,99): 10,20,30,99
    Native VLAN ID (or blank to skip): 99

    !!! Generated configuration may contain sensitive credentials.
    !!!

    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    GENERATED CISCO CONFIGURATION
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    =... (complete config with all sections) ...
    =...
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    WARNING: The generated configuration may contain sensitive credentials
    (enable secret, passwords, usernames). Do not share or store publicly.

    Save options:
      1. Display configuration again
      2. Save to .cfg file
      3. Save to .txt file
      4. Return to main menu

--------------------------------

File Reference

- ciscoconfig.py - Main script (single file, no dependencies)
- README.md - This document

--------------------------------

Code Quality

The implementation follows these guidelines:

- Single file (ciscoconfig.py), no complex package structure
- Standard library only (no external dependencies)
- Small, focused functions with clear names:
    main(), get_initial_config(), get_vlans(), get_access_ports(),
    get_trunk_ports(), validate_vlan(), parse_interfaces(), generate_config(),
    save_config()
- Clear comments and concise code
- No classes or abstractions unnecessary to the tool's purpose

--------------------------------

Testing

The script has been tested with valid inputs for all modules. Core validation
functions (VLAN IDs, IPv4 addresses, interface parsing, string sanitization)
have been verified. Interactive testing is recommended to confirm the full
workflow meets your needs.

--------------------------------

Security

- No default passwords are used
- Passwords are not displayed in the output
- A warning is shown that generated configs may contain sensitive credentials
- User-supplied descriptions and names are sanitized to prevent CLI injection

The tool runs locally without connecting to any Cisco device.