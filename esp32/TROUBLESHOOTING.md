# ESP32 Troubleshooting Guide

## Installation Issues

### Problem: "esptool not found"

**Solution:**
```bash
pip install esptool
# Or with pip3
pip3 install esptool
```

### Problem: "Permission denied: /dev/ttyUSB0"

**Linux Solution:**
```bash
sudo usermod -a -G dialout $USER
# Log out and log back in
```

**Quick fix (not permanent):**
```bash
sudo chmod 666 /dev/ttyUSB0
```

### Problem: "A serial exception error occurred"

**Solutions:**
1. Unplug and replug the USB cable
2. Try a different USB port
3. Use a different USB cable (data cable, not charge-only)
4. Press and hold BOOT button while connecting
5. Check if another program is using the port:
   ```bash
   lsof /dev/ttyUSB0
   ```

### Problem: MicroPython firmware won't flash

**Solutions:**
1. Erase flash first:
   ```bash
   esptool.py --port /dev/ttyUSB0 erase_flash
   ```
2. Try slower baud rate:
   ```bash
   esptool.py --port /dev/ttyUSB0 --baud 115200 write_flash -z 0x1000 firmware.bin
   ```
3. Hold BOOT button during flashing
4. Check ESP32 with multimeter (should be ~3.3V)

## WiFi Connection Issues

### Problem: "WiFi connection failed"

**Check 1: Frequency**
- ESP32 only supports 2.4 GHz WiFi
- Check your router settings
- Use a 2.4 GHz network

**Check 2: Credentials**
```python
# In config.py, make sure there are no extra spaces
WIFI_SSID = "MyNetwork"  # Exactly as shown in WiFi settings
WIFI_PASSWORD = "MyPassword123"
```

**Check 3: Signal Strength**
- Move ESP32 closer to router
- Use external antenna (if your board supports it)
- Avoid metal enclosures

**Check 4: Router Settings**
- Some routers block new devices
- Check MAC address filtering
- Temporarily disable WiFi security to test

### Problem: "Connected but can't reach WLED"

**Solutions:**
1. Verify both are on same network:
   ```bash
   # From PC, ping ESP32
   ping 192.168.1.50
   
   # From PC, ping WLED
   ping 192.168.1.100
   ```

2. Check WLED IP hasn't changed:
   - WLED might have DHCP address that changes
   - Set static IP in WLED settings
   - Or use hostname instead of IP (if supported)

3. Test WLED directly:
   ```bash
   curl http://192.168.1.100/json/state
   ```

## WLED Communication Issues

### Problem: "Error getting WLED state"

**Check 1: Network**
```python
# On ESP32, test in MicroPython REPL:
>>> import network
>>> wlan = network.WLAN(network.STA_IF)
>>> wlan.isconnected()
True
>>> wlan.ifconfig()
('192.168.1.50', '255.255.255.0', '192.168.1.1', '192.168.1.1')
```

**Check 2: HTTP Request**
```python
# On ESP32 REPL:
>>> import urequests
>>> response = urequests.get('http://192.168.1.100/json/state')
>>> response.text
# Should show JSON data
>>> response.close()
```

**Check 3: WLED Settings**
- Ensure WLED HTTP API is enabled
- Check WLED isn't in AP mode
- Verify WLED firmware version (0.13.0+)

### Problem: Commands don't work

**Solutions:**
1. Check Modbus connection:
   ```python
   from pymodbus.client import ModbusTcpClient
   client = ModbusTcpClient('192.168.1.50', port=5020)
   print(client.connect())  # Should be True
   ```

2. Enable debug mode in config.py:
   ```python
   DEBUG = True
   ```

3. Monitor serial console for errors:
   ```bash
   mpremote connect /dev/ttyUSB0
   ```

## Modbus Connection Issues

### Problem: "Can't connect to Modbus"

**Check 1: Port**
```bash
# Test if port is open
nc -zv 192.168.1.50 5020
# Or
telnet 192.168.1.50 5020
```

**Check 2: Firewall**
- Disable firewall temporarily to test
- Add rule for port 5020

