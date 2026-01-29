# ModbustoWELD Examples

This document provides practical examples for using ModbustoWELD in various scenarios.

## Table of Contents

- [Basic Setup](#basic-setup)
- [Python Client Examples](#python-client-examples)
- [PLC Integration](#plc-integration)
- [Home Automation Integration](#home-automation-integration)
- [Advanced Examples](#advanced-examples)

## Basic Setup

### 1. Install and Run the Bridge

```bash
# Install dependencies
pip install -r requirements.txt

# Edit config.yaml with your WLED IP
nano config.yaml

# Start the bridge
python main.py
```

### 2. Verify Connection

```bash
# In another terminal, run the test client
python test_client.py
```

## Python Client Examples

### Example 1: Simple On/Off Control

```python
from pymodbus.client import ModbusTcpClient

# Connect to bridge
client = ModbusTcpClient('localhost', port=5020)

# Turn on
client.write_register(0, 1)

# Turn off
client.write_register(0, 0)

client.close()
```

### Example 2: Set Brightness and Color

```python
from pymodbus.client import ModbusTcpClient
import time

client = ModbusTcpClient('localhost', port=5020)

# Turn on
client.write_register(0, 1)
time.sleep(0.5)

# Set brightness to 50%
client.write_register(1, 128)
time.sleep(0.5)

# Set color to purple (RGB: 128, 0, 128)
client.write_registers(2, [128, 0, 128])

client.close()
```

### Example 3: Color Cycling

```python
from pymodbus.client import ModbusTcpClient
import time

client = ModbusTcpClient('localhost', port=5020)

# Turn on
client.write_register(0, 1)
client.write_register(1, 200)  # Bright

colors = [
    (255, 0, 0),    # Red
    (255, 127, 0),  # Orange
    (255, 255, 0),  # Yellow
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (75, 0, 130),   # Indigo
    (148, 0, 211)   # Violet
]

for red, green, blue in colors:
    print(f"Setting color to RGB({red}, {green}, {blue})")
    client.write_registers(2, [red, green, blue])
    time.sleep(2)

client.close()
```

### Example 4: Reading Current State

```python
from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('localhost', port=5020)

# Read all status registers
result = client.read_input_registers(0, count=5)

if not result.isError():
    power, brightness, red, green, blue = result.registers
    print(f"Power: {'ON' if power else 'OFF'}")
    print(f"Brightness: {brightness}/255")
    print(f"Color: RGB({red}, {green}, {blue})")
else:
    print(f"Error: {result}")

client.close()
```

### Example 5: Sunrise Simulation

```python
from pymodbus.client import ModbusTcpClient
import time

def sunrise_effect(client, duration_minutes=30):
    """Simulate a sunrise over a given duration"""
    steps = duration_minutes * 60  # One step per second
    
    # Start with lights off
    client.write_register(0, 1)  # Turn on
    client.write_register(1, 0)  # Brightness 0
    client.write_registers(2, [255, 50, 0])  # Warm orange
    
    for step in range(steps):
        # Calculate brightness (0 to 255)
        brightness = int((step / steps) * 255)
        client.write_register(1, brightness)
        
        # Gradually shift from orange to yellow to white
        if step < steps / 2:
            # Orange to yellow
            green = int((step / (steps / 2)) * 200)
            client.write_registers(2, [255, 50 + green, 0])
        else:
            # Yellow to white
            blue = int(((step - steps / 2) / (steps / 2)) * 200)
            client.write_registers(2, [255, 250, blue])
        
        time.sleep(1)
    
    print("Sunrise complete!")

client = ModbusTcpClient('localhost', port=5020)
sunrise_effect(client, duration_minutes=5)  # 5-minute sunrise
client.close()
```

## PLC Integration

### Ladder Logic Example (Conceptual)

```
# Register Map for PLC:
# MW0 = Power (0/1)
# MW1 = Brightness (0-255)
# MW2 = Red (0-255)
# MW3 = Green (0-255)
# MW4 = Blue (0-255)

# Simple on/off with button
| I0.0 |---[/]---( MW0 )    # Button press toggles power

# Brightness control with potentiometer
| AIW0 |--[SCALE 0-255]--( MW1 )

# Emergency red alert
| M0.1 |--[MOVE 1]--( MW0 )      # Turn on
       |--[MOVE 255]--( MW1 )    # Full brightness
       |--[MOVE 255]--( MW2 )    # Red
       |--[MOVE 0]--( MW3 )      # Green
       |--[MOVE 0]--( MW4 )      # Blue
```

### Siemens TIA Portal (SCL)

```pascal
// Read current state
MB_Client(
    REQ := TRUE,
    MB_MODE := 0,  // Read input registers
    MB_ADDR := 0,
    MB_LEN := 5,
    MB_DATA_ADDR := P#DB10.DBX0.0,
    CONNECT := DB20.Modbus_Connection
);

// Write new color
IF "SetColorButton" THEN
    DB10.Power := 1;
    DB10.Brightness := 200;
    DB10.Red := "ColorRed";
    DB10.Green := "ColorGreen";
    DB10.Blue := "ColorBlue";
    
    MB_Client(
        REQ := TRUE,
        MB_MODE := 1,  // Write holding registers
        MB_ADDR := 0,
        MB_LEN := 5,
        MB_DATA_ADDR := P#DB10.DBX0.0,
        CONNECT := DB20.Modbus_Connection
    );
END_IF;
```

## Home Automation Integration

### Node-RED Flow

```json
[
    {
        "id": "modbus_read",
        "type": "modbus-read",
        "name": "Read WLED State",
        "topic": "",
        "showStatusActivities": false,
        "logIOActivities": false,
        "showErrors": false,
        "unitid": "1",
        "dataType": "InputRegister",
        "adr": "0",
        "quantity": "5",
        "rate": "2",
        "rateUnit": "s",
        "delayOnStart": false,
        "startDelayTime": "",
        "server": "modbus_server"
    },
    {
        "id": "modbus_write",
        "type": "modbus-write",
        "name": "Set WLED Color",
        "showStatusActivities": false,
        "showErrors": false,
        "unitid": "1",
        "dataType": "HoldingRegister",
        "adr": "2",
        "quantity": "3",
        "server": "modbus_server"
    }
]
```

### Home Assistant Configuration

```yaml
# configuration.yaml

modbus:
  - name: wled_bridge
    type: tcp
    host: 192.168.1.50
    port: 5020
    
    lights:
      - name: "WLED Strip"
        address: 0  # Power register
        write_address: 0
        brightness_address: 1
        brightness_write_address: 1
        rgb_address: 2
        rgb_write_address: 2
```

## Advanced Examples

### Example 6: Multi-Zone Control

```python
from pymodbus.client import ModbusTcpClient

class WLEDZone:
    def __init__(self, host, port=5020):
        self.client = ModbusTcpClient(host, port=port)
    
    def set_scene(self, scene_name):
        scenes = {
            'relax': {'power': 1, 'brightness': 100, 'color': (255, 100, 50)},
            'party': {'power': 1, 'brightness': 255, 'color': (255, 0, 255)},
            'work': {'power': 1, 'brightness': 200, 'color': (255, 255, 255)},
            'sleep': {'power': 1, 'brightness': 20, 'color': (255, 50, 0)},
        }
        
        if scene_name in scenes:
            scene = scenes[scene_name]
            self.client.write_register(0, scene['power'])
            self.client.write_register(1, scene['brightness'])
            self.client.write_registers(2, list(scene['color']))
            print(f"Scene '{scene_name}' activated")
    
    def close(self):
        self.client.close()

# Control multiple zones
living_room = WLEDZone('192.168.1.10', 5020)
bedroom = WLEDZone('192.168.1.11', 5021)

living_room.set_scene('party')
bedroom.set_scene('sleep')

living_room.close()
bedroom.close()
```

### Example 7: Event-Driven Notifications

```python
from pymodbus.client import ModbusTcpClient
import time

def notification_flash(client, color=(255, 0, 0), flashes=3):
    """Flash LEDs for notifications"""
    # Save current state
    result = client.read_input_registers(0, count=5)
    if not result.isError():
        saved_state = result.registers
        
        # Flash
        for _ in range(flashes):
            client.write_register(0, 1)
            client.write_registers(2, list(color))
            client.write_register(1, 255)
            time.sleep(0.3)
            client.write_register(0, 0)
            time.sleep(0.3)
        
        # Restore state
        client.write_register(0, saved_state[0])
        client.write_register(1, saved_state[1])
        client.write_registers(2, saved_state[2:5])

client = ModbusTcpClient('localhost', port=5020)

# Example: Flash red when door opens
notification_flash(client, color=(255, 0, 0), flashes=2)

# Example: Flash green when task completes
notification_flash(client, color=(0, 255, 0), flashes=1)

client.close()
```

## Tips and Best Practices

1. **Connection Management**: Reuse client connections when making multiple requests
2. **Error Handling**: Always check if result.isError() before using register values
3. **Timing**: Add small delays (0.1-0.5s) between commands for better reliability
4. **State Validation**: Read back values after writing to confirm changes
5. **Network**: Ensure stable network connection between bridge and WLED device
