#!/usr/bin/env python3
"""
Integration Test for ModbustoWELD
Tests the complete system: Mock WLED -> Bridge -> Modbus Client
"""

import subprocess
import time
import sys
from pymodbus.client import ModbusTcpClient

def wait_for_server(host, port, timeout=10):
    """Wait for server to be ready"""
    import socket
    start = time.time()
    while time.time() - start < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            if result == 0:
                return True
        except:
            pass
        time.sleep(0.5)
    return False

def run_integration_test():
    """Run the full integration test"""
    print("=" * 60)
    print("ModbustoWELD Integration Test")
    print("=" * 60)
    
    # Start mock WLED server
    print("\n[1/3] Starting Mock WLED server...")
    mock_server = subprocess.Popen(
        ['python3', 'mock_wled_server.py', '--port', '8080'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Wait for mock server to start
    if not wait_for_server('localhost', 8080, timeout=5):
        print("ERROR: Mock WLED server failed to start")
        mock_server.terminate()
        return False
    print("✓ Mock WLED server started on port 8080")
    
    # Start Modbus bridge
    print("\n[2/3] Starting Modbus bridge...")
    bridge = subprocess.Popen(
        ['python3', 'main.py', '--config', 'config.test.yaml'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Wait for bridge to start
    if not wait_for_server('localhost', 5020, timeout=10):
        print("ERROR: Modbus bridge failed to start")
        bridge.terminate()
        mock_server.terminate()
        return False
    print("✓ Modbus bridge started on port 5020")
    
    # Give it a moment to stabilize
    time.sleep(2)
    
    # Run tests
    print("\n[3/3] Running Modbus client tests...")
    success = True
    
    try:
        client = ModbusTcpClient('localhost', port=5020)
        
        if not client.connect():
            print("ERROR: Could not connect to Modbus bridge")
            success = False
        else:
            print("✓ Connected to Modbus bridge")
            
            # Test 1: Turn on
            print("\nTest 1: Turn on LEDs")
            client.write_register(0, 1)
            time.sleep(1)
            result = client.read_input_registers(0, count=1)
            if not result.isError() and result.registers[0] == 1:
                print("  ✓ Power ON confirmed")
            else:
                print("  ✗ Power ON failed")
                success = False
            
            # Test 2: Set brightness
            print("\nTest 2: Set brightness to 200")
            client.write_register(1, 200)
            time.sleep(1)
            result = client.read_input_registers(1, count=1)
            if not result.isError() and result.registers[0] == 200:
                print("  ✓ Brightness 200 confirmed")
            else:
                print(f"  ✗ Brightness failed (got {result.registers[0] if not result.isError() else 'error'})")
                success = False
            
            # Test 3: Set color to red
            print("\nTest 3: Set color to red (255, 0, 0)")
            client.write_registers(2, [255, 0, 0])
            time.sleep(1)
            result = client.read_input_registers(2, count=3)
            if not result.isError() and result.registers == [255, 0, 0]:
                print("  ✓ Color RED confirmed")
            else:
                print(f"  ✗ Color failed (got {result.registers if not result.isError() else 'error'})")
                success = False
            
            # Test 4: Set color to green
            print("\nTest 4: Set color to green (0, 255, 0)")
            client.write_registers(2, [0, 255, 0])
            time.sleep(1)
            result = client.read_input_registers(2, count=3)
            if not result.isError() and result.registers == [0, 255, 0]:
                print("  ✓ Color GREEN confirmed")
            else:
                print(f"  ✗ Color failed (got {result.registers if not result.isError() else 'error'})")
                success = False
            
            # Test 5: Read complete state
            print("\nTest 5: Read complete state")
            result = client.read_input_registers(0, count=5)
            if not result.isError():
                power, brightness, red, green, blue = result.registers
                print(f"  Power: {'ON' if power else 'OFF'}")
                print(f"  Brightness: {brightness}")
                print(f"  Color: RGB({red}, {green}, {blue})")
                print("  ✓ State read successful")
            else:
                print("  ✗ State read failed")
                success = False
            
            client.close()
    
    except Exception as e:
        print(f"\nERROR during testing: {e}")
        success = False
    
    finally:
        # Cleanup
        print("\n" + "=" * 60)
        print("Cleaning up...")
        bridge.terminate()
        mock_server.terminate()
        
        # Wait for processes to end
        bridge.wait(timeout=5)
        mock_server.wait(timeout=5)
        print("✓ Cleanup complete")
    
    # Print results
    print("\n" + "=" * 60)
    if success:
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        return True
    else:
        print("✗ SOME TESTS FAILED")
        print("=" * 60)
        return False

if __name__ == '__main__':
    success = run_integration_test()
    sys.exit(0 if success else 1)
