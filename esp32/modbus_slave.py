"""
Simple Modbus TCP Slave for ESP32 MicroPython
Implements basic Modbus TCP functionality for WLED control
"""

import socket
import struct

class ModbusTCPSlave:
    """
    Lightweight Modbus TCP slave implementation for ESP32
    
    Supports:
    - Function Code 3: Read Holding Registers
    - Function Code 4: Read Input Registers  
    - Function Code 6: Write Single Register
    - Function Code 16: Write Multiple Registers
    """
    
    def __init__(self, host='0.0.0.0', port=5020, slave_id=1):
        """
        Initialize Modbus TCP slave
        
        Args:
            host: Host to bind to (default: 0.0.0.0)
            port: Port to listen on (default: 5020)
            slave_id: Modbus slave ID (default: 1)
        """
        self.host = host
        self.port = port
        self.slave_id = slave_id
        self.socket = None
        self.running = False
        
        # Initialize register storage
        # Holding registers (read/write) - commands
        self.holding_registers = [0] * 100
        
        # Input registers (read-only) - status
        self.input_registers = [0] * 100
        
        print(f"[Modbus] Initialized slave ID {slave_id} on {host}:{port}")
    
    def start(self):
        """Start the Modbus TCP server"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        self.socket.settimeout(1.0)  # 1 second timeout for accept()
        self.running = True
        print(f"[Modbus] Server started on {self.host}:{self.port}")
    
    def stop(self):
        """Stop the Modbus TCP server"""
        self.running = False
        if self.socket:
            self.socket.close()
        print("[Modbus] Server stopped")
    
    def set_holding_registers(self, address, values):
        """Set holding register values"""
        for i, value in enumerate(values):
            if address + i < len(self.holding_registers):
                self.holding_registers[address + i] = value
    
    def get_holding_registers(self, address, count):
        """Get holding register values"""
        return self.holding_registers[address:address + count]
    
    def set_input_registers(self, address, values):
        """Set input register values"""
        for i, value in enumerate(values):
            if address + i < len(self.input_registers):
                self.input_registers[address + i] = value
    
    def get_input_registers(self, address, count):
        """Get input register values"""
        return self.input_registers[address:address + count]
    
    def _parse_mbap_header(self, data):
        """Parse Modbus Application Protocol header"""
        if len(data) < 7:
            return None
        
        transaction_id = struct.unpack('>H', data[0:2])[0]
        protocol_id = struct.unpack('>H', data[2:4])[0]
        length = struct.unpack('>H', data[4:6])[0]
        unit_id = data[6]
        
        return {
            'transaction_id': transaction_id,
            'protocol_id': protocol_id,
            'length': length,
            'unit_id': unit_id
        }
    
    def _build_mbap_header(self, transaction_id, length):
        """Build Modbus Application Protocol header"""
        return struct.pack('>HHHB',
            transaction_id,  # Transaction ID
            0,               # Protocol ID (0 for Modbus)
            length,          # Length
            self.slave_id    # Unit ID
        )
    
    def _handle_read_holding_registers(self, request, transaction_id):
        """Handle Function Code 3: Read Holding Registers"""
        address = struct.unpack('>H', request[0:2])[0]
        count = struct.unpack('>H', request[2:4])[0]
        
        # Read registers
        values = self.get_holding_registers(address, count)
        
        # Build response
        byte_count = count * 2
        response_pdu = struct.pack('BB', 0x03, byte_count)
        for value in values:
            response_pdu += struct.pack('>H', value)
        
        # Add MBAP header
        mbap = self._build_mbap_header(transaction_id, len(response_pdu) + 1)
        return mbap + response_pdu
    
    def _handle_read_input_registers(self, request, transaction_id):
        """Handle Function Code 4: Read Input Registers"""
        address = struct.unpack('>H', request[0:2])[0]
        count = struct.unpack('>H', request[2:4])[0]
        
        # Read registers
        values = self.get_input_registers(address, count)
        
        # Build response
        byte_count = count * 2
        response_pdu = struct.pack('BB', 0x04, byte_count)
        for value in values:
            response_pdu += struct.pack('>H', value)
        
        # Add MBAP header
        mbap = self._build_mbap_header(transaction_id, len(response_pdu) + 1)
        return mbap + response_pdu
    
    def _handle_write_single_register(self, request, transaction_id):
        """Handle Function Code 6: Write Single Register"""
        address = struct.unpack('>H', request[0:2])[0]
        value = struct.unpack('>H', request[2:4])[0]
        
        # Write register
        self.set_holding_registers(address, [value])
        
        # Echo request as response
        response_pdu = struct.pack('BHH', 0x06, address, value)
        mbap = self._build_mbap_header(transaction_id, len(response_pdu) + 1)
        return mbap + response_pdu
    
    def _handle_write_multiple_registers(self, request, transaction_id):
        """Handle Function Code 16: Write Multiple Registers"""
        address = struct.unpack('>H', request[0:2])[0]
        count = struct.unpack('>H', request[2:4])[0]
        byte_count = request[4]
        
        # Extract values
        values = []
        for i in range(count):
            offset = 5 + (i * 2)
            value = struct.unpack('>H', request[offset:offset+2])[0]
            values.append(value)
        
        # Write registers
        self.set_holding_registers(address, values)
        
        # Build response
        response_pdu = struct.pack('BHH', 0x10, address, count)
        mbap = self._build_mbap_header(transaction_id, len(response_pdu) + 1)
        return mbap + response_pdu
    
    def _handle_request(self, data):
        """Handle Modbus TCP request"""
        try:
            # Parse MBAP header
            header = self._parse_mbap_header(data)
            if not header:
                return None
            
            # Check unit ID
            if header['unit_id'] != self.slave_id:
                return None
            
            # Get function code
            function_code = data[7]
            request_pdu = data[8:]
            
            # Handle function codes
            if function_code == 0x03:  # Read Holding Registers
                return self._handle_read_holding_registers(request_pdu, header['transaction_id'])
            elif function_code == 0x04:  # Read Input Registers
                return self._handle_read_input_registers(request_pdu, header['transaction_id'])
            elif function_code == 0x06:  # Write Single Register
                return self._handle_write_single_register(request_pdu, header['transaction_id'])
            elif function_code == 0x10:  # Write Multiple Registers
                return self._handle_write_multiple_registers(request_pdu, header['transaction_id'])
            else:
                print(f"[Modbus] Unsupported function code: {function_code}")
                return None
                
        except Exception as e:
            print(f"[Modbus] Error handling request: {e}")
            return None
    
    def handle_connection(self, client_socket):
        """Handle a client connection"""
        try:
            client_socket.settimeout(5.0)
            data = client_socket.recv(256)
            
            if data:
                response = self._handle_request(data)
                if response:
                    client_socket.send(response)
        except OSError as e:
            if e.args[0] != 110:  # ETIMEDOUT
                print(f"[Modbus] Connection error: {e}")
        except Exception as e:
            print(f"[Modbus] Error: {e}")
        finally:
            client_socket.close()
    
    def process_requests(self):
        """Process incoming Modbus requests (non-blocking)"""
        if not self.running:
            return
        
        try:
            client_socket, client_addr = self.socket.accept()
            self.handle_connection(client_socket)
        except OSError as e:
            # Timeout or no connection - this is normal
            pass
        except Exception as e:
            print(f"[Modbus] Accept error: {e}")
