# ModbustoWELD for ESP32

Run the ModbustoWELD bridge directly on an ESP32 microcontroller with WiFi connectivity.

## Quick Links

- 🚀 **[Quick Start Guide](QUICKSTART.md)** - Get running in 15 minutes!
- 🔧 **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions
- 📝 **Full README** - You're reading it
- 🧪 **[test_esp32.py](test_esp32.py)** - Test script for your ESP32

## Overview

This implementation allows you to run a complete Modbus TCP to WLED bridge on an ESP32 microcontroller, eliminating the need for a separate computer. The ESP32 connects to your WiFi network and acts as a Modbus TCP slave, controlling WLED devices via HTTP.

## Features

- ✨ Runs standalone on ESP32 (no PC required)
- 📡 WiFi connectivity
- 🔌 Modbus TCP slave implementation (act as Modbus server)
- 🔌 **NEW: Modbus TCP client implementation** (connect to other Modbus servers)
- 🌈 Full WLED control (power, brightness, RGB, effects)
- 💾 Low memory footprint (~50KB)
- ⚡ Fast response times (<100ms typical)
- 🔋 Low power consumption

## Hardware Requirements

- **ESP32 Development Board** (any variant with WiFi)
  - ESP32-DevKitC
  - ESP32-WROOM-32
  - ESP32-S2/S3
  - NodeMCU-32S
- **USB cable** for programming
- **WiFi network** (2.4 GHz)
- **WLED device** on the same network

### Tested Boards
- ✅ ESP32-DevKitC V4
- ✅ ESP32-WROOM-32
- ✅ NodeMCU-32S

## Software Requirements

- **MicroPython firmware** v1.19.1 or later
- **esptool** (for flashing)
- **ampy** or **mpremote** (for file upload)

## Installation

### Step 1: Install MicroPython on ESP32

1. Download the latest MicroPython firmware for ESP32:
   ```bash
   wget https://micropython.org/resources/firmware/esp32-20230426-v1.20.0.bin
   ```

2. Install esptool (if not already installed):
   ```bash
   pip install esptool
   ```

3. Connect your ESP32 via USB and find the serial port:
   - **Linux/Mac**: Usually `/dev/ttyUSB0` or `/dev/ttyUSB1`
   - **Windows**: Usually `COM3`, `COM4`, etc.

4. Erase the flash:
   ```bash
   esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
   ```

5. Flash MicroPython firmware:
   ```bash
   esptool.py --chip esp32 --port /dev/ttyUSB0 --baud 460800 write_flash -z 0x1000 esp32-20230426-v1.20.0.bin
   ```

### Step 2: Install File Upload Tool

Install `mpremote` (recommended):
```bash
pip install mpremote
```

Or install `ampy`:
```bash
pip install adafruit-ampy
```

### Step 3: Configure the Bridge

1. Edit `config.py` with your settings:
   ```python
   # WiFi Configuration
   WIFI_SSID = "your_wifi_ssid"
   WIFI_PASSWORD = "your_wifi_password"

   # Modbus TCP Configuration
   MODBUS_PORT = 5020
   MODBUS_SLAVE_ID = 1

   # WLED Configuration
   WLED_HOST = "192.168.1.100"  # Your WLED device IP
   WLED_PORT = 80
   ```

### Step 4: Upload Files to ESP32

**For Modbus Server (WLED Bridge):**

Using `mpremote`:
```bash
cd esp32
mpremote connect /dev/ttyUSB0 cp config.py :
mpremote connect /dev/ttyUSB0 cp wled_client.py :
mpremote connect /dev/ttyUSB0 cp modbus_slave.py :
mpremote connect /dev/ttyUSB0 cp main.py :
```

Or using `ampy`:
```bash
cd esp32
export AMPY_PORT=/dev/ttyUSB0
ampy put config.py
ampy put wled_client.py
ampy put modbus_slave.py
ampy put main.py
```

