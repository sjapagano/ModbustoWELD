"""
WLED Client for ESP32 MicroPython
Handles communication with WLED devices via HTTP API
"""

import urequests as requests
import ujson as json

class WLEDClient:
    """Client for communicating with WLED devices"""
    
    def __init__(self, host, port=80):
        """
        Initialize WLED client
        
        Args:
            host: WLED device hostname or IP address
            port: WLED device HTTP port (default: 80)
        """
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        print(f"[WLED] Initialized client for {self.base_url}")
    
    def get_state(self):
        """
        Get current WLED state
        
        Returns:
            Dictionary with current state or None on error
        """
        try:
            response = requests.get(f"{self.base_url}/json/state", timeout=5)
            if response.status_code == 200:
                data = response.json()
                response.close()
                return data
            response.close()
            return None
        except Exception as e:
            print(f"[WLED] Error getting state: {e}")
            return None
    
    def get_info(self):
        """
        Get WLED device information
        
        Returns:
            Dictionary with device info or None on error
        """
        try:
            response = requests.get(f"{self.base_url}/json/info", timeout=5)
            if response.status_code == 200:
                data = response.json()
                response.close()
                return data
            response.close()
            return None
        except Exception as e:
            print(f"[WLED] Error getting info: {e}")
            return None
    
    def set_power(self, on):
        """
        Turn WLED on or off
        
        Args:
            on: True to turn on, False to turn off
            
        Returns:
            True on success, False on error
        """
        try:
            data = json.dumps({"on": on})
            response = requests.post(
                f"{self.base_url}/json/state",
                data=data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            success = response.status_code == 200
            response.close()
            if success:
                print(f"[WLED] Set power to {on}")
            return success
        except Exception as e:
            print(f"[WLED] Error setting power: {e}")
            return False
    
    def set_brightness(self, brightness):
        """
        Set WLED brightness (0-255)
        
        Args:
            brightness: Brightness value (0-255)
            
        Returns:
            True on success, False on error
        """
        try:
            brightness = max(0, min(255, int(brightness)))
            data = json.dumps({"bri": brightness})
            response = requests.post(
                f"{self.base_url}/json/state",
                data=data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            success = response.status_code == 200
            response.close()
            if success:
                print(f"[WLED] Set brightness to {brightness}")
            return success
        except Exception as e:
            print(f"[WLED] Error setting brightness: {e}")
            return False
    
    def set_color(self, red, green, blue):
        """
        Set WLED color (RGB)
        
        Args:
            red: Red value (0-255)
            green: Green value (0-255)
            blue: Blue value (0-255)
            
        Returns:
            True on success, False on error
        """
        try:
            red = max(0, min(255, int(red)))
            green = max(0, min(255, int(green)))
            blue = max(0, min(255, int(blue)))
            data = json.dumps({"seg": [{"col": [[red, green, blue]]}]})
            response = requests.post(
                f"{self.base_url}/json/state",
                data=data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            success = response.status_code == 200
            response.close()
            if success:
                print(f"[WLED] Set color to RGB({red}, {green}, {blue})")
            return success
        except Exception as e:
            print(f"[WLED] Error setting color: {e}")
            return False
    
    def set_effect(self, effect_id):
        """
        Set WLED effect
        
        Args:
            effect_id: Effect ID number
            
        Returns:
            True on success, False on error
        """
        try:
            data = json.dumps({"seg": [{"fx": int(effect_id)}]})
            response = requests.post(
                f"{self.base_url}/json/state",
                data=data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            success = response.status_code == 200
            response.close()
            if success:
                print(f"[WLED] Set effect to {effect_id}")
            return success
        except Exception as e:
            print(f"[WLED] Error setting effect: {e}")
            return False