**Check 3: IP Address**
- Double-check ESP32 IP from serial console
- ESP32 might have gotten different IP from DHCP

### Problem: "Connection timeout"

**Solutions:**
1. Increase client timeout:
   ```python
   client = ModbusTcpClient('192.168.1.50', port=5020, timeout=10)
   ```

2. Check ESP32 is still running:
   - LED should be blinking
   - Connect to serial console
   - Try resetting ESP32

3. Network latency:
   ```bash
   ping 192.168.1.50
   # Check response times
   ```

## Memory Issues

### Problem: "MemoryError" or ESP32 resets

**Solutions:**

1. Reduce update interval in config.py:
   ```python
   UPDATE_INTERVAL = 1000  # Slower updates = less memory
   ```

2. Disable debug:
   ```python
   DEBUG = False
   ```

3. Check memory in REPL:
   ```python
   >>> import gc
   >>> gc.collect()
   >>> gc.mem_free()
   # Should be > 50000
   ```

4. Reset ESP32 periodically:
   ```python
   # Add to main.py after some hours of runtime
   from machine import reset
   if uptime > 86400:  # 24 hours
       reset()
   ```

## Performance Issues

### Problem: Slow response times

**Solutions:**

1. Reduce update interval (trade-off with memory):
   ```python
   UPDATE_INTERVAL = 250  # Faster but uses more resources
   ```

2. Check WiFi signal strength:
   ```python
   >>> wlan.status('rssi')
   # Should be > -70 for good performance
   ```

3. Move ESP32 closer to router or WLED

### Problem: LED keeps blinking (restart loop)

**Causes:**
- Exception in code
- Memory exhaustion
- Corrupt flash

**Solutions:**
1. Connect serial console to see error
2. Reflash MicroPython
3. Check power supply (should be stable 3.3V)

## Code Issues

### Problem: "ImportError: no module named 'urequests'"

**Solution:**
MicroPython firmware might be minimal. Install network modules:
```python
# In MicroPython REPL:
>>> import upip
>>> upip.install('micropython-urequests')
```

Or use the full firmware build.

### Problem: Changes to code not taking effect

**Solutions:**
1. Make sure you uploaded the file:
   ```bash
   mpremote connect /dev/ttyUSB0 ls
   ```

2. Reset ESP32 after upload:
   ```python
   >>> import machine
   >>> machine.reset()
   ```

3. Check you edited the right file (ESP32, not PC version)

## Hardware Issues

### Problem: ESP32 gets hot

**Normal:** ESP32 gets warm during WiFi use

**Too hot:** If too hot to touch, check:
- Short circuit on board
- Power supply voltage (should be 3.3V or 5V USB)
- Damaged board

### Problem: Inconsistent behavior

**Solutions:**
1. Check power supply:
   - Use quality USB cable
   - Use powered USB hub if needed
   - Add 10µF capacitor near ESP32 power pins

2. Check for loose connections

3. Test with different ESP32 board

## Getting Help

Still stuck? Here's what to include when asking for help:

1. **Hardware:**
   - ESP32 board model
   - How it's powered

2. **Software:**
   - MicroPython version
   - Output from serial console
   - Full error messages

3. **Network:**
   - Can you ping ESP32?
   - Can you ping WLED?
   - Router model

4. **What you tried:**
   - Steps from this guide
   - Any changes to code

Post your issue on GitHub with this information!

## Quick Diagnostic Script

Run this in MicroPython REPL to check everything:

```python
import network
import urequests
import gc

print("=== ESP32 Diagnostics ===")

# Memory
gc.collect()
print(f"Free memory: {gc.mem_free()} bytes")

# WiFi
wlan = network.WLAN(network.STA_IF)
print(f"WiFi connected: {wlan.isconnected()}")
if wlan.isconnected():
    print(f"IP: {wlan.ifconfig()[0]}")
    print(f"RSSI: {wlan.status('rssi')} dBm")

# WLED test
try:
    r = urequests.get('http://192.168.1.100/json/info', timeout=5)
    print(f"WLED reachable: {r.status_code == 200}")
    r.close()
except:
    print("WLED reachable: False")

print("=== End Diagnostics ===")
```