**For Modbus Client (Optional):**

If you want to use the ESP32 as a Modbus client to connect to other Modbus servers:

```bash
# Using mpremote
mpremote connect /dev/ttyUSB0 cp modbus_client.py :
mpremote connect /dev/ttyUSB0 cp modbus_client_example.py :

# Or using ampy
ampy put modbus_client.py
ampy put modbus_client_example.py
```

### Step 5: Run the Bridge

#### Option 1: Run Manually
Connect to the ESP32 serial console and run:
```python
import main
```

#### Option 2: Auto-start on Boot
Create a `boot.py` file that will run automatically:
```python
# boot.py
import main
```

Upload it:
```bash
mpremote connect /dev/ttyUSB0 cp boot.py :
```

Now the bridge will start automatically when the ESP32 powers on.

## Usage

### Connecting via Serial Console

Monitor the bridge output:
```bash
mpremote connect /dev/ttyUSB0
```

Or with screen:
```bash
screen /dev/ttyUSB0 115200
```

### Expected Output

```
==================================================
ModbustoWELD Bridge for ESP32
==================================================
[WiFi] Connecting to MyWiFi...
[WiFi] Connected!
[WiFi] IP Address: 192.168.1.50
[WiFi] Netmask: 255.255.255.0
[WiFi] Gateway: 192.168.1.1

[WLED] Connecting to 192.168.1.100:80
[WLED] Connected to: My LED Strip
[WLED] Version: 0.14.0

[Modbus] Starting server on port 5020
[Modbus] Server started on 0.0.0.0:5020

==================================================
Bridge is running!
Connect Modbus clients to: 192.168.1.50:5020
==================================================
```

### Testing the Connection

From another computer on the same network:

```python
from pymodbus.client import ModbusTcpClient

# Connect to ESP32 bridge
client = ModbusTcpClient('192.168.1.50', port=5020)

# Turn on LEDs
client.write_register(0, 1)

# Set brightness to 200
client.write_register(1, 200)

# Set color to blue
client.write_registers(2, [0, 0, 255])

client.close()
```

## Register Map

Same as the Python version:

### Holding Registers (Write Commands)
| Register | Function | Range | Description |
|----------|----------|-------|-------------|
| 0 | Power | 0-1 | 0=OFF, 1=ON |
| 1 | Brightness | 0-255 | LED brightness level |
| 2 | Red | 0-255 | Red color component |
| 3 | Green | 0-255 | Green color component |
| 4 | Blue | 0-255 | Blue color component |
| 5 | Effect | 0-255+ | WLED effect ID |

### Input Registers (Read Status)
| Register | Function | Range | Description |
|----------|----------|-------|-------------|
| 0 | Current Power | 0-1 | Current power state |
| 1 | Current Brightness | 0-255 | Current brightness |
| 2 | Current Red | 0-255 | Current red value |
| 3 | Current Green | 0-255 | Current green value |
| 4 | Current Blue | 0-255 | Current blue value |

## Modbus Client Usage

In addition to the Modbus TCP server (slave) functionality, the ESP32 can also act as a Modbus TCP **client** to connect to other Modbus servers.

### Features

- Connect to remote Modbus TCP servers
- Read holding registers (Function Code 3)
- Read input registers (Function Code 4)
- Write single register (Function Code 6)
- Write multiple registers (Function Code 16)
- Configurable timeout
- Error handling and reconnection support

### Installation

Upload the Modbus client module to your ESP32:

```bash
mpremote connect /dev/ttyUSB0 cp modbus_client.py :
```

### Basic Usage

```python
from modbus_client import ModbusTCPClient

# Create client
client = ModbusTCPClient(host="192.168.1.10", port=502, timeout=5)

# Connect to server
if client.connect():
    # Read holding registers
    values = client.read_holding_registers(address=0, count=5)
    print(f"Values: {values}")
    
    # Write single register
    client.write_register(address=0, value=100)
    
    # Write multiple registers
    client.write_registers(address=1, values=[50, 150, 200])
    
    # Read input registers
    status = client.read_input_registers(address=0, count=5)
    print(f"Status: {status}")
    
    # Close connection
    client.close()
```

