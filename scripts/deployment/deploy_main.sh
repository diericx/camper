#!/bin/bash

# Main Controller Deployment Script
# Deploys and configures the main controller on Raspberry Pi

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SERVICE_USER="pi"
SERVICE_GROUP="pi"
INSTALL_DIR="/home/pi/camper-control-system"
SERVICE_NAME="camper-main-controller"

echo -e "${GREEN}=== Camper Control System - Main Controller Deployment ===${NC}"
echo "Project root: $PROJECT_ROOT"
echo "Install directory: $INSTALL_DIR"
echo

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Error: This script must be run as root${NC}"
   echo "Usage: sudo $0"
   exit 1
fi

# Function to install system dependencies
install_system_dependencies() {
    echo -e "${GREEN}Installing system dependencies...${NC}"
    
    apt-get update
    apt-get install -y \
        python3 \
        python3-pip \
        python3-venv \
        git \
        curl \
        systemd
    
    echo "System dependencies installed"
}

# Function to create installation directory
create_install_directory() {
    echo -e "${GREEN}Creating installation directory...${NC}"
    
    # Create install directory
    mkdir -p "$INSTALL_DIR"
    
    # Copy project files
    echo "Copying project files..."
    cp -r "$PROJECT_ROOT"/* "$INSTALL_DIR/"
    
    # Set ownership
    chown -R "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_DIR"
    
    echo "Installation directory created: $INSTALL_DIR"
}

# Function to set up Python virtual environment
setup_python_environment() {
    echo -e "${GREEN}Setting up Python virtual environment...${NC}"
    
    cd "$INSTALL_DIR"
    
    # Create virtual environment as the service user
    sudo -u "$SERVICE_USER" python3 -m venv venv
    
    # Install Python dependencies
    sudo -u "$SERVICE_USER" ./venv/bin/pip install --upgrade pip
    sudo -u "$SERVICE_USER" ./venv/bin/pip install -r requirements.txt
    
    echo "Python environment set up successfully"
}

# Function to create directories
create_directories() {
    echo -e "${GREEN}Creating required directories...${NC}"
    
    # Create directories
    mkdir -p "$INSTALL_DIR/logs"
    mkdir -p "$INSTALL_DIR/data"
    mkdir -p "$INSTALL_DIR/data/backups"
    
    # Set permissions
    chown -R "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_DIR/logs"
    chown -R "$SERVICE_USER:$SERVICE_GROUP" "$INSTALL_DIR/data"
    
    echo "Directories created"
}

# Function to create systemd service
create_systemd_service() {
    echo -e "${GREEN}Creating systemd service...${NC}"
    
    cat > "/etc/systemd/system/${SERVICE_NAME}.service" << EOF
[Unit]
Description=Camper Main Controller API
After=network.target
Wants=network.target

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_GROUP
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python main_controller/app.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=$INSTALL_DIR
Environment=MAIN_CONTROLLER_CONFIG=$INSTALL_DIR/config/main_config.json

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=$INSTALL_DIR/logs $INSTALL_DIR/data

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd
    systemctl daemon-reload
    
    echo "Systemd service created: $SERVICE_NAME"
}

# Function to configure firewall
configure_firewall() {
    echo -e "${GREEN}Configuring firewall...${NC}"
    
    # Check if ufw is installed
    if command -v ufw >/dev/null 2>&1; then
        echo "Configuring UFW firewall..."
        
        # Allow SSH
        ufw allow ssh
        
        # Allow main controller API
        ufw allow 5000/tcp comment "Camper Main Controller API"
        
        # Allow WiFi access point traffic
        ufw allow in on wlan0
        ufw allow out on wlan0
        
        echo "Firewall configured"
    else
        echo -e "${YELLOW}UFW not installed, skipping firewall configuration${NC}"
    fi
}

# Function to create management scripts
create_management_scripts() {
    echo -e "${GREEN}Creating management scripts...${NC}"
    
    # Create start script
    cat > "/usr/local/bin/camper-start" << EOF
#!/bin/bash
# Start Camper Control System

echo "Starting Camper Control System..."

# Start WiFi access point
if [[ -f /usr/local/bin/start-wifi-ap ]]; then
    /usr/local/bin/start-wifi-ap
fi

# Start main controller
systemctl start $SERVICE_NAME

echo "Camper Control System started"
echo "Main Controller API: http://192.168.4.1:5000"
EOF

    # Create stop script
    cat > "/usr/local/bin/camper-stop" << EOF
#!/bin/bash
# Stop Camper Control System

echo "Stopping Camper Control System..."

# Stop main controller
systemctl stop $SERVICE_NAME

# Stop WiFi services
systemctl stop hostapd
systemctl stop dnsmasq

echo "Camper Control System stopped"
EOF

    # Create status script
    cat > "/usr/local/bin/camper-status" << EOF
#!/bin/bash
# Check Camper Control System status

echo "=== Camper Control System Status ==="
echo

echo "Main Controller Service:"
systemctl is-active $SERVICE_NAME && echo -e "  Status: \033[0;32mactive\033[0m" || echo -e "  Status: \033[0;31minactive\033[0m"

echo
echo "WiFi Access Point:"
systemctl is-active hostapd && echo -e "  hostapd: \033[0;32mactive\033[0m" || echo -e "  hostapd: \033[0;31minactive\033[0m"
systemctl is-active dnsmasq && echo -e "  dnsmasq: \033[0;32mactive\033[0m" || echo -e "  dnsmasq: \033[0;31minactive\033[0m"

echo
echo "Network Information:"
echo "  WiFi SSID: CamperControl"
echo "  Pi IP: 192.168.4.1"
echo "  API URL: http://192.168.4.1:5000"

echo
echo "Recent logs:"
journalctl -u $SERVICE_NAME --no-pager -n 5
EOF

    # Make scripts executable
    chmod +x /usr/local/bin/camper-start
    chmod +x /usr/local/bin/camper-stop
    chmod +x /usr/local/bin/camper-status
    
    echo "Management scripts created:"
    echo "  camper-start  - Start the system"
    echo "  camper-stop   - Stop the system"
    echo "  camper-status - Check system status"
}

# Function to enable and start services
enable_services() {
    echo -e "${GREEN}Enabling and starting services...${NC}"
    
    # Enable main controller service
    systemctl enable "$SERVICE_NAME"
    
    # Start the service
    systemctl start "$SERVICE_NAME"
    
    # Check service status
    sleep 2
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "Main controller service: ${GREEN}active${NC}"
    else
        echo -e "Main controller service: ${RED}failed to start${NC}"
        echo "Check logs with: journalctl -u $SERVICE_NAME"
    fi
}

# Function to run tests
run_tests() {
    echo -e "${GREEN}Running basic tests...${NC}"
    
    cd "$INSTALL_DIR"
    
    # Test Python imports
    echo "Testing Python imports..."
    sudo -u "$SERVICE_USER" ./venv/bin/python -c "
import sys
sys.path.append('.')
from shared.constants import *
from main_controller.device_registry import DeviceRegistry
print('✓ Python imports successful')
"
    
    # Test configuration loading
    echo "Testing configuration loading..."
    sudo -u "$SERVICE_USER" ./venv/bin/python -c "
import sys
sys.path.append('.')
from shared.utils import load_json_config
config = load_json_config('config/main_config.json')
print('✓ Configuration loading successful')
"
    
    echo "Basic tests completed"
}

# Function to display final information
show_final_info() {
    echo
    echo -e "${GREEN}=== Main Controller Deployment Complete ===${NC}"
    echo
    echo "Installation Details:"
    echo "  Install Directory: $INSTALL_DIR"
    echo "  Service Name: $SERVICE_NAME"
    echo "  Service User: $SERVICE_USER"
    echo
    echo "Management Commands:"
    echo "  Start System:  sudo camper-start"
    echo "  Stop System:   sudo camper-stop"
    echo "  Check Status:  sudo camper-status"
    echo
    echo "Service Commands:"
    echo "  Start:   sudo systemctl start $SERVICE_NAME"
    echo "  Stop:    sudo systemctl stop $SERVICE_NAME"
    echo "  Status:  sudo systemctl status $SERVICE_NAME"
    echo "  Logs:    sudo journalctl -u $SERVICE_NAME -f"
    echo
    echo "API Access:"
    echo "  Local:   http://localhost:5000"
    echo "  Network: http://192.168.4.1:5000"
    echo
    echo "Configuration Files:"
    echo "  Main Config: $INSTALL_DIR/config/main_config.json"
    echo "  WiFi Config: $INSTALL_DIR/config/wifi/"
    echo
    echo "Log Files:"
    echo "  Application: $INSTALL_DIR/logs/main_controller.log"
    echo "  System:      journalctl -u $SERVICE_NAME"
}

# Main execution
main() {
    echo "Starting main controller deployment..."
    echo
    
    install_system_dependencies
    create_install_directory
    setup_python_environment
    create_directories
    create_systemd_service
    configure_firewall
    create_management_scripts
    enable_services
    run_tests
    show_final_info
    
    echo
    echo -e "${GREEN}Deployment completed successfully!${NC}"
    echo
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Set up WiFi access point: sudo $INSTALL_DIR/scripts/setup/setup_wifi_ap.sh"
    echo "2. Reboot the system: sudo reboot"
    echo "3. Check system status: sudo camper-status"
}

# Run main function
main "$@"