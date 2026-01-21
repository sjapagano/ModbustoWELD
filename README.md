# ModbustoWELD

A Modbus TCP server that acts as a bridge to control WLED devices. This allows industrial automation systems, PLCs, and SCADA systems to control WLED LED strips via standard Modbus TCP protocol.

## Features

- ✨ Control WLED devices via Modbus TCP
- 🔌 Standard Modbus register interface
- 🌈 Control power, brightness, RGB color, and effects
- 📊 Read current WLED state via input registers
- ⚙️ Configurable via YAML or command-line arguments
- 📝 Comprehensive logging

## Requirements

- Python 3.7+
- WLED device on the network
- Network connectivity between the Modbus client and this bridge

## Installation

### Method 1: Direct Python Installation

1. Clone the repository:
```bash
git clone https://github.com/sjapagano/ModbustoWELD.git
cd ModbustoWELD
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the application (edit `config.yaml`):
```yaml
modbus:
  host: "0.0.0.0"  # Listen on all interfaces
  port: 5020       # Modbus TCP port

wled:
  host: "192.168.1.100"  # Your WLED device IP
  port: 80

logging:
  level: "INFO"
```

### Method 2: Docker

1. Clone the repository:
```bash
git clone https://github.com/sjapagano/ModbustoWELD.git
cd ModbustoWELD
```

2. Edit `config.yaml` with your WLED device IP

3. Build and run with Docker Compose:
```bash
docker-compose up -d
```

Or build manually:
```bash
docker build -t modbustoweld .
docker run -d -p 5020:5020 -v $(pwd)/config.yaml:/app/config.yaml --name modbustoweld modbustoweld
```

4. View logs:
```bash
docker-compose logs -f
# or
docker logs -f modbustoweld
```

## Usage

### Basic Usage

Run with default configuration:
```bash
python main.py
```

Run with custom configuration file:
```bash
python main.py --config myconfig.yaml
```

### Command-Line Options

```bash
python main.py --help
```

Override configuration with command-line arguments:
```bash
python main.py --wled-host 192.168.1.100 --modbus-port 5020 --log-level DEBUG
```

## Modbus Register Map

### Holding Registers (Read/Write - Commands)

| Register | Function | Range | Description |
|----------|----------|-------|-------------|
| 0 | Power | 0-1 | 0=OFF, 1=ON |
| 1 | Brightness | 0-255 | LED brightness level |
| 2 | Red | 0-255 | Red color component |
| 3 | Green | 0-255 | Green color component |
| 4 | Blue | 0-255 | Blue color component |
| 5 | Effect | 0-255+ | WLED effect ID |

### Input Registers (Read-Only - Status)

| Register | Function | Range | Description |
|----------|----------|-------|-------------|
| 0 | Current Power | 0-1 | Current power state |
| 1 | Current Brightness | 0-255 | Current brightness |
| 2 | Current Red | 0-255 | Current red value |
| 3 | Current Green | 0-255 | Current green value |
| 4 | Current Blue | 0-255 | Current blue value |

## Examples

### Using Python with pymodbus

```python
from pymodbus.client import ModbusTcpClient

# Connect to the bridge
client = ModbusTcpClient('localhost', port=5020)

# Turn on the LEDs
client.write_register(0, 1)

# Set brightness to 128
client.write_register(1, 128)

# Set color to red (RGB: 255, 0, 0)
client.write_registers(2, [255, 0, 0])

# Read current brightness
result = client.read_input_registers(1, 1)
print(f"Current brightness: {result.registers[0]}")

client.close()
```

### Using Modbus Poll/Slave Tools

1. Connect to `<bridge-ip>:5020`
2. Write to holding register 0 with value 1 to turn on
3. Write to holding register 1 with value 0-255 to set brightness
4. Write to holding registers 2, 3, 4 to set RGB color

## Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌──────────────┐
│  Modbus Client  │         │  ModbustoWELD    │         │     WLED     │
│   (PLC/SCADA)   │◄───────►│     Bridge       │◄───────►│    Device    │
│                 │  Modbus │                  │  HTTP   │              │
└─────────────────┘   TCP   └──────────────────┘  API    └──────────────┘
```

The bridge:
1. Runs a Modbus TCP server listening on the configured port
2. Accepts Modbus read/write commands from clients
3. Translates Modbus register operations to WLED HTTP API calls
4. Periodically polls WLED device for current state
5. Updates input registers with current WLED state

## Troubleshooting

### Cannot connect to WLED device

- Verify WLED device IP address is correct
- Ensure WLED device is on the same network
- Test WLED API manually: `curl http://<wled-ip>/json/state`

### Modbus client cannot connect

- Check firewall settings
- Verify the Modbus port (default: 5020) is not blocked
- Check that the bridge is listening on the correct interface

### Changes not applying

- Check the logs for errors: `tail -f modbustoweld.log`
- Verify WLED device is responding
- Increase log level to DEBUG for more details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Credits

- [WLED](https://github.com/Aircoookie/WLED) - Amazing LED control software
- [pymodbus](https://github.com/pymodbus-dev/pymodbus) - Modbus protocol implementation
