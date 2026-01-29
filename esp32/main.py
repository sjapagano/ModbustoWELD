"""
ModbustoWELD for ESP32 MicroPython
Main application - Modbus TCP to WLED Bridge running on ESP32
"""

import network
import time
import gc
from machine import Pin

# Import local modules
from config import *
from wled_client import WLEDClient
from modbus_slave import ModbusTCPSlave

class ModbusWLEDBridge:
    """Main bridge application"""
    
    def __init__(self):
        self.wled_client = None
        self.modbus_slave = None
        self.wlan = None
        self.led = None
        self.running = False
        
        # Track last register values to detect changes
        self.last_values = {
            'power': None,
            'brightness': None,
            'red': None,
            'green': None,
            'blue': None,
            'effect': None
        }
        
        # LED for status indication (built-in LED on GPIO 2)
        try:
            self.led = Pin(2, Pin.OUT)
            self.led.value(0)
        except:
            self.led = None
    
    def connect_wifi(self):
        """Connect to WiFi network"""
        print("\n" + "="*50)
        print("ModbustoWELD Bridge for ESP32")
        print("="*50)
        
        self.wlan = network.WLAN(network.STA_IF)
        self.wlan.active(True)
        
        if not self.wlan.isconnected():
            print(f"[WiFi] Connecting to {WIFI_SSID}...")
            self.wlan.connect(WIFI_SSID, WIFI_PASSWORD)
            
            # Wait for connection with timeout
            timeout = 20
            while not self.wlan.isconnected() and timeout > 0:
                time.sleep(1)
                timeout -= 1
                print(".", end="")
            
            print()
            
            if not self.wlan.isconnected():
                print("[WiFi] Connection failed!")
                return False
        
        print(f"[WiFi] Connected!")
        print(f"[WiFi] IP Address: {self.wlan.ifconfig()[0]}")
        print(f"[WiFi] Netmask: {self.wlan.ifconfig()[1]}")
        print(f"[WiFi] Gateway: {self.wlan.ifconfig()[2]}")
        
        # Blink LED to indicate WiFi connected
        if self.led:
            for _ in range(3):
                self.led.value(1)
                time.sleep(0.1)
                self.led.value(0)
                time.sleep(0.1)
        
        return True
    
    def initialize(self):
        """Initialize all components"""
        # Connect to WiFi
        if not self.connect_wifi():
            return False
        
        # Initialize WLED client
        print(f"\n[WLED] Connecting to {WLED_HOST}:{WLED_PORT}")
        self.wled_client = WLEDClient(WLED_HOST, WLED_PORT)
        
        # Test WLED connection
        info = self.wled_client.get_info()
        if info:
            print(f"[WLED] Connected to: {info.get('name', 'Unknown')}")
            print(f"[WLED] Version: {info.get('ver', 'Unknown')}")
        else:
            print("[WLED] Warning: Could not connect to WLED device")
        
        # Initialize Modbus slave
        print(f"\n[Modbus] Starting server on port {MODBUS_PORT}")
        self.modbus_slave = ModbusTCPSlave(
            host='0.0.0.0',
            port=MODBUS_PORT,
            slave_id=MODBUS_SLAVE_ID
        )
        self.modbus_slave.start()
        
        print("\n" + "="*50)
        print("Bridge is running!")
        print(f"Connect Modbus clients to: {self.wlan.ifconfig()[0]}:{MODBUS_PORT}")
        print("="*50 + "\n")
        
        return True
    
    def update_wled_state(self):
        """Update input registers with current WLED state"""
        try:
            state = self.wled_client.get_state()
            if state:
                # Extract state information
                power = 1 if state.get('on', False) else 0
                brightness = state.get('bri', 0)
                
                # Get color from first segment
                seg = state.get('seg', [{}])[0] if state.get('seg') else {}
                col = seg.get('col', [[0, 0, 0]])[0] if seg.get('col') else [0, 0, 0]
                red = col[0] if len(col) > 0 else 0
                green = col[1] if len(col) > 1 else 0
                blue = col[2] if len(col) > 2 else 0
                
                # Update input registers
                self.modbus_slave.set_input_registers(0, [power, brightness, red, green, blue])
                
        except Exception as e:
            if DEBUG:
                print(f"[Bridge] Error updating WLED state: {e}")
    
    def process_commands(self):
        """Process commands from holding registers"""
        try:
            # Get current holding register values
            values = self.modbus_slave.get_holding_registers(0, 6)
            
            # Process power command
            if values[0] != self.last_values['power']:
                self.last_values['power'] = values[0]
                self.wled_client.set_power(bool(values[0]))
            
            # Process brightness command
            if values[1] != self.last_values['brightness']:
                self.last_values['brightness'] = values[1]
                self.wled_client.set_brightness(values[1])
            
            # Process color command (check if any RGB value changed)
            if (values[2] != self.last_values['red'] or
                values[3] != self.last_values['green'] or
                values[4] != self.last_values['blue']):
                self.last_values['red'] = values[2]
                self.last_values['green'] = values[3]
                self.last_values['blue'] = values[4]
                self.wled_client.set_color(values[2], values[3], values[4])
            
            # Process effect command
            if values[5] != self.last_values['effect']:
                self.last_values['effect'] = values[5]
                self.wled_client.set_effect(values[5])
                
        except Exception as e:
            if DEBUG:
                print(f"[Bridge] Error processing commands: {e}")
    
    def run(self):
        """Main run loop"""
        self.running = True
        last_update = 0
        
        try:
            while self.running:
                # Process Modbus requests (non-blocking)
                self.modbus_slave.process_requests()
                
                # Update WLED state periodically
                current_time = time.ticks_ms()
                if time.ticks_diff(current_time, last_update) >= UPDATE_INTERVAL:
                    last_update = current_time
                    
                    # Blink LED to show activity
                    if self.led:
                        self.led.value(1)
                    
                    # Process commands and update state
                    self.process_commands()
                    self.update_wled_state()
                    
                    # LED off
                    if self.led:
                        self.led.value(0)
                    
                    # Periodic garbage collection
                    gc.collect()
                
                # Small delay to prevent tight loop
                time.sleep_ms(10)
                
        except KeyboardInterrupt:
            print("\n[Bridge] Shutting down...")
        except Exception as e:
            print(f"[Bridge] Fatal error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the bridge"""
        self.running = False
        if self.modbus_slave:
            self.modbus_slave.stop()
        if self.led:
            self.led.value(0)
        print("[Bridge] Stopped")

def main():
    """Main entry point"""
    bridge = ModbusWLEDBridge()
    
    if bridge.initialize():
        bridge.run()
    else:
        print("[Bridge] Initialization failed")

if __name__ == '__main__':
    main()
