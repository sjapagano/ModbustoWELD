"""
Example script demonstrating the ESP32 Modbus TCP Client

This script shows how to use the ModbusTCPClient to communicate
with Modbus TCP servers from an ESP32.

Usage:
1. Upload modbus_client.py to your ESP32
2. Update the configuration below with your Modbus server details
3. Upload and run this script on your ESP32
"""

import time
from modbus_client import ModbusTCPClient

# Configuration
MODBUS_SERVER_HOST = "192.168.1.10"  # IP address of Modbus TCP server
MODBUS_SERVER_PORT = 502              # Standard Modbus TCP port
MODBUS_TIMEOUT = 5                    # Connection timeout in seconds

def main():
    """Main example function"""
    print("=" * 50)
    print("ESP32 Modbus TCP Client Example")
    print("=" * 50)
    
    # Create Modbus client
    client = ModbusTCPClient(
        host=MODBUS_SERVER_HOST,
        port=MODBUS_SERVER_PORT,
        timeout=MODBUS_TIMEOUT
    )
    
    # Connect to server
    print("\n[1] Connecting to Modbus server...")
    if not client.connect():
        print("ERROR: Failed to connect to Modbus server")
        print(f"Please verify server is running at {MODBUS_SERVER_HOST}:{MODBUS_SERVER_PORT}")
        return
    
    print("✓ Connected successfully!\n")
    
    try:
        # Example 1: Read holding registers
        print("[2] Reading holding registers 0-4...")
        values = client.read_holding_registers(address=0, count=5)
        if values:
            print(f"  Values: {values}")
            for i, value in enumerate(values):
                print(f"  Register {i}: {value}")
        else:
            print("  ERROR: Failed to read registers")
        
        time.sleep(1)
        
        # Example 2: Write single register
        print("\n[3] Writing value 100 to register 0...")
        success = client.write_register(address=0, value=100)
        if success:
            print("  ✓ Write successful")
        else:
            print("  ERROR: Write failed")
        
        time.sleep(1)
        
        # Example 3: Read back the value
        print("\n[4] Reading back register 0...")
        values = client.read_holding_registers(address=0, count=1)
        if values:
            print(f"  Value: {values[0]}")
        else:
            print("  ERROR: Failed to read register")
        
        time.sleep(1)
        
        # Example 4: Write multiple registers
        print("\n[5] Writing multiple values to registers 1-3...")
        success = client.write_registers(address=1, values=[50, 150, 200])
        if success:
            print("  ✓ Write successful")
        else:
            print("  ERROR: Write failed")
        
        time.sleep(1)
        
        # Example 5: Read input registers
        print("\n[6] Reading input registers 0-4...")
        values = client.read_input_registers(address=0, count=5)
        if values:
            print(f"  Values: {values}")
            for i, value in enumerate(values):
                print(f"  Input Register {i}: {value}")
        else:
            print("  ERROR: Failed to read input registers")
        
        time.sleep(1)
        
        # Example 6: Multiple read/write operations
        print("\n[7] Demonstrating multiple operations...")
        for i in range(3):
            print(f"  Iteration {i+1}:")
            
            # Write a value
            test_value = 10 + (i * 10)
            if client.write_register(address=5, value=test_value):
                print(f"    Wrote {test_value} to register 5")
            
            # Read it back
            values = client.read_holding_registers(address=5, count=1)
            if values:
                print(f"    Read back: {values[0]}")
            
            time.sleep(0.5)
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nERROR: {e}")
    finally:
        # Always close the connection
        print("\nClosing connection...")
        client.close()
        print("Done!")


def example_control_wled_bridge():
    """
    Example: Control a WLED device through a ModbustoWELD bridge
    
    This demonstrates controlling WLED via Modbus, where the ESP32
    acts as a Modbus client connecting to a ModbustoWELD bridge.
    """
    print("\n" + "=" * 50)
    print("Example: Controlling WLED via Modbus")
    print("=" * 50)
    
    # Connect to ModbustoWELD bridge
    client = ModbusTCPClient(
        host="192.168.1.20",  # ModbustoWELD bridge IP
        port=5020             # ModbustoWELD default port
    )
    
    if not client.connect():
        print("ERROR: Cannot connect to ModbustoWELD bridge")
        return
    
    print("Connected to ModbustoWELD bridge")
    
    try:
        # Turn on WLED
        print("\n[1] Turning on WLED...")
        client.write_register(0, 1)  # Register 0 = Power
        time.sleep(1)
        
        # Set brightness to 128
        print("[2] Setting brightness to 128...")
        client.write_register(1, 128)  # Register 1 = Brightness
        time.sleep(1)
        
        # Set color to red
        print("[3] Setting color to RED...")
        client.write_registers(2, [255, 0, 0])  # Registers 2,3,4 = R,G,B
        time.sleep(2)
        
        # Set color to green
        print("[4] Setting color to GREEN...")
        client.write_registers(2, [0, 255, 0])
        time.sleep(2)
        
        # Set color to blue
        print("[5] Setting color to BLUE...")
        client.write_registers(2, [0, 0, 255])
        time.sleep(2)
        
        # Read current state
        print("\n[6] Reading current WLED state...")
        state = client.read_input_registers(0, 5)
        if state:
            print(f"  Power: {'ON' if state[0] else 'OFF'}")
            print(f"  Brightness: {state[1]}")
            print(f"  Color: RGB({state[2]}, {state[3]}, {state[4]})")
        
        print("\n✓ WLED control example completed!")
        
    finally:
        client.close()


if __name__ == '__main__':
    # Run basic examples
    main()
    
    # Uncomment to run WLED control example
    # example_control_wled_bridge()
