# Cisco Configuration Generator

A simple interactive CLI tool that generates Cisco switch configuration commands based on user input.

## Features

- Interactive menu-driven interface
- Generate initial configuration (hostname, enable secret, management VLAN/IP, gateway, SSH, etc.)
- Configure VLANs (with validation and duplicate prevention)
- Configure access ports (single, range, or comma-separated interfaces)
- Configure trunk ports (allowed VLANs, native VLAN)
- Generate complete switch configuration
- Save configuration to `.cfg` or `.txt` files
- Input validation and security warnings

## Requirements

- Python 3.6+ (standard library only)

## Installation

Clone or download the repository:

```bash
git clone https://github.com/aavash-devkota/Cisco_Switch_template.git
cd Cisco_Switch_template
```

## Usage

Run the tool:

```bash
python3 ciscoconfig.py
```

You will see the main menu:

```text
Cisco Configuration Generator
-----------------------------
1. Generate initial configuration
2. Configure VLANs
3. Configure access ports
4. Configure trunk ports
5. Generate complete switch configuration
0. Exit
```

Follow the prompts to provide the required information. The tool will generate copyable Cisco IOS/IOS XE commands.

## Interface Format

Access and trunk ports accept these formats:

- `GigabitEthernet1/0/1` - Single interface
- `GigabitEthernet1/0/1-12` - Port range
- `GigabitEthernet1/0/1-8,15` - Range and individual ports

## Security Notes

- Do **not** use default passwords in production
- The tool warns when generating configurations with credentials
- User inputs (descriptions, names) are sanitized to prevent CLI injection
- Generated configurations run locally - no connection to Cisco devices

## License

This project is open-source and available under the MIT License. See [LICENSE](LICENSE) for details.

## Examples

See [EXAMPLES.md](EXAMPLES.md) for example inputs and outputs.
