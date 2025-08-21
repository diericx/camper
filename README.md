# Camper Device Control System

A distributed IoT control system for managing ESP8266 devices from a Raspberry Pi main controller. The system uses Flask APIs for communication and supports device registration, heartbeat monitoring, and command execution.

## System Overview

- **Main Controller**: Raspberry Pi running Flask API that manages device registry
- **Device Controllers**: ESP8266 devices running specific Flask APIs (e.g., rear camera)
- **Communication**: WiFi access point hosted on Raspberry Pi for isolated network
- **Storage**: In-memory device registry with automatic cleanup
- **Architecture**: RESTful APIs with JSON communication

## Features

- ✅ **Device Registration**: Automatic device registration with type restrictions
- ✅ **Heartbeat Monitoring**: Continuous device health monitoring
- ✅ **Device Control**: Send commands to registered devices
- ✅ **WiFi Access Point**: Isolated network for device communication
- ✅ **Auto Cleanup**: Remove inactive devices automatically
- ✅ **Extensible Design**: Easy to add new device types
- ✅ **Comprehensive Logging**: Structured logging with rotation
- ✅ **Error Handling**: Robust error handling and recovery

## Quick Start

### 1. Deploy Main Controller (Raspberry Pi)

```bash
# Clone the repository
git clone <repository-url>
cd camper-control-system

# Deploy main controller
sudo scripts/deployment/deploy_main.sh

# Set up WiFi access point
sudo scripts/setup/setup_wifi_ap.sh

# Reboot to apply network changes
sudo reboot
```

### 2. Start Device Controller (ESP8266)

```bash
# On the device (or development machine)
python device_controllers/start_device.py --device-type rear-camera
```

### 3. Test the System

```bash
# Check system status
sudo camper-status

# Test API endpoints
curl http://192.168.4.1:5000/health
curl http://192.168.4.1:5000/api/v1/main-controller/devices
```

## API Documentation

### Main Controller API (Port 5000)

#### Device Registration

```http
PUT /api/v1/main-controller/device/{device_id}
Content-Type: application/json

{
    "device_type": "rear-camera",
    "ip_address": "192.168.4.100",
    "port": 5001
}
```

#### Get Devices

```http
GET /api/v1/main-controller/devices
GET /api/v1/main-controller/devices?active_only=true
GET /api/v1/main-controller/devices?device_type=rear-camera
```

#### Device Control

```http
POST /api/v1/main-controller/control/{device_id}/{command}
```

### Rear Camera API (Port 5001)

#### Camera Movement

```http
POST /api/v1/rear-camera/up      # Move camera up
POST /api/v1/rear-camera/down    # Move camera down
POST /api/v1/rear-camera/reset   # Reset to middle position
GET  /api/v1/rear-camera/status  # Get camera status
```

## Configuration

### Main Controller Configuration

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 5000
  },
  "cleanup": {
    "inactive_threshold_minutes": 2,
    "removal_threshold_minutes": 5,
    "cleanup_interval_seconds": 60
  },
  "device_types": {
    "rear-camera": {
      "max_count": 1,
      "description": "Rear camera controller - single instance only"
    }
  }
}
```

### Device Configuration

```json
{
  "device_id": "rear-camera-001",
  "device_type": "rear-camera",
  "api_port": 5001,
  "main_controller": {
    "ip": "192.168.4.1",
    "port": 5000
  },
  "heartbeat": {
    "interval_seconds": 30,
    "retry_attempts": 3
  }
}
```

## Network Configuration

- **WiFi SSID**: CamperControl
- **WiFi Password**: camper123
- **Pi IP Address**: 192.168.4.1
- **DHCP Range**: 192.168.4.100 - 192.168.4.200
- **Main Controller API**: http://192.168.4.1:5000

## Management Commands

```bash
# System management
sudo camper-start    # Start the entire system
sudo camper-stop     # Stop the entire system
sudo camper-status   # Check system status

# Service management
sudo systemctl start camper-main-controller
sudo systemctl stop camper-main-controller
sudo systemctl status camper-main-controller

# View logs
sudo journalctl -u camper-main-controller -f
tail -f /home/pi/camper-control-system/logs/main_controller.log
```

## Project Structure

```
camper-control-system/
├── main_controller/           # Main controller Flask API
│   ├── app.py                # Main Flask application
│   ├── device_registry.py    # In-memory device registry
│   ├── cleanup_service.py    # Background cleanup service
│   └── api/                  # API route handlers
├── device_controllers/        # Device controller implementations
│   ├── base_controller.py    # Base device controller class
│   ├── heartbeat_service.py  # Heartbeat service
│   ├── start_device.py       # Device startup script
│   └── rear_camera/          # Rear camera implementation
├── shared/                   # Shared utilities and constants
├── config/                   # Configuration files
│   ├── main_config.json      # Main controller config
│   ├── device_configs/       # Device-specific configs
│   └── wifi/                 # WiFi access point config
├── scripts/                  # Deployment and setup scripts
└── logs/                     # Application logs
```

## Device Types

### Rear Camera Controller

- **Type**: `rear-camera`
- **Limit**: 1 device maximum
- **Commands**: up, down, reset, status
- **Hardware**: Servo motor control (simulated)

### Adding New Device Types

1. Create device controller in `device_controllers/new_device/`
2. Implement device-specific API endpoints
3. Add device type to constants and configuration
4. Update control route mappings

## Development

### Running in Development Mode

```bash
# Start main controller
python main_controller/app.py

# Start device controller
python device_controllers/start_device.py --device-type rear-camera
```

### Testing

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests (when implemented)
python -m pytest tests/

# Validate configuration
python device_controllers/start_device.py --validate-config
```

## Troubleshooting

### Common Issues

1. **Device Registration Fails**

   - Check WiFi connectivity
   - Verify main controller is running
   - Check device configuration

2. **WiFi Access Point Not Working**

   - Run WiFi setup script again
   - Check hostapd and dnsmasq services
   - Verify network interface configuration

3. **Service Won't Start**
   - Check logs: `journalctl -u camper-main-controller`
   - Verify Python dependencies
   - Check file permissions

### Log Locations

- **Application Logs**: `/home/pi/camper-control-system/logs/`
- **System Logs**: `journalctl -u camper-main-controller`
- **WiFi Logs**: `/var/log/dnsmasq.log`

## Architecture Benefits

- **Simplicity**: In-memory storage eliminates database complexity
- **Reliability**: Self-healing system with automatic device re-registration
- **Performance**: Fast device lookups and minimal resource usage
- **Extensibility**: Easy to add new device types and commands
- **Isolation**: Dedicated WiFi network for security

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review the logs
3. Create an issue in the repository
