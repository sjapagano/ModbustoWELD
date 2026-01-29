# GL-C-618WL Quick Verification Guide

## Will the GL-C-618WL work with ModbustoWELD?

**Short Answer:** It depends on whether it runs (or can run) WLED firmware.

## Quick Check (2 minutes)

### Step 1: Try accessing WLED API

```bash
# Replace with your GL-C-618WL's IP address
curl http://192.168.1.XXX/json/info
```

**If you get a JSON response with WLED version info:**
✅ **YES! Your GL-C-618WL is compatible!** Proceed to configuration.

**If you get an error or different response:**
⚠️ Continue to Step 2 to check if it can be flashed with WLED.

### Step 2: Use the automated verification script

```bash
# Run the compatibility checker
python verify_gl_controller.py 192.168.1.XXX
```

This will test all compatibility requirements and tell you:
- ✅ Compatible - Ready to use
- ⚠️ Needs WLED firmware flash
- ❌ Not compatible - Hardware limitations

## Results Interpretation

### ✅ Compatible (Already Running WLED)

**What this means:**
Your GL-C-618WL is already running WLED firmware and is ready to use with ModbustoWELD immediately.

**Next steps:**
1. Note your controller's IP address
2. Update `config.yaml`:
   ```yaml
   wled:
     host: "192.168.1.XXX"  # Your GL-C-618WL IP
     port: 80
   ```
3. Start ModbustoWELD: `python main.py`
4. Test with Modbus client (see [EXAMPLES.md](EXAMPLES.md))

### ⚠️ Needs WLED Firmware (ESP8266/ESP32 Based)

**What this means:**
Your GL-C-618WL uses an ESP8266 or ESP32 chip but isn't running WLED firmware yet. You can flash it with WLED to make it compatible.

**Next steps:**
1. Visit https://install.wled.me/
2. Use web-based installer (Chrome/Edge browser required)
3. Connect GL-C-618WL via USB
4. Follow installation prompts
5. After flashing, run verification again

**Detailed instructions:** See [COMPATIBILITY.md](COMPATIBILITY.md#step-3-flash-wled-firmware-if-needed)

### ❌ Not Compatible (Different Hardware)

**What this means:**
Your GL-C-618WL uses non-ESP hardware or locked firmware that cannot be replaced with WLED.

**Options:**
1. **Use a different controller:**
   - QuinLED boards (purpose-built for WLED)
   - ESP32 DevKit board ($5-10)
   - Any ESP8266/ESP32-based LED controller
   
2. **Keep GL-C-618WL for other uses:**
   - This project is specifically for WLED devices
   - Your controller may work with other software

**Recommended alternatives:** See [COMPATIBILITY.md](COMPATIBILITY.md#alternative-controllers)

## Common GL-C-618WL Variants

### Type A: ESP-Based (Compatible ✅)
- **Chip:** ESP8266 or ESP32
- **Can flash WLED:** Yes
- **Example models:** GL-C-618WL-ESP8266, GL-C-618WL-ESP32
- **How to identify:** Open case, look for ESP chip markings

### Type B: Proprietary Chip (Not Compatible ❌)
- **Chip:** Tuya, Realtek, or other proprietary
- **Can flash WLED:** No
- **Alternative:** Use WLED-compatible controller
- **How to identify:** No ESP markings on chip

## Configuration Example

Once verified compatible, here's a complete configuration example:

### Python/PC Version (config.yaml)
```yaml
modbus:
  host: "0.0.0.0"
  port: 5020

wled:
  host: "192.168.1.100"  # GL-C-618WL IP
  port: 80

logging:
  level: "INFO"
```

### ESP32 Version (esp32/config.py)
```python
# WiFi Configuration
WIFI_SSID = "your_wifi_ssid"
WIFI_PASSWORD = "your_wifi_password"

# Modbus TCP Configuration
MODBUS_PORT = 5020
MODBUS_SLAVE_ID = 1

# WLED Configuration (GL-C-618WL)
WLED_HOST = "192.168.1.100"  # GL-C-618WL IP
WLED_PORT = 80

# Update interval (milliseconds)
UPDATE_INTERVAL = 500

# Debug mode
DEBUG = True
```

## Testing Your Setup

After configuration, test the complete system:

```python
#!/usr/bin/env python3
from pymodbus.client import ModbusTcpClient

# Connect to ModbustoWELD bridge
client = ModbusTcpClient('localhost', port=5020)

if client.connect():
    print("✓ Connected to ModbustoWELD bridge")
    
    # Turn on GL-C-618WL via Modbus
    client.write_register(0, 1)
    print("✓ Turned on LED")
    
    # Set brightness
    client.write_register(1, 128)
    print("✓ Set brightness to 128")
    
    # Set color to purple
    client.write_registers(2, [128, 0, 128])
    print("✓ Set color to purple")
    
    # Read status
    status = client.read_input_registers(0, 5)
    print(f"✓ Status: Power={status.registers[0]}, Brightness={status.registers[1]}")
    
    client.close()
    print("✓ Test complete!")
else:
    print("✗ Cannot connect to ModbustoWELD bridge")
```

## Troubleshooting

### Issue: Verification script can't connect
**Check:**
- GL-C-618WL is powered on
- Connected to same network
- IP address is correct
- No firewall blocking port 80

### Issue: WLED API responds but colors are wrong
**Solution:**
- Configure LED type in WLED settings
- Check color order (RGB vs GRB vs BGR)
- WLED Config → LED Preferences

### Issue: Flash fails with "Failed to connect"
**Solutions:**
- Hold BOOT/FLASH button during connection
- Try different USB cable
- Install USB drivers (CH340, CP2102)
- Use correct COM port

## Getting Help

1. **Run the verification script** first:
   ```bash
   python verify_gl_controller.py <your-ip>
   ```

2. **Check the full compatibility guide:**
   [COMPATIBILITY.md](COMPATIBILITY.md)

3. **WLED Resources:**
   - https://kno.wled.ge/
   - https://github.com/Aircoookie/WLED
   - WLED Discord community

4. **ModbustoWELD Issues:**
   - https://github.com/sjapagano/ModbustoWELD/issues

## Summary

| Scenario | Compatible? | Action Required |
|----------|-------------|-----------------|
| Already runs WLED | ✅ Yes | Configure and use immediately |
| ESP-based, no WLED | ⚠️ Maybe | Flash WLED firmware first |
| Proprietary chip | ❌ No | Use WLED-compatible alternative |
| Unknown | ❓ Check | Run `verify_gl_controller.py` |

**Bottom line:** The GL-C-618WL will work with ModbustoWELD if it runs (or can run) WLED firmware. The verification script will tell you definitively.
