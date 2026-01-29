#!/usr/bin/env python3
"""
Mock WLED Server for Testing
Simulates a WLED device for testing the ModbustoWELD bridge
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys

class MockWLEDState:
    """Simulated WLED device state"""
    def __init__(self):
        self.on = False
        self.brightness = 128
        self.red = 255
        self.green = 255
        self.blue = 255
        self.effect = 0
    
    def to_dict(self):
        return {
            "on": self.on,
            "bri": self.brightness,
            "seg": [{
                "id": 0,
                "start": 0,
                "stop": 30,
                "col": [[self.red, self.green, self.blue]],
                "fx": self.effect
            }]
        }
    
    def get_info(self):
        return {
            "ver": "0.14.0-mock",
            "name": "Mock WLED Device",
            "leds": {
                "count": 30
            },
            "str": True,
            "arch": "esp32"
        }

# Global state
wled_state = MockWLEDState()

class MockWLEDHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Override to customize logging"""
        sys.stdout.write(f"[Mock WLED] {format % args}\n")
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == "/json/state":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps(wled_state.to_dict())
            self.wfile.write(response.encode())
            print(f"  → State: {'ON' if wled_state.on else 'OFF'}, Bri: {wled_state.brightness}, RGB({wled_state.red}, {wled_state.green}, {wled_state.blue})")
        
        elif self.path == "/json/info":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps(wled_state.get_info())
            self.wfile.write(response.encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == "/json/state":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode())
                
                # Update state
                if "on" in data:
                    wled_state.on = data["on"]
                    print(f"  → Power: {'ON' if wled_state.on else 'OFF'}")
                
                if "bri" in data:
                    wled_state.brightness = data["bri"]
                    print(f"  → Brightness: {wled_state.brightness}")
                
                if "seg" in data and len(data["seg"]) > 0:
                    seg = data["seg"][0]
                    
                    if "col" in seg and len(seg["col"]) > 0:
                        color = seg["col"][0]
                        if len(color) >= 3:
                            wled_state.red = color[0]
                            wled_state.green = color[1]
                            wled_state.blue = color[2]
                            print(f"  → Color: RGB({wled_state.red}, {wled_state.green}, {wled_state.blue})")
                    
                    if "fx" in seg:
                        wled_state.effect = seg["fx"]
                        print(f"  → Effect: {wled_state.effect}")
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = json.dumps({"success": True})
                self.wfile.write(response.encode())
            
            except Exception as e:
                print(f"Error processing POST: {e}")
                self.send_response(400)
                self.end_headers()
        
        else:
            self.send_response(404)
            self.end_headers()

def run_mock_server(host='0.0.0.0', port=8080):
    """Run the mock WLED server"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, MockWLEDHandler)
    print(f"Mock WLED server running on http://{host}:{port}")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down mock WLED server")
        httpd.shutdown()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Mock WLED Server for Testing')
    parser.add_argument('--host', default='0.0.0.0', help='Host to listen on (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8080, help='Port to listen on (default: 8080)')
    
    args = parser.parse_args()
    
    run_mock_server(args.host, args.port)
