"""
Simple Modbus TCP Client for ESP32 MicroPython
Implements basic Modbus TCP client functionality
"""

import socket
import struct

class ModbusTCPClient:
    """
    Lightweight Modbus TCP client implementation for ESP32
    
    Supports:
    - Function Code 3: Read Holding Registers
    - Function Code 4: Read Input Registers  
    - Function Code 6: Write Single Register
    - Function Code 16: Write Multiple Registers
    """
    
    def __init__(self, host, port=502, timeout=5):
        """
        Initialize Modbus TCP client
        
        Args:
            host: Modbus server hostname or IP address
            port: Modbus server port (default: 502)
            timeout: Socket timeout in seconds (default: 5)
        """
        self.host = host
        self.port = port
        self.timeout = timeout
        self.socket = None
        self.transaction_id = 0
        self.unit_id = 1  # Default Modbus unit ID
        
        print(f"[Modbus Client] Initialized for {host}:{port}")
    
    def connect(self):
        """
        Connect to Modbus TCP server
        
        Returns:
            True on success, False on error
        """
        try:
            if self.socket:
                self.close()
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.host, self.port))
            print(f"[Modbus Client] Connected to {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"[Modbus Client] Connection error: {e}")
            return False
    
    def close(self):
        """Close the connection"""
        if self.socket:
            try:
                self.socket.close()
            except (OSError, Exception):
                pass
            self.socket = None
            print("[Modbus Client] Connection closed")
    
    def is_connected(self):
        """Check if connected to server"""
        return self.socket is not None
    
    def _get_next_transaction_id(self):
        """Get next transaction ID"""
        self.transaction_id = (self.transaction_id + 1) & 0xFFFF
        return self.transaction_id
    
    def _build_mbap_header(self, length):
        """Build Modbus Application Protocol header"""
        return struct.pack('>HHHB',
            self._get_next_transaction_id(),  # Transaction ID
            0,                                 # Protocol ID (0 for Modbus)
            length,                           # Length
            self.unit_id                      # Unit ID
        )
    
    def _send_request(self, function_code, data):
        """
        Send Modbus request and receive response
        
        Args:
            function_code: Modbus function code
            data: Request data bytes
            
        Returns:
            Response data bytes or None on error
        """
        if not self.is_connected():
            print("[Modbus Client] Not connected")
            return None
        
        try:
            # Build request PDU
            pdu = struct.pack('B', function_code) + data
            
            # Build MBAP header
            mbap = self._build_mbap_header(len(pdu) + 1)
            
            # Send request
            request = mbap + pdu
            self.socket.send(request)
            
            # Receive response
            # First, read MBAP header (7 bytes)
            header = self.socket.recv(7)
            if len(header) < 7:
                print("[Modbus Client] Incomplete header received")
                return None
            
            # Parse header
            trans_id, proto_id, length, unit_id = struct.unpack('>HHHB', header)
            
            # Read remaining data
            remaining = length - 1  # Length includes unit_id
            response_data = b''
            while len(response_data) < remaining:
                chunk = self.socket.recv(remaining - len(response_data))
                if not chunk:
                    break
                response_data += chunk
            
            # Check we have at least the function code byte
            if len(response_data) < 1:
                print("[Modbus Client] Empty response received")
                return None
            
            # Check function code
            response_fc = response_data[0]
            
            # Check for Modbus exception
            if response_fc & 0x80:
                if len(response_data) < 2:
                    print("[Modbus Client] Invalid exception response")
                    return None
                exception_code = response_data[1]
                print(f"[Modbus Client] Exception: code {exception_code}")
                return None
            
            # Verify function code matches
            if response_fc != function_code:
                print(f"[Modbus Client] Function code mismatch: expected {function_code}, got {response_fc}")
                return None
            
            return response_data[1:]  # Return data without function code
            
        except Exception as e:
            print(f"[Modbus Client] Request error: {e}")
            return None
    
    def read_holding_registers(self, address, count):
        """
        Read holding registers (Function Code 3)
        
        Args:
            address: Starting register address (0-65535)
            count: Number of registers to read (1-125)
            
        Returns:
            List of register values or None on error
        """
        # Validate parameters
        if not (0 <= address <= 65535):
            print(f"[Modbus Client] Invalid address: {address}")
            return None
        if not (1 <= count <= 125):
            print(f"[Modbus Client] Invalid count: {count} (must be 1-125)")
            return None
        if address + count > 65536:
            print(f"[Modbus Client] Address range overflow")
            return None
        
        # Build request data
        data = struct.pack('>HH', address, count)
        
        # Send request
        response = self._send_request(0x03, data)
        if response is None:
            return None
        
        # Parse response
        byte_count = response[0]
        if byte_count != count * 2:
            print(f"[Modbus Client] Invalid byte count: expected {count * 2}, got {byte_count}")
            return None
        
        # Extract register values
        values = []
        for i in range(count):
            offset = 1 + (i * 2)
            value = struct.unpack('>H', response[offset:offset+2])[0]
            values.append(value)
        
        return values
    
    def read_input_registers(self, address, count):
        """
        Read input registers (Function Code 4)
        
        Args:
            address: Starting register address (0-65535)
            count: Number of registers to read (1-125)
            
        Returns:
            List of register values or None on error
        """
        # Validate parameters
        if not (0 <= address <= 65535):
            print(f"[Modbus Client] Invalid address: {address}")
            return None
        if not (1 <= count <= 125):
            print(f"[Modbus Client] Invalid count: {count} (must be 1-125)")
            return None
        if address + count > 65536:
            print(f"[Modbus Client] Address range overflow")
            return None
        
        # Build request data
        data = struct.pack('>HH', address, count)
        
        # Send request
        response = self._send_request(0x04, data)
        if response is None:
            return None
        
        # Parse response
        byte_count = response[0]
        if byte_count != count * 2:
            print(f"[Modbus Client] Invalid byte count: expected {count * 2}, got {byte_count}")
            return None
        
        # Extract register values
        values = []
        for i in range(count):
            offset = 1 + (i * 2)
            value = struct.unpack('>H', response[offset:offset+2])[0]
            values.append(value)
        
        return values
    
    def write_register(self, address, value):
        """
        Write single register (Function Code 6)
        
        Args:
            address: Register address (0-65535)
            value: Value to write (0-65535)
            
        Returns:
            True on success, False on error
        """
        # Validate parameters
        if not (0 <= address <= 65535):
            print(f"[Modbus Client] Invalid address: {address}")
            return False
        if not (0 <= value <= 65535):
            print(f"[Modbus Client] Invalid value: {value}")
            return False
        
        # Build request data
        data = struct.pack('>HH', address, value)
        
        # Send request
        response = self._send_request(0x06, data)
        if response is None:
            return False
        
        # Parse response (should echo request)
        resp_address = struct.unpack('>H', response[0:2])[0]
        resp_value = struct.unpack('>H', response[2:4])[0]
        
        if resp_address != address or resp_value != value:
            print(f"[Modbus Client] Write verification failed")
            return False
        
        return True
    
    def write_registers(self, address, values):
        """
        Write multiple registers (Function Code 16)
        
        Args:
            address: Starting register address (0-65535)
            values: List of values to write (1-123 values, each 0-65535)
            
        Returns:
            True on success, False on error
        """
        # Validate parameters
        if not (0 <= address <= 65535):
            print(f"[Modbus Client] Invalid address: {address}")
            return False
        if not values or len(values) == 0:
            print(f"[Modbus Client] No values provided")
            return False
        if len(values) > 123:
            print(f"[Modbus Client] Too many values: {len(values)} (max 123)")
            return False
        if address + len(values) > 65536:
            print(f"[Modbus Client] Address range overflow")
            return False
        for val in values:
            if not (0 <= val <= 65535):
                print(f"[Modbus Client] Invalid value: {val}")
                return False
        
        count = len(values)
        byte_count = count * 2
        
        # Build request data
        data = struct.pack('>HHB', address, count, byte_count)
        for value in values:
            data += struct.pack('>H', value)
        
        # Send request
        response = self._send_request(0x10, data)
        if response is None:
            return False
        
        # Parse response
        resp_address = struct.unpack('>H', response[0:2])[0]
        resp_count = struct.unpack('>H', response[2:4])[0]
        
        if resp_address != address or resp_count != count:
            print(f"[Modbus Client] Write verification failed")
            return False
        
        return True