### Example: Control WLED via Modbus

```python
from modbus_client import ModbusTCPClient
import time

# Connect to ModbustoWELD bridge
client = ModbusTCPClient(host="192.168.1.20", port=5020)

if client.connect():
    # Turn on WLED
    client.write_register(0, 1)
    time.sleep(1)
    
    # Set brightness
    client.write_register(1, 128)
    time.sleep(1)
    
    # Set color to red
    client.write_registers(2, [255, 0, 0])
    time.sleep(2)
    
    # Read current state
    state = client.read_input_registers(0, 5)
    print(f"Power: {state[0]}, Brightness: {state[1]}")
    print(f"Color: RGB({state[2]}, {state[3]}, {state[4]})")
    
    client.close()
```

### Full Example Script

A complete example script is provided in `modbus_client_example.py` that demonstrates all client features:

```bash
# Upload and run the example
mpremote connect /dev/ttyUSB0 cp modbus_client_example.py :
mpremote connect /dev/ttyUSB0 run modbus_client_example.py
```

The example script shows:
- Connecting to a Modbus server
- Reading/writing holding registers
- Reading input registers
- Error handling
- Controlling WLED devices via Modbus

### Use Cases

The Modbus client allows your ESP32 to:
- **Read data from PLCs** - Monitor PLC registers and respond to changes
- **Control other Modbus devices** - Send commands to industrial equipment
- **Chain multiple bridges** - ESP32 reads from one Modbus server and controls WLED
- **Data logging** - Poll Modbus sensors and log data
- **Automation** - Create complex automation by reading sensors and controlling actuators

### API Reference

#### `ModbusTCPClient(host, port=502, timeout=5)`

Create a new Modbus TCP client.

**Parameters:**
- `host` - Modbus server IP address or hostname
- `port` - Modbus server port (default: 502)
- `timeout` - Socket timeout in seconds (default: 5)

#### `connect()`

Connect to the Modbus server.

**Returns:** `True` on success, `False` on error

#### `close()`

Close the connection to the server.

#### `read_holding_registers(address, count)`

Read holding registers (Function Code 3).

**Parameters:**
- `address` - Starting register address
- `count` - Number of registers to read

**Returns:** List of register values or `None` on error

#### `read_input_registers(address, count)`

Read input registers (Function Code 4).

**Parameters:**
- `address` - Starting register address
- `count` - Number of registers to read

**Returns:** List of register values or `None` on error

#### `write_register(address, value)`

Write a single register (Function Code 6).

**Parameters:**
- `address` - Register address
- `value` - Value to write (0-65535)

**Returns:** `True` on success, `False` on error

#### `write_registers(address, values)`

Write multiple registers (Function Code 16).

**Parameters:**
- `address` - Starting register address
- `values` - List of values to write

**Returns:** `True` on success, `False` on error

## LED Status Indicator

The built-in LED (GPIO 2) provides status indication:
- **3 quick blinks**: WiFi connected
- **Slow blink (every 500ms)**: Bridge is running and processing updates

## Troubleshooting

### WiFi Connection Issues

