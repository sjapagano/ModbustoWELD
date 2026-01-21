"""
Modbus TCP Server
Exposes WLED functionality via Modbus TCP registers
"""

import logging
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusDeviceContext,
    ModbusServerContext
)
from threading import Thread
import time
import asyncio

logger = logging.getLogger(__name__)


class ModbusWLEDServer:
    """
    Modbus TCP server that exposes WLED controls via Modbus registers
    
    Register Map:
    - Holding Register 0: Power (0=OFF, 1=ON)
    - Holding Register 1: Brightness (0-255)
    - Holding Register 2: Red (0-255)
    - Holding Register 3: Green (0-255)
    - Holding Register 4: Blue (0-255)
    - Holding Register 5: Effect ID (0-255+)
    
    - Input Register 0: Current Power State (0=OFF, 1=ON)
    - Input Register 1: Current Brightness (0-255)
    - Input Register 2: Current Red (0-255)
    - Input Register 3: Current Green (0-255)
    - Input Register 4: Current Blue (0-255)
    """
    
    def __init__(self, wled_client, host: str = "0.0.0.0", port: int = 5020):
        """
        Initialize Modbus server
        
        Args:
            wled_client: WLEDClient instance
            host: Modbus server host
            port: Modbus server port
        """
        self.wled_client = wled_client
        self.host = host
        self.port = port
        
        # Initialize data blocks
        # Holding registers (writable) - used for commands
        self.holding_registers = ModbusSequentialDataBlock(0, [0] * 100)
        
        # Input registers (read-only) - used for status
        self.input_registers = ModbusSequentialDataBlock(0, [0] * 100)
        
        # Coils and discrete inputs (not used in this implementation)
        self.coils = ModbusSequentialDataBlock(0, [0] * 100)
        self.discrete_inputs = ModbusSequentialDataBlock(0, [0] * 100)
        
        # Create device context
        self.device_context = ModbusDeviceContext(
            di=self.discrete_inputs,
            co=self.coils,
            hr=self.holding_registers,
            ir=self.input_registers
        )
        
        # Create server context
        self.context = ModbusServerContext(devices=self.device_context, single=True)
        
        self.server_thread = None
        self.update_thread = None
        self.running = False
        
        logger.info(f"Initialized Modbus server on {host}:{port}")
    
    def start(self):
        """Start the Modbus server and update thread"""
        self.running = True
        
        # Start update thread to sync WLED state and process commands
        self.update_thread = Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
        # Start Modbus TCP server
        logger.info(f"Starting Modbus TCP server on {self.host}:{self.port}")
        
        # Run the async server in sync mode
        asyncio.run(StartAsyncTcpServer(
            context=self.context,
            address=(self.host, self.port)
        ))
    
    def stop(self):
        """Stop the server"""
        self.running = False
        logger.info("Stopping Modbus server")
    
    def _update_loop(self):
        """Background thread to update WLED state and process commands"""
        logger.info("Starting update loop")
        
        # Track last written values to detect changes
        last_values = {
            'power': None,
            'brightness': None,
            'red': None,
            'green': None,
            'blue': None,
            'effect': None
        }
        
        while self.running:
            try:
                # Get current WLED state
                state = self.wled_client.get_state()
                if state:
                    # Update input registers with current state
                    power = 1 if state.get('on', False) else 0
                    brightness = state.get('bri', 0)
                    
                    # Get color from first segment
                    seg = state.get('seg', [{}])[0]
                    col = seg.get('col', [[0, 0, 0]])[0]
                    red = col[0] if len(col) > 0 else 0
                    green = col[1] if len(col) > 1 else 0
                    blue = col[2] if len(col) > 2 else 0
                    
                    # Update input registers
                    self.input_registers.setValues(0, [power, brightness, red, green, blue])
                
                # Check for changes in holding registers (commands from Modbus client)
                values = self.holding_registers.getValues(0, 6)
                
                # Process power command
                if values[0] != last_values['power']:
                    last_values['power'] = values[0]
                    self.wled_client.set_power(bool(values[0]))
                
                # Process brightness command
                if values[1] != last_values['brightness']:
                    last_values['brightness'] = values[1]
                    self.wled_client.set_brightness(values[1])
                
                # Process color command (check if any RGB value changed)
                if (values[2] != last_values['red'] or 
                    values[3] != last_values['green'] or 
                    values[4] != last_values['blue']):
                    last_values['red'] = values[2]
                    last_values['green'] = values[3]
                    last_values['blue'] = values[4]
                    self.wled_client.set_color(values[2], values[3], values[4])
                
                # Process effect command
                if values[5] != last_values['effect']:
                    last_values['effect'] = values[5]
                    self.wled_client.set_effect(values[5])
                
            except Exception as e:
                logger.error(f"Error in update loop: {e}")
            
            # Update every 500ms
            time.sleep(0.5)
