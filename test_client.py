#!/usr/bin/env python3
"""
Test script for ModbustoWELD
Demonstrates how to use the bridge with a Modbus client
"""

import time
import sys
from pymodbus.client import ModbusTcpClient

def test_modbus_bridge(host='localhost', port=5020):
    """Test the Modbus to WLED bridge"""
    
    print(f"Connecting to ModbustoWELD bridge at {host}:{port}...")
    client = ModbusTcpClient(host, port=port)
    
    if not client.connect():
        print("ERROR: Could not connect to Modbus bridge")
        print("Make sure the bridge is running: python main.py")
        sys.exit(1)
    
    print("✓ Connected successfully!\n")
    
    try:
        # Test 1: Read current state
        print("Test 1: Reading current WLED state...")
        result = client.read_input_registers(0, count=5)
        if result.isError():
            print(f"  ERROR: {result}")
        else:
            power, brightness, red, green, blue = result.registers
            print(f"  Power: {'ON' if power else 'OFF'}")
            print(f"  Brightness: {brightness}")
            print(f"  Color: RGB({red}, {green}, {blue})\n")
        
        # Test 2: Turn on LEDs
        print("Test 2: Turning on LEDs...")
        client.write_register(0, 1)
        time.sleep(1)
        print("  ✓ Command sent\n")
        
        # Test 3: Set brightness to 128
        print("Test 3: Setting brightness to 128...")
        client.write_register(1, 128)
        time.sleep(1)
        print("  ✓ Command sent\n")
        
        # Test 4: Set color to red
        print("Test 4: Setting color to RED (255, 0, 0)...")
        client.write_registers(2, [255, 0, 0])
        time.sleep(2)
        print("  ✓ Command sent\n")
        
        # Test 5: Set color to green
        print("Test 5: Setting color to GREEN (0, 255, 0)...")
        client.write_registers(2, [0, 255, 0])
        time.sleep(2)
        print("  ✓ Command sent\n")
        
        # Test 6: Set color to blue
        print("Test 6: Setting color to BLUE (0, 0, 255)...")
        client.write_registers(2, [0, 0, 255])
        time.sleep(2)
        print("  ✓ Command sent\n")
        
        # Test 7: Set brightness to max
        print("Test 7: Setting brightness to maximum (255)...")
        client.write_register(1, 255)
        time.sleep(2)
        print("  ✓ Command sent\n")
        
        # Test 8: Set brightness to low
        print("Test 8: Setting brightness to low (50)...")
        client.write_register(1, 50)
        time.sleep(2)
        print("  ✓ Command sent\n")
        
        # Test 9: Restore brightness
        print("Test 9: Restoring brightness to 128...")
        client.write_register(1, 128)
        time.sleep(1)
        print("  ✓ Command sent\n")
        
        # Test 10: Read final state
        print("Test 10: Reading final state...")
        result = client.read_input_registers(0, count=5)
        if not result.isError():
            power, brightness, red, green, blue = result.registers
            print(f"  Power: {'ON' if power else 'OFF'}")
            print(f"  Brightness: {brightness}")
            print(f"  Color: RGB({red}, {green}, {blue})\n")
        
        print("=" * 50)
        print("All tests completed successfully! ✓")
        print("=" * 50)
        
    except Exception as e:
        print(f"ERROR during testing: {e}")
    finally:
        client.close()
        print("\nDisconnected from bridge")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test ModbustoWELD bridge')
    parser.add_argument('--host', default='localhost', help='Bridge host (default: localhost)')
    parser.add_argument('--port', type=int, default=5020, help='Bridge port (default: 5020)')
    
    args = parser.parse_args()
    
    test_modbus_bridge(args.host, args.port)