**Problem**: ESP32 can't connect to WiFi
- Verify SSID and password in `config.py`
- Ensure your WiFi is 2.4 GHz (ESP32 doesn't support 5 GHz)
- Check WiFi signal strength
- Try moving ESP32 closer to the router

### WLED Connection Issues

**Problem**: Can't connect to WLED device
- Verify WLED IP address in `config.py`
- Ensure WLED device is powered on
- Test WLED manually: `curl http://<wled-ip>/json/state`
- Check that ESP32 and WLED are on the same network

### Modbus Connection Issues

**Problem**: Modbus client can't connect
- Verify ESP32 IP address (shown on serial console)
- Check firewall settings on client computer
- Ensure port 5020 is not blocked
- Try pinging the ESP32: `ping <esp32-ip>`

### Memory Issues

**Problem**: ESP32 runs out of memory
- Reduce `UPDATE_INTERVAL` in `config.py`
- Set `DEBUG = False` to reduce logging
- Restart ESP32 (press RESET button)

### Checking Logs

Enable debug mode in `config.py`:
```python
DEBUG = True
```

Connect to serial console to see detailed logs.

## Performance

- **Response Time**: 50-100ms typical
- **Update Rate**: 2 Hz (500ms polling, configurable)
- **Memory Usage**: ~50KB
- **Power Consumption**: ~80mA @ 3.3V (WiFi active)
- **Concurrent Clients**: Supports multiple simultaneous Modbus connections

## Limitations

- Single WLED device per ESP32
- WiFi 2.4 GHz only (no 5 GHz support)
- Limited to basic Modbus functions (FC 3, 4, 6, 16)
- No HTTPS support (HTTP only)
- Maximum 100 registers per register type

## Advanced Configuration

### Custom Port

Change the Modbus port in `config.py`:
```python
MODBUS_PORT = 502  # Standard Modbus port
```

### Faster Updates

Reduce the update interval (at the cost of more power consumption):
```python
UPDATE_INTERVAL = 250  # 250ms = 4 Hz update rate
```

### Custom Slave ID

Change the Modbus slave ID:
```python
MODBUS_SLAVE_ID = 10
```

## Power Saving

For battery-powered applications, you can implement deep sleep between updates:

```python
from machine import deepsleep

# Process some updates
# ...

# Sleep for 1 second
deepsleep(1000)
```

Note: This will require reconfiguration on wake-up.

## Upgrading

To update the bridge software:

1. Download the latest files from the repository
2. Upload the new files to ESP32 (overwrites old files)
3. Reset the ESP32

## Comparison with Python Version

| Feature | ESP32 | Python (PC) |
|---------|-------|-------------|
| Hardware Cost | $5-10 | $50-500+ |
| Power Usage | <1W | 10-100W |
| Size | Tiny | Desktop/Laptop |
| Reliability | High | Medium |
| Performance | Good | Excellent |
| Features | Basic | Full |
| Setup Complexity | Medium | Low |

## Modbus Client vs Server

The ESP32 implementation includes both Modbus client and server functionality:

| Component | Role | Use Case |
|-----------|------|----------|
| **Modbus Server (Slave)** | Receives commands from other Modbus clients | Control WLED from PLC/SCADA systems |
| **Modbus Client (Master)** | Sends commands to other Modbus servers | Read PLC data, control other Modbus devices |

**Example scenarios:**
- **Server only**: PLC → ESP32 → WLED (ESP32 receives commands)
- **Client only**: ESP32 → PLC/Device (ESP32 sends commands)
- **Both**: ESP32 reads from PLC and controls WLED based on data

## Use Cases

Perfect for:
- 🏭 Industrial installations where PC is impractical
- 🏠 Home automation (low power, always-on)
- 🔌 Panel-mounted installations
- 🚀 Remote/embedded applications
- 💰 Budget-conscious projects

## Support

For ESP32-specific issues:
- Check serial console output
- Review MicroPython documentation
- Test basic WiFi connectivity first
- Verify WLED works independently

## Additional Resources

- [MicroPython Documentation](https://docs.micropython.org/)
- [ESP32 Pinout Reference](https://randomnerdtutorials.com/esp32-pinout-reference-gpios/)
- [WLED API Documentation](https://kno.wled.ge/interfaces/json-api/)
- [Modbus Protocol Specification](https://modbus.org/specs.php)

## Contributing

Contributions to improve ESP32 support are welcome! Please see the main CONTRIBUTING.md file.

## License

Same as main project - MIT License
