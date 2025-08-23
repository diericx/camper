#!/bin/bash

# Camper Main Controller Service Installation Script
# This script installs the Flask API as a systemd service

set -e

SERVICE_NAME="camper-main-controller"
SERVICE_FILE="${SERVICE_NAME}.service"
SYSTEMD_DIR="/etc/systemd/system"
CURRENT_DIR="$(pwd)"
PROJECT_DIR="$(dirname "$CURRENT_DIR")"

echo "Installing Camper Main Controller Service..."
echo "Current directory: $CURRENT_DIR"
echo "Project directory: $PROJECT_DIR"

source setup-pyenv.sh

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "This script must be run as root (use sudo)"
    echo "Usage: sudo ./install-service.sh"
    exit 1
fi

# Check if service file exists
if [ ! -f "$SERVICE_FILE" ]; then
    echo "Error: $SERVICE_FILE not found in current directory"
    exit 1
fi

# Update the service file with the correct paths
echo "Updating service file with current paths..."
sed -i "s|/home/pi/camper/main-controller|$CURRENT_DIR|g" "$SERVICE_FILE"

# Copy service file to systemd directory
echo "Copying service file to $SYSTEMD_DIR..."
cp "$SERVICE_FILE" "$SYSTEMD_DIR/"

# Set proper permissions
chmod 644 "$SYSTEMD_DIR/$SERVICE_FILE"

# Reload systemd daemon
echo "Reloading systemd daemon..."
systemctl daemon-reload

# Enable the service to start on boot
echo "Enabling service to start on boot..."
systemctl enable "$SERVICE_NAME"

# Start the service
echo "Starting the service..."
systemctl start "$SERVICE_NAME"

# Check service status
echo ""
echo "Service installation complete!"
echo ""
echo "Service status:"
systemctl status "$SERVICE_NAME" --no-pager -l

echo ""
echo "Useful commands:"
echo "  Check status:    sudo systemctl status $SERVICE_NAME"
echo "  Start service:   sudo systemctl start $SERVICE_NAME"
echo "  Stop service:    sudo systemctl stop $SERVICE_NAME"
echo "  Restart service: sudo systemctl restart $SERVICE_NAME"
echo "  View logs:       sudo journalctl -u $SERVICE_NAME -f"
echo "  Disable service: sudo systemctl disable $SERVICE_NAME"
echo ""
echo "The API should now be running on port 80 (production mode)"
echo "Health check: http://localhost/health"