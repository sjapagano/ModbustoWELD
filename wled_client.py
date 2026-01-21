"""
WLED API Client
Handles communication with WLED devices via HTTP API
"""

import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class WLEDClient:
    """Client for communicating with WLED devices"""
    
    def __init__(self, host: str, port: int = 80):
        """
        Initialize WLED client
        
        Args:
            host: WLED device hostname or IP address
            port: WLED device HTTP port (default: 80)
        """
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        logger.info(f"Initialized WLED client for {self.base_url}")
    
    def get_state(self) -> Optional[Dict[str, Any]]:
        """
        Get current WLED state
        
        Returns:
            Dictionary with current state or None on error
        """
        try:
            response = requests.get(f"{self.base_url}/json/state", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting WLED state: {e}")
            return None
    
    def get_info(self) -> Optional[Dict[str, Any]]:
        """
        Get WLED device information
        
        Returns:
            Dictionary with device info or None on error
        """
        try:
            response = requests.get(f"{self.base_url}/json/info", timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting WLED info: {e}")
            return None
    
    def set_power(self, on: bool) -> bool:
        """
        Turn WLED on or off
        
        Args:
            on: True to turn on, False to turn off
            
        Returns:
            True on success, False on error
        """
        try:
            data = {"on": on}
            response = requests.post(f"{self.base_url}/json/state", json=data, timeout=5)
            response.raise_for_status()
            logger.info(f"Set WLED power to {on}")
            return True
        except Exception as e:
            logger.error(f"Error setting WLED power: {e}")
            return False
    
    def set_brightness(self, brightness: int) -> bool:
        """
        Set WLED brightness (0-255)
        
        Args:
            brightness: Brightness value (0-255)
            
        Returns:
            True on success, False on error
        """
        try:
            brightness = max(0, min(255, brightness))
            data = {"bri": brightness}
            response = requests.post(f"{self.base_url}/json/state", json=data, timeout=5)
            response.raise_for_status()
            logger.info(f"Set WLED brightness to {brightness}")
            return True
        except Exception as e:
            logger.error(f"Error setting WLED brightness: {e}")
            return False
    
    def set_color(self, red: int, green: int, blue: int) -> bool:
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
            red = max(0, min(255, red))
            green = max(0, min(255, green))
            blue = max(0, min(255, blue))
            data = {"seg": [{"col": [[red, green, blue]]}]}
            response = requests.post(f"{self.base_url}/json/state", json=data, timeout=5)
            response.raise_for_status()
            logger.info(f"Set WLED color to RGB({red}, {green}, {blue})")
            return True
        except Exception as e:
            logger.error(f"Error setting WLED color: {e}")
            return False
    
    def set_effect(self, effect_id: int) -> bool:
        """
        Set WLED effect
        
        Args:
            effect_id: Effect ID number
            
        Returns:
            True on success, False on error
        """
        try:
            data = {"seg": [{"fx": effect_id}]}
            response = requests.post(f"{self.base_url}/json/state", json=data, timeout=5)
            response.raise_for_status()
            logger.info(f"Set WLED effect to {effect_id}")
            return True
        except Exception as e:
            logger.error(f"Error setting WLED effect: {e}")
            return False
