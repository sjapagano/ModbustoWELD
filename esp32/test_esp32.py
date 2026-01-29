"""
ESP32 Test Client Example
Tests the ESP32 bridge from another computer on the network
"""

from pymodbus.client import ModbusTcpClient
import time

# Replace with your ESP32 IP address (shown in serial console)
ESP32_IP = "192.168.1.50"
ESP32_PORT = 5020

def test_esp32_bridge():
    """Test the ESP32 ModbustoWELD bridge"""
    
    print(f"Connecting to ESP32 bridge at {ESP32_IP}:{ESP32_PORT}...")
    client = ModbusTcpClient(ESP32_IP, port=ESP32_PORT)
    
    if not client.connect():
        print("ERROR: Could not connect to ESP32 bridge")
        print("Check:")
        print("1. ESP32 is powered on and running")
        print("2. IP address is correct (check serial console)")
        print("3. Both devices are on the same network")
        print("4. Port 5020 is not blocked")
        return
    
    print("✓ Connected successfully!\n")
    
    try:
        # Test 1: Read current state
        print("Test 1: Reading current WLED state...")
        result = client.read_input_registers(0, count=5)
        if not result.isError():
            power, brightness, red, green, blue = result.registers
            print(f"  Power: {'ON' if power else 'OFF'}")
            print(f"  Brightness: {brightness}")
            print(f"  Color: RGB({red}, {green}, {blue})\n")
        else:
            print(f"  ERROR: {result}\n")
        
        # Test 2: Turn on LEDs
        print("Test 2: Turning on LEDs...")
        client.write_register(0, 1)
        time.sleep(1)
        print("  ✓ Command sent\n")
        
        # Test 3: Set brightness
        print("Test 3: Setting brightness to 200...")
        client.write_register(1, 200)
        time.sleep(1)
        print("  ✓ Command sent\n")
        
        # Test 4: Rainbow sequence
        print("Test 4: Rainbow color sequence...")
        colors = [
            ("Red", 255, 0, 0),
            ("Orange", 255, 127, 0),
            ("Yellow", 255, 255, 0),
            ("Green", 0, 255, 0),
            ("Blue", 0, 0, 255),
            ("Indigo", 75, 0, 130),
            ("Violet", 148, 0, 211),
        ]
        
        for name, r, g, b in colors:
            print(f"  {name}...")
            client.write_registers(2, [r, g, b])
            time.sleep(1.5)
        print("  ✓ Rainbow complete!\n")
        
        # Test 5: Read final state
        print("Test 5: Reading final state...")
        result = client.read_input_registers(0, count=5)
        if not result.isError():
            power, brightness, red, green, blue = result.registers
            print(f"  Power: {'ON' if power else 'OFF'}")
            print(f"  Brightness: {brightness}")
            print(f"  Color: RGB({red}, {green}, {blue})\n")
        
        print("=" * 50)
        print("All tests completed successfully! ✓")
        print("=" * 50)
        print("\nYour ESP32 bridge is working correctly!")
        print(f"Connect your PLC or SCADA to {ESP32_IP}:{ESP32_PORT}")
        
    except Exception as e:
        print(f"ERROR during testing: {e}")
    finally:
        client.close()
        print("\nDisconnected from ESP32 bridge")

if __name__ == '__main__':
    test_esp32_bridge()
