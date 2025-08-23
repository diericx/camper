# Main Controller Flask API

A simple Flask API designed for Raspberry Pi device control as part of the camper project.

## Features

- **PUT /api/v1/device/{id}** - Update device information
- **GET /api/v1/devices** - List all registered devices
- **GET /health** - Health check endpoint
- Device cleanup (removes stale devices automatically)
- Basic error handling and validation
- Logging for debugging on Raspberry Pi
- Network accessible (0.0.0.0)
- Production/Development mode support
- Systemd service for auto-start on boot
- Minimal dependencies

## Quick Start

### Device Setup

Make sure the other network device exists (wlan1 via usb)

```
$ sudo nmcli device
wlan0          wifi      connected               preconfigured
lo             loopback  connected (externally)  lo
wlan1          wifi      disconnected            --
p2p-dev-wlan0  wifi-p2p  disconnected            --
p2p-dev-wlan1  wifi-p2p  disconnected            --
```

Switch main config to the dongle and setup networks

```
sudo nmcli connection modify preconfigured connection.interface-name wlan1
sudo nmcli connection up preconfigured
# Wifi cuts out here
sudo nmcli connection add type wifi con-name "<SSID>" ifname wlan1 ssid "<SSID>" wifi-sec.key-mgmt wpa-psk wifi-sec.psk "<PASSWORD>"
```

Set up the hotspot

```shell-session
sudo nmcli device wifi hotspot ssid CamperController password campercontroller ifname wlan0
```

Install git and python

```
sudo apt update
sudo apt install git python3
```

### Development Mode

1. **Clone and navigate to the project:**

   ```bash
   cd main-controller
   ```

2. **Run the startup script:**

   ```bash
   ./run.sh
   ```

   This script will:

   - Create a virtual environment if needed
   - Install dependencies
   - Start the Flask API on port 8080 (development) or port 80 (production)

### Production Mode (Systemd Service)

For production deployment with auto-start on boot:

1. **Install as a systemd service:**

   ```bash
   sudo ./install-service.sh
   ```

   This will:

   - Install the service to start on boot
   - Run in production mode on port 80
   - Automatically restart if it crashes
   - Log to system journal

2. **Service management commands:**

   ```bash
   # Check status
   sudo systemctl status camper-main-controller

   # Start/stop/restart
   sudo systemctl start camper-main-controller
   sudo systemctl stop camper-main-controller
   sudo systemctl restart camper-main-controller

   # View logs
   sudo journalctl -u camper-main-controller -f

   # Disable auto-start
   sudo systemctl disable camper-main-controller
   ```

### Manual Setup

1. **Create virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python3 app.py
   ```

## API Endpoints

### Update Device

- **URL:** `PUT /api/v1/device/{id}`
- **Description:** Register or update device information
- **Parameters:**
  - `id` (path parameter): Device identifier
- **Request Body:** JSON with device_type
  ```json
  { "device_type": "REAR_CAMERA" }
  ```
- **Success Response:**
  ```json
  { "status": "success" }
  ```
- **Error Responses:**
  - `400`: `{"error": "Invalid device ID"}` or `{"error": "Invalid device type"}`
  - `500`: `{"error": "Internal server error"}`

### List Devices

- **URL:** `GET /api/v1/devices`
- **Description:** Get list of all registered devices
- **Success Response:**
  ```json
  [
    {
      "device_id": "rear-camera",
      "device_type": "REAR_CAMERA",
      "addr": "192.168.1.100",
      "last_seen": "2025-08-23T18:42:00.123456"
    }
  ]
  ```

### Health Check

- **URL:** `GET /health`
- **Description:** Check API health status
- **Success Response:**
  ```json
  {
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00.000000",
    "service": "main-controller"
  }
  ```

## Usage Examples

### Using curl (Development Mode - Port 8080)

```bash
# Health check
curl http://localhost:8080/health

# Register/update device
curl -X PUT http://localhost:8080/api/v1/device/rear-camera \
  -H "Content-Type: application/json" \
  -d '{"device_type": "REAR_CAMERA"}'

