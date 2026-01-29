# ESP32 Quick Start Guide

Get your ModbustoWELD bridge running on ESP32 in 15 minutes!

## What You Need

- ESP32 board (any ESP32-DevKit variant)
- USB cable
- Computer with Python installed
- WiFi network (2.4 GHz)
- WLED device on the same network

## Step-by-Step Installation

### 1. Install Tools (One Time)

```bash
pip install esptool mpremote
```

### 2. Download MicroPython

```bash
cd esp32
wget https://micropython.org/resources/firmware/esp32-20230426-v1.20.0.bin
```

### 3. Configure WiFi and WLED

Edit `config.py`:
```python
WIFI_SSID = "YourWiFiName"
WIFI_PASSWORD = "YourWiFiPassword"
WLED_HOST = "192.168.1.100"  # Your WLED IP
```

### 4. Connect ESP32

- Plug ESP32 into USB port
- Find the port:
  - Linux/Mac: Usually `/dev/ttyUSB0`
  - Windows: Usually `COM3` or `COM4`

### 5. Flash and Upload

```bash
./install.sh
```

Choose option 3 (Full setup) and follow prompts.

### 6. Test It!

The script will show you the ESP32's IP address. From another computer:

```python
from pymodbus.client import ModbusTcpClient

# Replace with your ESP32 IP
client = ModbusTcpClient('192.168.1.50', port=5020)

# Turn on LEDs
client.write_register(0, 1)

# Set to bright blue
client.write_register(1, 255)
client.write_registers(2, [0, 0, 255])

client.close()
```

## Common Issues

### "Device not found"
- Try different USB cable (some are charge-only)
- Press and hold BOOT button while connecting
- Check port permissions: `sudo usermod -a -G dialout $USER`

### "WiFi connection failed"
- Ensure 2.4 GHz network (ESP32 doesn't support 5 GHz)
- Check SSID and password in config.py
- Move ESP32 closer to router

### "Can't import urequests"
- MicroPython might not be installed correctly
- Re-run install.sh option 1

## What's Happening?

When you power on the ESP32:
1. Connects to WiFi (LED blinks 3 times when connected)
2. Connects to WLED device
3. Starts Modbus TCP server on port 5020
4. LED blinks slowly to show it's running

## Auto-Start on Boot

To make it start automatically when powered:

```bash
mpremote connect /dev/ttyUSB0
# In the MicroPython prompt:
>>> f = open('boot.py', 'w')
>>> f.write('import main')
>>> f.close()
>>> import machine
>>> machine.reset()
```

## Monitoring

View live output:
```bash
mpremote connect /dev/ttyUSB0
```

Press Ctrl+] to exit.

## Next Steps

- Check out the full [ESP32 README](README.md) for advanced features
- Try the [examples](../EXAMPLES.md) with your ESP32
- Set up multiple ESP32 bridges for different WLED devices

## Help!

If something's not working:
1. Check the serial console output
2. Verify WiFi credentials
3. Test WLED manually: `curl http://<wled-ip>/json/state`
4. Join the discussion on GitHub Issues

## Power Your ESP32

Options:
- USB power bank (portable)
- USB phone charger (always-on)
- 5V regulated power supply (industrial)
- Solar with battery (off-grid)

ESP32 draws only ~80mA, so even a small power bank lasts days!
