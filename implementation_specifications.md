# Implementation Specifications

## Technical Requirements

### Dependencies

```
Flask==2.3.3
SQLite3 (built-in)
requests==2.31.0
python-dotenv==1.0.0
APScheduler==3.10.4
```

### Python Version

- Python 3.8+ (compatible with Raspberry Pi OS)

## Detailed Component Specifications

### 1. Main Controller API Implementation

#### Core Features

- **Device Registration**: Handle PUT requests for device registration
- **Device Registry**: In-memory dictionary for device tracking
- **Heartbeat Monitoring**: Background task to clean up inactive devices
- **Device Type Limits**: Enforce single instance per device type
- **API Validation**: Input validation and error handling

#### Key Classes and Methods

```python
class DeviceRegistry:
    def __init__(self):
        self.devices = {}  # In-memory device storage
        self.device_type_limits = {"rear-camera": 1}

    def register_device(device_id, device_type, ip_address, port)
    def update_heartbeat(device_id)
    def get_active_devices()
    def cleanup_inactive_devices()
    def is_device_type_available(device_type)
    def get_device_by_id(device_id)
    def remove_device(device_id)
    def count_devices_by_type(device_type)

class MainControllerAPI:
    def register_device_endpoint()
    def get_devices_endpoint()
    def control_device_endpoint()
```

#### Database Schema Details

```sql
-- Device registry table
CREATE TABLE devices (
    id TEXT PRIMARY KEY,
    device_type TEXT NOT NULL,
    ip_address TEXT NOT NULL,
    port INTEGER NOT NULL,
    last_seen TIMESTAMP NOT NULL,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    failure_count INTEGER DEFAULT 0
);

-- Device type limits
CREATE TABLE device_type_limits (
    device_type TEXT PRIMARY KEY,
    max_count INTEGER NOT NULL,
    description TEXT
);

-- Initial data
INSERT INTO device_type_limits VALUES
('rear-camera', 1, 'Rear camera controller - single instance only');
```

### 2. Device Controller Base Implementation

#### Base Controller Features

- **Configuration Loading**: Read device config on startup
- **Auto-Registration**: Register with main controller on boot
- **Heartbeat Service**: Continuous registration updates
- **Error Handling**: Graceful failure handling and retry logic

#### Key Classes and Methods

```python
class BaseDeviceController:
    def __init__(config_path)
    def load_config()
    def register_with_main_controller()
    def start_heartbeat_service()
    def handle_registration_failure()
    def create_flask_app()
    def run()

class HeartbeatService:
    def __init__(device_controller)
    def start()
    def send_heartbeat()
    def handle_heartbeat_failure()
```

### 3. Rear Camera Controller Implementation

#### Camera Control Features

- **Movement Control**: Up/down camera movement
- **Status Reporting**: Camera position and health status
- **Error Recovery**: Handle movement failures gracefully

#### API Endpoints Implementation

```python
@app.route('/api/v1/rear-camera/up', methods=['POST'])
def move_camera_up():
    # Implementation for camera up movement
    pass

@app.route('/api/v1/rear-camera/down', methods=['POST'])
def move_camera_down():
    # Implementation for camera down movement
    pass

@app.route('/api/v1/rear-camera/status', methods=['GET'])
def get_camera_status():
    # Return current camera status
    pass
```

### 4. Configuration System

#### Main Controller Configuration

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": false
  },
  "database": {
    "path": "data/devices.db"
  },
  "cleanup": {
    "inactive_threshold_minutes": 2,
    "removal_threshold_minutes": 5,
    "cleanup_interval_seconds": 60
  },
  "wifi": {
    "ssid": "CamperControl",
    "password": "camper123",
    "ip_range": "192.168.4.0/24"
  }
}
```

#### Device Configuration Template

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
    "retry_attempts": 3,
    "retry_delay_seconds": 5
  },
  "device_specific": {
    "camera": {
      "movement_speed": "slow",
      "position_limits": {
        "up_limit": 90,
        "down_limit": -30
      }
    }
  }
}
```

### 5. Error Handling Strategy

#### Main Controller Error Handling

- **Registration Conflicts**: Return 409 for device type limits
- **Invalid Data**: Return 400 for malformed requests
- **Database Errors**: Log and return 500 with retry guidance
- **Device Communication**: Handle timeouts and connection failures

#### Device Controller Error Handling

- **Registration Failures**: Exponential backoff retry
- **Network Issues**: Graceful degradation and reconnection
- **Hardware Failures**: Log errors and attempt recovery
- **Configuration Errors**: Fail fast with clear error messages

### 6. Logging Strategy

#### Log Levels and Categories

```python
# Main Controller Logging
logger.info("Device registered: {device_id} ({device_type})")
logger.warning("Device type limit reached: {device_type}")
logger.error("Database connection failed: {error}")
logger.debug("Heartbeat received from: {device_id}")

# Device Controller Logging
logger.info("Device started: {device_id}")
logger.warning("Registration failed, retrying: {attempt}/{max_attempts}")
logger.error("Hardware control failed: {error}")
logger.debug("Heartbeat sent successfully")
```

#### Log File Structure

```
logs/
├── main_controller.log
├── rear_camera.log
└── system.log
```

### 7. Service Management

#### Systemd Service Files

**Main Controller Service**

```ini
[Unit]
Description=Camper Main Controller API
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/camper-control-system
ExecStart=/usr/bin/python3 main_controller/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Device Controller Service Template**

```ini
[Unit]
Description=Camper Device Controller
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/camper-control-system
ExecStart=/usr/bin/python3 device_controllers/start_device.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 8. Testing Strategy

#### Unit Tests

- Device registration logic
- Database operations
- Configuration loading
- Error handling scenarios

#### Integration Tests

- End-to-end device registration
- Heartbeat mechanism
- Device cleanup process
- API endpoint functionality

#### Hardware Tests

- Camera movement control
- Network connectivity
- WiFi access point functionality
- Device boot sequence

### 9. Deployment Checklist

#### Raspberry Pi Setup

1. Install Raspberry Pi OS
2. Configure WiFi access point
3. Install Python dependencies
4. Create directory structure
5. Initialize database
6. Configure systemd services
7. Test main controller startup

#### ESP8266 Setup

1. Flash device firmware
2. Configure device-specific settings
3. Test WiFi connectivity
4. Verify registration process
5. Test device-specific APIs
6. Configure auto-start service

### 10. Performance Considerations

#### Resource Usage

- **Memory**: Estimated 50MB per device controller
- **CPU**: Minimal usage during normal operation
- **Network**: ~1KB per heartbeat message
- **Storage**: SQLite database growth ~1KB per device

#### Scalability Limits

- **Max Devices**: 50 devices per Raspberry Pi
- **Network Bandwidth**: 802.11n sufficient for control traffic
- **Database Size**: SQLite handles thousands of device records
- **Response Time**: <100ms for device registration

This specification provides the detailed technical foundation needed to implement the distributed device control system.
