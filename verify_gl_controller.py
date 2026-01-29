#!/usr/bin/env python3
"""
GL-C-618WL Compatibility Verification Script

This script helps verify if your GL-C-618WL controller is compatible
with ModbustoWELD by testing WLED API connectivity and functionality.
"""

import sys
import requests
import argparse
import time
from typing import Optional, Dict, Any

class GLControllerVerifier:
    """Verify GL-C-618WL controller compatibility with ModbustoWELD"""
    
    def __init__(self, host: str, port: int = 80):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.results = {
            'connectivity': False,
            'wled_api': False,
            'info_endpoint': False,
            'state_endpoint': False,
            'control_test': False,
            'version': None,
            'device_name': None
        }
    
    def print_header(self):
        """Print verification header"""
        print("=" * 70)
        print("GL-C-618WL Compatibility Verification for ModbustoWELD")
        print("=" * 70)
        print(f"Testing controller at: {self.base_url}")
        print()
    
    def test_connectivity(self) -> bool:
        """Test basic HTTP connectivity"""
        print("[1/5] Testing basic connectivity...")
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code < 500:  # Any response that's not server error
                print(f"  ✓ Controller responds to HTTP requests")
                print(f"  ✓ Status code: {response.status_code}")
                self.results['connectivity'] = True
                return True
            else:
                print(f"  ✗ Unexpected status code: {response.status_code}")
                return False
        except requests.exceptions.Timeout:
            print(f"  ✗ Connection timeout - check IP address and network")
            return False
        except requests.exceptions.ConnectionError:
            print(f"  ✗ Connection failed - controller not reachable")
            return False
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return False
    
    def test_wled_info(self) -> bool:
        """Test WLED /json/info endpoint"""
        print("\n[2/5] Testing WLED info endpoint...")
        try:
            response = requests.get(f"{self.base_url}/json/info", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.results['info_endpoint'] = True
                self.results['version'] = data.get('ver', 'Unknown')
                self.results['device_name'] = data.get('name', 'Unknown')
                
                print(f"  ✓ WLED info endpoint responds")
                print(f"  ✓ Device name: {self.results['device_name']}")
                print(f"  ✓ WLED version: {self.results['version']}")
                print(f"  ✓ Architecture: {data.get('arch', 'Unknown')}")
                
                # Check version compatibility
                version = self.results['version']
                if version and version.startswith('0.'):
                    version_parts = version.split('.')
                    if len(version_parts) >= 2:
                        major, minor = int(version_parts[0]), int(version_parts[1])
                        if major == 0 and minor >= 13:
                            print(f"  ✓ Version compatible (0.13.0+)")
                        else:
                            print(f"  ⚠ Version may be too old (recommend 0.13.0+)")
                
                return True
            else:
                print(f"  ✗ Endpoint returned status {response.status_code}")
                print(f"  ✗ This does NOT appear to be a WLED device")
                return False
        except requests.exceptions.RequestException as e:
            print(f"  ✗ Cannot access WLED info endpoint")
            print(f"  ✗ Error: {e}")
            print(f"  ✗ This does NOT appear to be running WLED firmware")
            return False
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            return False
    
    def test_wled_state(self) -> bool:
        """Test WLED /json/state endpoint"""
        print("\n[3/5] Testing WLED state endpoint...")
        try:
            response = requests.get(f"{self.base_url}/json/state", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.results['state_endpoint'] = True
                
                print(f"  ✓ WLED state endpoint responds")
                print(f"  ✓ Power state: {'ON' if data.get('on') else 'OFF'}")
                print(f"  ✓ Brightness: {data.get('bri', 'Unknown')}")
                
                # Get color info if available
                segments = data.get('seg', [])
                if segments:
                    colors = segments[0].get('col', [[]])[0]
                    if len(colors) >= 3:
                        print(f"  ✓ Color (RGB): {colors[0]}, {colors[1]}, {colors[2]}")
                
                self.results['wled_api'] = True
                return True
            else:
                print(f"  ✗ Endpoint returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"  ✗ Cannot access WLED state endpoint: {e}")
            return False
    
    def test_wled_control(self) -> bool:
        """Test WLED control (write to device)"""
        print("\n[4/5] Testing WLED control...")
        print("  This will briefly change your LED settings...")
        
        # Save current state
        try:
            response = requests.get(f"{self.base_url}/json/state", timeout=5)
            original_state = response.json() if response.status_code == 200 else None
        except:
            original_state = None
        
        try:
            # Test turning on
            print("  Testing: Turn ON...")
            response = requests.post(
                f"{self.base_url}/json/state",
                json={"on": True},
                timeout=5
            )
            if response.status_code != 200:
                print(f"  ✗ Failed to turn on (status {response.status_code})")
                return False
            
            time.sleep(0.5)
            
            # Test brightness
            print("  Testing: Set brightness to 128...")
            response = requests.post(
                f"{self.base_url}/json/state",
                json={"bri": 128},
                timeout=5
            )
            if response.status_code != 200:
                print(f"  ✗ Failed to set brightness (status {response.status_code})")
                return False
            
            time.sleep(0.5)
            
            # Test color
            print("  Testing: Set color to blue...")
            response = requests.post(
                f"{self.base_url}/json/state",
                json={"seg": [{"col": [[0, 0, 255]]}]},
                timeout=5
            )
            if response.status_code != 200:
                print(f"  ✗ Failed to set color (status {response.status_code})")
                return False
            
            time.sleep(0.5)
            
            # Restore original state
            if original_state:
                print("  Restoring original state...")
                requests.post(
                    f"{self.base_url}/json/state",
                    json=original_state,
                    timeout=5
                )
            
            print(f"  ✓ Successfully controlled device via WLED API")
            self.results['control_test'] = True
            return True
            
        except Exception as e:
            print(f"  ✗ Control test failed: {e}")
            return False
    
    def test_modbus_compatibility(self) -> bool:
        """Test compatibility with ModbustoWELD register map"""
        print("\n[5/5] Testing ModbustoWELD register map compatibility...")
        
        # Verify all required fields are accessible
        required_fields = ['on', 'bri', 'seg']
        
        try:
            response = requests.get(f"{self.base_url}/json/state", timeout=5)
            if response.status_code != 200:
                print(f"  ✗ Cannot access state endpoint")
                return False
            
            data = response.json()
            
            for field in required_fields:
                if field in data:
                    print(f"  ✓ Required field '{field}' present")
                else:
                    print(f"  ✗ Required field '{field}' missing")
                    return False
            
            # Check segment structure
            segments = data.get('seg', [])
            if segments and 'col' in segments[0]:
                print(f"  ✓ Color data structure correct")
            else:
                print(f"  ⚠ Color data structure unexpected")
            
            print(f"  ✓ Device compatible with ModbustoWELD register map")
            return True
            
        except Exception as e:
            print(f"  ✗ Compatibility check failed: {e}")
            return False
    
    def print_summary(self):
        """Print verification summary"""
        print("\n" + "=" * 70)
        print("VERIFICATION SUMMARY")
        print("=" * 70)
        
        all_passed = (
            self.results['connectivity'] and
            self.results['wled_api'] and
            self.results['info_endpoint'] and
            self.results['state_endpoint'] and
            self.results['control_test']
        )
        
        if all_passed:
            print("\n✅ GL-C-618WL IS COMPATIBLE with ModbustoWELD!")
            print()
            print("Your controller:")
            print(f"  • Name: {self.results['device_name']}")
            print(f"  • WLED Version: {self.results['version']}")
            print(f"  • HTTP API: Working")
            print(f"  • Control: Working")
            print()
            print("Next steps:")
            print("  1. Configure ModbustoWELD with this device IP")
            print(f"     WLED_HOST = \"{self.host}\"")
            print("  2. Start the ModbustoWELD bridge")
            print("  3. Connect your Modbus client to the bridge")
            print()
        else:
            print("\n❌ GL-C-618WL is NOT currently compatible")
            print()
            print("Issues found:")
            if not self.results['connectivity']:
                print("  ✗ Cannot connect to controller")
                print("    → Check IP address and network connection")
            if not self.results['info_endpoint'] or not self.results['state_endpoint']:
                print("  ✗ WLED API not detected")
                print("    → Controller may not be running WLED firmware")
                print("    → Consider flashing WLED firmware (see COMPATIBILITY.md)")
            if not self.results['control_test']:
                print("  ✗ Cannot control device")
                print("    → WLED API may not be functioning correctly")
            print()
            print("For help, see:")
            print("  • COMPATIBILITY.md - Hardware compatibility guide")
            print("  • https://github.com/Aircoookie/WLED - WLED firmware")
        
        print("=" * 70)
        
        return 0 if all_passed else 1
    
    def run_verification(self) -> int:
        """Run complete verification"""
        self.print_header()
        
        # Run all tests
        if not self.test_connectivity():
            self.print_summary()
            return 1
        
        if not self.test_wled_info():
            self.print_summary()
            return 1
        
        self.test_wled_state()
        self.test_wled_control()
        self.test_modbus_compatibility()
        
        return self.print_summary()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Verify GL-C-618WL controller compatibility with ModbustoWELD'
    )
    parser.add_argument(
        'host',
        help='IP address or hostname of GL-C-618WL controller'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=80,
        help='HTTP port (default: 80)'
    )
    
    args = parser.parse_args()
    
    verifier = GLControllerVerifier(args.host, args.port)
    sys.exit(verifier.run_verification())


if __name__ == '__main__':
    main()
