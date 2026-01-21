#!/usr/bin/env python3
"""
ModbustoWELD - Modbus TCP to WLED Bridge
Main application entry point
"""

import sys
import yaml
import logging
import argparse
from pathlib import Path

from wled_client import WLEDClient
from modbus_server import ModbusWLEDServer


def setup_logging(level: str = "INFO"):
    """Configure logging"""
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('modbustoweld.log')
        ]
    )


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"Error loading config file: {e}")
        sys.exit(1)


def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description='ModbustoWELD - Modbus TCP to WLED Bridge',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Register Map:
  Holding Registers (read/write - commands):
    0: Power (0=OFF, 1=ON)
    1: Brightness (0-255)
    2: Red (0-255)
    3: Green (0-255)
    4: Blue (0-255)
    5: Effect ID
    
  Input Registers (read-only - status):
    0: Current Power State (0=OFF, 1=ON)
    1: Current Brightness (0-255)
    2: Current Red (0-255)
    3: Current Green (0-255)
    4: Current Blue (0-255)

Example:
  python main.py --config config.yaml
  python main.py --wled-host 192.168.1.100 --modbus-port 5020
        """
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--wled-host',
        type=str,
        help='WLED device hostname or IP (overrides config)'
    )
    
    parser.add_argument(
        '--wled-port',
        type=int,
        help='WLED HTTP port (overrides config)'
    )
    
    parser.add_argument(
        '--modbus-host',
        type=str,
        help='Modbus server host (overrides config)'
    )
    
    parser.add_argument(
        '--modbus-port',
        type=int,
        help='Modbus server port (overrides config)'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (overrides config)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override with command-line arguments
    if args.wled_host:
        config['wled']['host'] = args.wled_host
    if args.wled_port:
        config['wled']['port'] = args.wled_port
    if args.modbus_host:
        config['modbus']['host'] = args.modbus_host
    if args.modbus_port:
        config['modbus']['port'] = args.modbus_port
    if args.log_level:
        config['logging']['level'] = args.log_level
    
    # Setup logging
    log_level = config.get('logging', {}).get('level', 'INFO')
    setup_logging(log_level)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting ModbustoWELD")
    logger.info(f"Configuration: {config}")
    
    # Initialize WLED client
    wled_host = config['wled']['host']
    wled_port = config['wled'].get('port', 80)
    wled_client = WLEDClient(wled_host, wled_port)
    
    # Test WLED connection
    info = wled_client.get_info()
    if info:
        logger.info(f"Connected to WLED device: {info.get('name', 'Unknown')}")
        logger.info(f"WLED Version: {info.get('ver', 'Unknown')}")
    else:
        logger.warning("Could not connect to WLED device, will retry...")
    
    # Initialize and start Modbus server
    modbus_host = config['modbus'].get('host', '0.0.0.0')
    modbus_port = config['modbus'].get('port', 5020)
    server = ModbusWLEDServer(wled_client, modbus_host, modbus_port)
    
    try:
        logger.info("Starting Modbus TCP server...")
        logger.info(f"Listening on {modbus_host}:{modbus_port}")
        logger.info("Press Ctrl+C to stop")
        server.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        server.stop()
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
