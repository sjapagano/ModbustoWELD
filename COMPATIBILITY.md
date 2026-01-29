# Hardware Compatibility Guide

## Overview

ModbustoWELD is designed to work with devices running **WLED firmware**. This document explains hardware compatibility requirements and how to verify if your controller will work with the system.

## GL-C-618WL Controller Compatibility

### What is GL-C-618WL?

The GL-C-618WL is a WiFi LED controller typically based on ESP8266 or ESP32 microcontroller. To use it with ModbustoWELD, it must either:
1. Already run WLED firmware, or
2. Be capable of being flashed with WLED firmware

### Compatibility Requirements

✅ **COMPATIBLE IF:**
- Controller runs WLED firmware (v0.13.0 or later)
- Supports WLED HTTP JSON API
- Based on ESP8266 or ESP32 chip (can be flashed with WLED)
- Connected to the same network as your Modbus bridge

❌ **NOT COMPATIBLE IF:**
- Uses proprietary firmware that cannot be replaced
- Does not support WLED API protocol
- Hardware is locked/encrypted preventing firmware updates

### Verification Steps for GL-C-618WL

#### Step 1: Check Current Firmware

1. **Connect to your GL-C-618WL** via WiFi
2. **Access the controller's web interface** (usually at `http://192.168.4.1` or check your router for the device IP)
3. **Look for WLED interface:**
   - If you see the WLED web UI, you're good to go! ✅
   - If you see a different app/interface, continue to Step 2

#### Step 2: Check Hardware Specifications

1. **Identify the chip** used in your GL-C-618WL:
   - Open the device case if possible
   - Look for markings: ESP8266, ESP32, ESP32-S2, etc.
   - Check the product documentation or manufacturer's website

2. **Verify it's ESP-based:**
   - ESP8266-based controllers ✅ Compatible with WLED
   - ESP32-based controllers ✅ Compatible with WLED
   - Other chips (e.g., Tuya, Realtek) ⚠️ May require custom firmware/approach

#### Step 3: Flash WLED Firmware (if needed)

If your GL-C-618WL doesn't run WLED but is ESP-based:

1. **Download WLED firmware:**
   ```
   Visit: https://install.wled.me/
   Select appropriate version for your chip (ESP8266/ESP32)
   ```

2. **Flash using web installer:**
   - Connect controller via USB
   - Use Chrome/Edge browser
   - Visit https://install.wled.me/
   - Follow on-screen instructions

3. **Or use esptool manually:**
   ```bash
   # Install esptool
   pip install esptool
   
   # Flash WLED firmware
   esptool.py --chip esp8266 --port /dev/ttyUSB0 write_flash 0x0 WLED_firmware.bin
   # (Replace esp8266 with esp32 if using ESP32)
   ```

#### Step 4: Test WLED Connectivity

Once WLED is installed:

1. **Configure WiFi on WLED:**
   - Connect to WLED AP (WLED-AP)
   - Configure your network credentials
   - Note the assigned IP address

2. **Test WLED API:**
   ```bash
   # Get device info
   curl http://<WLED-IP>/json/info
   
   # Get current state
   curl http://<WLED-IP>/json/state
   
   # Turn on LEDs
   curl -X POST http://<WLED-IP>/json/state -H "Content-Type: application/json" -d '{"on":true}'
   ```

3. **If API responds correctly** → GL-C-618WL is compatible! ✅

#### Step 5: Configure ModbustoWELD

Update your configuration with the WLED device IP:

**config.yaml:**
```yaml
wled:
  host: "192.168.1.X"  # Your GL-C-618WL IP running WLED
  port: 80
```

**Or for ESP32 (esp32/config.py):**
```python
WLED_HOST = "192.168.1.X"  # Your GL-C-618WL IP
WLED_PORT = 80
```

### Testing ModbustoWELD with GL-C-618WL

Once configured, test the complete setup:

