#!/bin/bash

# WiFi Access Point Setup Script for Raspberry Pi
# This script configures the Raspberry Pi as a WiFi access point for the camper control system

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
WIFI_CONFIG_DIR="$PROJECT_ROOT/config/wifi"

echo -e "${GREEN}=== Camper Control System - WiFi Access Point Setup ===${NC}"
echo "Project root: $PROJECT_ROOT"
echo "WiFi config directory: $WIFI_CONFIG_DIR"
echo

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}Error: This script must be run as root${NC}"
   echo "Usage: sudo $0"
   exit 1
fi

# Check if we're on a Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo -e "${YELLOW}Warning: This doesn't appear to be a Raspberry Pi${NC}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Function to backup existing files
backup_file() {
    local file=$1
    if [[ -f "$file" ]]; then
        echo "Backing up $file to $file.backup"
        cp "$file" "$file.backup"
    fi
}

# Function to install packages
install_packages() {
    echo -e "${GREEN}Installing required packages...${NC}"
    apt-get update
    apt-get install -y hostapd dnsmasq iptables-persistent
    
    # Stop services during configuration
    systemctl stop hostapd
    systemctl stop dnsmasq
}

# Function to configure static IP
configure_static_ip() {
    echo -e "${GREEN}Configuring static IP for wlan0...${NC}"
    
    # Configure dhcpcd to ignore wlan0
    backup_file /etc/dhcpcd.conf
    
    if ! grep -q "denyinterfaces wlan0" /etc/dhcpcd.conf; then
        echo "denyinterfaces wlan0" >> /etc/dhcpcd.conf
    fi
    
    # Configure static IP in interfaces file
    backup_file /etc/network/interfaces
    
    cat >> /etc/network/interfaces << EOF

# Static IP configuration for wlan0 (Access Point)
auto wlan0
iface wlan0 inet static
    address 192.168.4.1
    netmask 255.255.255.0
    network 192.168.4.0
    broadcast 192.168.4.255
EOF
}

# Function to configure hostapd
configure_hostapd() {
    echo -e "${GREEN}Configuring hostapd...${NC}"
    
    # Copy hostapd configuration
    if [[ -f "$WIFI_CONFIG_DIR/hostapd.conf" ]]; then
        backup_file /etc/hostapd/hostapd.conf
        cp "$WIFI_CONFIG_DIR/hostapd.conf" /etc/hostapd/hostapd.conf
        echo "Copied hostapd configuration"
    else
        echo -e "${RED}Error: hostapd.conf not found in $WIFI_CONFIG_DIR${NC}"
        exit 1
    fi
    
    # Configure hostapd daemon
    backup_file /etc/default/hostapd
    sed -i 's/#DAEMON_CONF=""/DAEMON_CONF="\/etc\/hostapd\/hostapd.conf"/' /etc/default/hostapd
}

# Function to configure dnsmasq
configure_dnsmasq() {
    echo -e "${GREEN}Configuring dnsmasq...${NC}"
    
    # Backup original dnsmasq configuration
    backup_file /etc/dnsmasq.conf
    
    # Copy our dnsmasq configuration
    if [[ -f "$WIFI_CONFIG_DIR/dnsmasq.conf" ]]; then
        cp "$WIFI_CONFIG_DIR/dnsmasq.conf" /etc/dnsmasq.conf
        echo "Copied dnsmasq configuration"
    else
        echo -e "${RED}Error: dnsmasq.conf not found in $WIFI_CONFIG_DIR${NC}"
        exit 1
    fi
    
    # Create DHCP lease directory
    mkdir -p /var/lib/dhcp
    touch /var/lib/dhcp/dnsmasq.leases
    chown dnsmasq:dnsmasq /var/lib/dhcp/dnsmasq.leases
}

# Function to configure IP forwarding and NAT
configure_routing() {
    echo -e "${GREEN}Configuring IP forwarding and NAT...${NC}"
    
    # Enable IP forwarding
    backup_file /etc/sysctl.conf
    if ! grep -q "net.ipv4.ip_forward=1" /etc/sysctl.conf; then
        echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
    fi
    
    # Configure iptables for NAT (if eth0 is available for internet sharing)
    if ip link show eth0 >/dev/null 2>&1; then
        echo "Configuring NAT for internet sharing via eth0..."
        
        # Clear existing rules
        iptables -t nat -F
        iptables -F
        iptables -X
        
        # Set up NAT
        iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
        iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
        iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT
        
        # Save iptables rules
        iptables-save > /etc/iptables/rules.v4
    else
        echo -e "${YELLOW}Warning: eth0 not found, skipping NAT configuration${NC}"
        echo "Devices will be able to communicate with the Pi but not access the internet"
    fi
}

# Function to enable services
enable_services() {
    echo -e "${GREEN}Enabling and starting services...${NC}"
    
    # Unmask and enable hostapd
    systemctl unmask hostapd
    systemctl enable hostapd
    
    # Enable dnsmasq
    systemctl enable dnsmasq
    
    # Start services
    systemctl start hostapd
    systemctl start dnsmasq
    
    # Check service status
    echo
    echo "Service status:"
    systemctl is-active hostapd && echo -e "hostapd: ${GREEN}active${NC}" || echo -e "hostapd: ${RED}inactive${NC}"
    systemctl is-active dnsmasq && echo -e "dnsmasq: ${GREEN}active${NC}" || echo -e "dnsmasq: ${RED}inactive${NC}"
}

# Function to create startup script
create_startup_script() {
    echo -e "${GREEN}Creating WiFi AP startup script...${NC}"
    
    cat > /usr/local/bin/start-wifi-ap << 'EOF'
#!/bin/bash
# WiFi Access Point startup script

# Bring up wlan0 interface
ip link set wlan0 up
ip addr add 192.168.4.1/24 dev wlan0

# Start services
systemctl start hostapd
systemctl start dnsmasq

echo "WiFi Access Point started"
echo "SSID: CamperControl"
echo "IP: 192.168.4.1"
EOF

    chmod +x /usr/local/bin/start-wifi-ap
}

# Function to display final information
show_final_info() {
    echo
    echo -e "${GREEN}=== WiFi Access Point Setup Complete ===${NC}"
    echo
    echo "Network Information:"
    echo "  SSID: CamperControl"
    echo "  Password: camper123"
    echo "  Pi IP Address: 192.168.4.1"
    echo "  DHCP Range: 192.168.4.100 - 192.168.4.200"
    echo
    echo "Main Controller API will be available at:"
    echo "  http://192.168.4.1:5000"
    echo
    echo "To restart the access point:"
    echo "  sudo /usr/local/bin/start-wifi-ap"
    echo
    echo "To check service status:"
    echo "  sudo systemctl status hostapd"
    echo "  sudo systemctl status dnsmasq"
    echo
    echo -e "${YELLOW}Please reboot the Raspberry Pi to ensure all changes take effect:${NC}"
    echo "  sudo reboot"
}

# Main execution
main() {
    echo "Starting WiFi Access Point setup..."
    echo
    
    install_packages
    configure_static_ip
    configure_hostapd
    configure_dnsmasq
    configure_routing
    enable_services
    create_startup_script
    show_final_info
    
    echo
    echo -e "${GREEN}Setup completed successfully!${NC}"
}

# Run main function
main "$@"