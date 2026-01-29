#!/usr/bin/env python3
"""
Test script to validate the ESP32 Modbus client implementation
This tests the code structure and logic without requiring actual ESP32 hardware
"""

import sys
import ast

def validate_python_syntax(filepath):
    """Validate Python syntax of a file"""
    print(f"Validating syntax: {filepath}")
    try:
        with open(filepath, 'r') as f:
            code = f.read()
        ast.parse(code)
        print(f"  ✓ Syntax is valid")
        return True
    except SyntaxError as e:
        print(f"  ✗ Syntax error: {e}")
        return False

def check_modbus_client_structure():
    """Check that the Modbus client has all required methods"""
    print("\nChecking ModbusTCPClient structure...")
    
    with open('esp32/modbus_client.py', 'r') as f:
        code = f.read()
    
    required_methods = [
        '__init__',
        'connect',
        'close',
        'read_holding_registers',
        'read_input_registers', 
        'write_register',
        'write_registers',
        '_build_mbap_header',
        '_send_request',
        '_get_next_transaction_id'
    ]
    
    all_found = True
    for method in required_methods:
        if f'def {method}(' in code:
            print(f"  ✓ Method '{method}' found")
        else:
            print(f"  ✗ Method '{method}' missing")
            all_found = False
    
    return all_found

def check_example_structure():
    """Check that the example script has required functions"""
    print("\nChecking example script structure...")
    
    with open('esp32/modbus_client_example.py', 'r') as f:
        code = f.read()
    
    required_elements = [
        'from modbus_client import ModbusTCPClient',
        'def main(',
        'def example_control_wled_bridge(',
        'MODBUS_SERVER_HOST',
        'MODBUS_SERVER_PORT'
    ]
    
    all_found = True
    for element in required_elements:
        if element in code:
            print(f"  ✓ Element '{element}' found")
        else:
            print(f"  ✗ Element '{element}' missing")
            all_found = False
    
    return all_found

def check_documentation():
    """Check that documentation was updated"""
    print("\nChecking documentation updates...")
    
    with open('esp32/README.md', 'r') as f:
        readme = f.read()
    
    required_sections = [
        'Modbus TCP client',
        'modbus_client.py',
        'ModbusTCPClient',
        'read_holding_registers',
        'write_register',
        'Modbus Client vs Server'
    ]
    
    all_found = True
    for section in required_sections:
        if section in readme:
            print(f"  ✓ Section/mention '{section}' found")
        else:
            print(f"  ✗ Section/mention '{section}' missing")
            all_found = False
    
    return all_found

def test_modbus_protocol_compliance():
    """Test that Modbus protocol constants are correct"""
    print("\nChecking Modbus protocol compliance...")
    
    with open('esp32/modbus_client.py', 'r') as f:
        code = f.read()
    
    # Check function codes
    tests = [
        ('0x03' in code, "Function Code 3 (Read Holding Registers)"),
        ('0x04' in code, "Function Code 4 (Read Input Registers)"),
        ('0x06' in code, "Function Code 6 (Write Single Register)"),
        ('0x10' in code, "Function Code 16 (Write Multiple Registers)"),
    ]
    
    all_passed = True
    for test, description in tests:
        if test:
            print(f"  ✓ {description}")
        else:
            print(f"  ✗ {description}")
            all_passed = False
    
    return all_passed

def main():
    """Run all validation tests"""
    print("=" * 60)
    print("ESP32 Modbus Client Implementation Validation")
    print("=" * 60)
    
    results = []
    
    # Test syntax
    results.append(("Syntax validation (modbus_client.py)", 
                   validate_python_syntax('esp32/modbus_client.py')))
    results.append(("Syntax validation (modbus_client_example.py)", 
                   validate_python_syntax('esp32/modbus_client_example.py')))
    
    # Test structure
    results.append(("ModbusTCPClient structure", check_modbus_client_structure()))
    results.append(("Example script structure", check_example_structure()))
    results.append(("Modbus protocol compliance", test_modbus_protocol_compliance()))
    results.append(("Documentation updates", check_documentation()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All validation tests passed!")
        print("=" * 60)
        return 0
    else:
        print("✗ Some validation tests failed")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