```python
from pymodbus.client import ModbusTcpClient

# Connect to ModbustoWELD bridge
client = ModbusTcpClient('localhost', port=5020)

# Turn on LEDs via Modbus
client.write_register(0, 1)

# Set brightness
client.write_register(1, 128)

# Set color to blue (RGB)
client.write_registers(2, [0, 0, 255])

# Read status
status = client.read_input_registers(0, 5)
print(f"Power: {status.registers[0]}")
print(f"Brightness: {status.registers[1]}")
print(f"Color: RGB({status.registers[2]}, {status.registers[3]}, {status.registers[4]})")

client.close()
```

### Common Issues with GL-C-618WL

#### Issue 1: Cannot Flash WLED
**Problem:** Device won't enter flash mode
**Solutions:**
- Hold BOOT/FLASH button while connecting USB
- Check USB drivers (CH340, CP2102)
- Try different USB cable
- Verify correct COM port

#### Issue 2: WiFi Connection Fails
**Problem:** WLED won't connect to WiFi
**Solutions:**
- Ensure 2.4 GHz WiFi (not 5 GHz)
- Check WiFi password
- Disable AP isolation on router
- Try different WiFi security mode (WPA2)

#### Issue 3: API Not Responding
**Problem:** WLED API doesn't respond
**Solutions:**
- Verify WLED version (v0.13.0+)
- Check firewall settings
- Test with `curl http://<IP>/json/info`
- Reboot WLED device

#### Issue 4: Colors Incorrect
**Problem:** LED colors don't match commands
**Solutions:**
- Configure LED type in WLED (WS2812B, SK6812, etc.)
- Check color order (RGB vs GRB vs BGR)
- Adjust in WLED settings: Config → LED Preferences

## Alternative Controllers

If GL-C-618WL is not compatible, consider these WLED-compatible alternatives:

### Officially Supported WLED Controllers:
- **QuinLED boards** - Purpose-built for WLED
- **dig-uno** - Popular WLED controller
- **ESP32 DevKit** - DIY option ($5-10)
- **WEMOS D1 Mini** - Compact ESP8266 option

### DIY ESP32/ESP8266 Build:
For maximum compatibility, build your own:
- ESP32 or ESP8266 dev board ($5-10)
- Level shifter (optional, for WS2812B)
- Power supply (5V for most LED strips)
- LED strip connector

## Technical Requirements Summary

### For GL-C-618WL or any controller:

**Hardware:**
- ESP8266 or ESP32 microcontroller
- WiFi capability (2.4 GHz)
- Sufficient GPIO pins for LED control
- 1MB+ flash memory

**Firmware:**
- WLED v0.13.0 or later recommended
- WLED v0.14.0+ tested with this project

**Network:**
- TCP/IP networking
- HTTP server capability
- JSON API support
- Same network segment as Modbus bridge

**LED Support:**
- WS2812B, WS2811, SK6812, APA102, or similar
- Configurable in WLED settings

## Getting Help

If you're having trouble verifying GL-C-618WL compatibility:

1. **Check WLED Documentation:**
   - https://kno.wled.ge/
   - https://github.com/Aircoookie/WLED

2. **WLED Community:**
   - WLED Discord server
   - Reddit: r/WLED

3. **ModbustoWELD Issues:**
   - https://github.com/sjapagano/ModbustoWELD/issues

## Summary: Will GL-C-618WL Work?

**YES** ✅ if:
- It already runs WLED firmware
- It's ESP8266/ESP32 based and you can flash WLED
- The device supports WLED HTTP JSON API

**NO** ❌ if:
- Hardware is locked/proprietary
- Not based on ESP chip
- Firmware cannot be replaced

**UNKNOWN** ⚠️ 
- Check with manufacturer if ESP-based
- Open device to identify chip
- Try WLED flash procedure

## Next Steps

1. Verify GL-C-618WL chip type (ESP8266/ESP32)
2. Flash WLED firmware if needed
3. Test WLED API connectivity
4. Configure ModbustoWELD with device IP
5. Run test script to verify end-to-end functionality

For detailed installation instructions, see:
- [Main README](README.md)
- [ESP32 README](esp32/README.md)
- [Examples](EXAMPLES.md)