# List all devices
curl http://localhost:8080/api/v1/devices
```

### Using curl (Production Mode - Port 80)

```bash
# Health check
curl http://localhost/health

# Register/update device
curl -X PUT http://localhost/api/v1/device/rear-camera \
  -H "Content-Type: application/json" \
  -d '{"device_type": "REAR_CAMERA"}'

# List all devices
curl http://localhost/api/v1/devices
```

### From another device on the network

```bash
# Replace RASPBERRY_PI_IP with your Pi's IP address
# Development mode (port 8080)
curl -X PUT http://RASPBERRY_PI_IP:8080/api/v1/device/rear-camera \
  -H "Content-Type: application/json" \
  -d '{"device_type": "REAR_CAMERA"}'

# Production mode (port 80)
curl -X PUT http://RASPBERRY_PI_IP/api/v1/device/rear-camera \
  -H "Content-Type: application/json" \
  -d '{"device_type": "REAR_CAMERA"}'
```

## Configuration

The API automatically configures based on environment:

### Development Mode (default)

- **Host:** 0.0.0.0 (accepts connections from any IP)
- **Port:** 8080
- **Debug:** True
- **Environment:** Set `FLASK_ENV=development` or leave unset

### Production Mode

- **Host:** 0.0.0.0 (accepts connections from any IP)
- **Port:** 80 (requires root/sudo)
- **Debug:** False
- **Environment:** Set `FLASK_ENV=production`
- **Logging:** File (`main-controller.log`) and console output

### Device Management

- **Device Expiry:** 30 seconds (devices are removed if not seen)
- **Cleanup Interval:** 1 second
- **Supported Device Types:** REAR_CAMERA (extensible)

## Logging

Logs are written to:

- **File:** `main-controller.log` in the same directory
- **Console:** Standard output

Log format includes timestamp, log level, and message for easy debugging.

## File Structure

```
main-controller/
├── app.py                          # Main Flask application
├── config.py                       # Configuration and Flask setup
├── requirements.txt                # Python dependencies
├── run.sh                         # Development startup script
├── camper-main-controller.service  # Systemd service file
├── install-service.sh             # Service installation script
├── README.md                      # This file
└── main-controller.log            # Log file (created when running)
```

## Development

To extend the API:

1. Add new routes in `app.py`
2. Update logging as needed
3. Test with the health endpoint first
4. Use the existing error handling patterns

## Troubleshooting

### Common Issues

1. **Port already in use:**

   ```bash
   # Find process using port 8080 (dev) or 80 (prod)
   lsof -i :8080
   lsof -i :80
   # Kill the process if needed
   kill -9 <PID>
   ```

2. **Permission denied on scripts:**

   ```bash
   chmod +x run.sh
   chmod +x install-service.sh
   ```

3. **Port 80 permission denied:**

   Production mode requires root privileges for port 80:

   ```bash
   sudo ./run.sh
   # Or use the systemd service
   sudo ./install-service.sh
   ```

4. **Python/pip not found:**

   ```bash
   # Install Python 3 and pip on Raspberry Pi
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   ```

5. **Service not starting:**
   ```bash
   # Check service status and logs
   sudo systemctl status camper-main-controller
   sudo journalctl -u camper-main-controller -f
   ```

### Logs

Check `main-controller.log` for detailed error information and request logs.

## Network Access

The API is configured to accept connections from any IP address (0.0.0.0). To access from other devices:

1. Find your Raspberry Pi's IP address:

   ```bash
   hostname -I
   ```

2. Access the API from other devices using:

   ```
   # Development mode
   http://RASPBERRY_PI_IP:8080/api/v1/device/{id}

   # Production mode
   http://RASPBERRY_PI_IP/api/v1/device/{id}
   ```

## Security Note

This is a basic implementation. For production use, consider adding:

- Authentication/authorization
- HTTPS/TLS encryption
- Rate limiting
- Input sanitization
- Firewall rules
