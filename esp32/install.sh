#!/bin/bash
# ESP32 Flash and Upload Script
# Automates the process of flashing MicroPython and uploading files to ESP32

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "ModbustoWELD ESP32 Installation Script"
echo "=========================================="

# Check if we're in the esp32 directory
if [ ! -f "main.py" ]; then
    echo -e "${RED}Error: Please run this script from the esp32 directory${NC}"
    exit 1
fi

# Detect serial port
echo -e "\n${YELLOW}Detecting ESP32 serial port...${NC}"
if [ -e "/dev/ttyUSB0" ]; then
    PORT="/dev/ttyUSB0"
elif [ -e "/dev/ttyUSB1" ]; then
    PORT="/dev/ttyUSB1"
elif [ -e "/dev/cu.usbserial-0001" ]; then
    PORT="/dev/cu.usbserial-0001"
else
    echo -e "${RED}Could not detect ESP32 serial port${NC}"
    echo "Please specify the port manually:"
    read -p "Port (e.g., /dev/ttyUSB0): " PORT
fi

echo -e "${GREEN}Using port: $PORT${NC}"

# Check if config.py has been edited
if grep -q "your_wifi_ssid" config.py; then
    echo -e "\n${RED}Warning: config.py still contains default values!${NC}"
    echo "Please edit config.py with your WiFi credentials and WLED settings"
    read -p "Press Enter to continue or Ctrl+C to abort..."
fi

# Check for required tools
echo -e "\n${YELLOW}Checking for required tools...${NC}"

if ! command -v esptool.py &> /dev/null; then
    echo -e "${RED}esptool not found. Installing...${NC}"
    pip install esptool
fi

if ! command -v mpremote &> /dev/null; then
    echo -e "${RED}mpremote not found. Installing...${NC}"
    pip install mpremote
fi

# Menu
echo -e "\n${YELLOW}What would you like to do?${NC}"
echo "1) Flash MicroPython firmware (first time setup)"
echo "2) Upload files only (MicroPython already installed)"
echo "3) Full setup (flash + upload)"
echo "4) Exit"
read -p "Choice (1-4): " choice

case $choice in
    1|3)
        # Download and flash MicroPython
        echo -e "\n${YELLOW}Downloading MicroPython firmware...${NC}"
        
        FIRMWARE="esp32-20230426-v1.20.0.bin"
        if [ ! -f "$FIRMWARE" ]; then
            wget "https://micropython.org/resources/firmware/$FIRMWARE"
        fi
        
        echo -e "\n${YELLOW}Erasing flash...${NC}"
        esptool.py --chip esp32 --port $PORT erase_flash
        
        echo -e "\n${YELLOW}Flashing MicroPython...${NC}"
        esptool.py --chip esp32 --port $PORT --baud 460800 write_flash -z 0x1000 $FIRMWARE
        
        echo -e "${GREEN}MicroPython flashed successfully!${NC}"
        echo "Waiting 3 seconds for ESP32 to boot..."
        sleep 3
        
        if [ "$choice" = "1" ]; then
            exit 0
        fi
        ;;
    4)
        exit 0
        ;;
esac

if [ "$choice" = "2" ] || [ "$choice" = "3" ]; then
    # Upload files
    echo -e "\n${YELLOW}Uploading files to ESP32...${NC}"
    
    FILES=("config.py" "wled_client.py" "modbus_slave.py" "main.py")
    
    for file in "${FILES[@]}"; do
        echo "Uploading $file..."
        mpremote connect $PORT cp $file :
    done
    
    echo -e "\n${GREEN}All files uploaded successfully!${NC}"
    
    # Ask about boot.py
    echo -e "\n${YELLOW}Would you like to create boot.py for auto-start?${NC}"
    read -p "(y/n): " autostart
    
    if [ "$autostart" = "y" ] || [ "$autostart" = "Y" ]; then
        echo "import main" > /tmp/boot.py
        echo "Uploading boot.py..."
        mpremote connect $PORT cp /tmp/boot.py :
        rm /tmp/boot.py
        echo -e "${GREEN}Auto-start configured!${NC}"
    fi
    
    echo -e "\n${YELLOW}Would you like to monitor the serial output?${NC}"
    read -p "(y/n): " monitor
    
    if [ "$monitor" = "y" ] || [ "$monitor" = "Y" ]; then
        echo -e "\n${GREEN}Starting serial monitor... (Press Ctrl+] to exit)${NC}"
        echo "Resetting ESP32..."
        mpremote connect $PORT reset
        sleep 2
        mpremote connect $PORT
    fi
fi

echo -e "\n${GREEN}=========================================="
echo "Installation complete!"
echo "==========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Connect to serial console: mpremote connect $PORT"
echo "2. Run: import main"
echo "3. Note the IP address shown"
echo "4. Connect Modbus clients to <IP>:5020"
echo ""
