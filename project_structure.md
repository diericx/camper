# Project Structure and File Organization

## Complete Directory Structure

```
camper-control-system/
├── README.md
├── requirements.txt
├── setup.py
├── .env.example
├── .gitignore
│
├── main_controller/
│   ├── __init__.py
│   ├── app.py                 # Main Flask application
│   ├── device_registry.py     # Device management logic (in-memory)
│   ├── config.py             # Configuration management
│   ├── cleanup_service.py    # Background cleanup tasks
│   └── api/
│       ├── __init__.py
│       ├── device_routes.py  # Device registration endpoints
│       └── control_routes.py # Device control endpoints
│
├── device_controllers/
│   ├── __init__.py
│   ├── base_controller.py    # Base device controller class
│   ├── heartbeat_service.py  # Heartbeat management
│   ├── start_device.py       # Device startup script
│   │
│   ├── rear_camera/
│   │   ├── __init__.py
│   │   ├── app.py           # Rear camera Flask app
│   │   ├── camera_control.py # Camera-specific logic
│   │   └── hardware/
│   │       ├── __init__.py
│   │       └── servo_control.py # Hardware interface
│   │
│   └── templates/            # Templates for new device types
│       ├── device_template/
│       │   ├── __init__.py
│       │   ├── app.py
│       │   └── device_control.py
│       └── README.md
│
├── shared/
│   ├── __init__.py
│   ├── utils.py             # Shared utilities
│   ├── constants.py         # System constants
│   ├── exceptions.py        # Custom exceptions
│   └── logging_config.py    # Logging configuration
│
├── config/
│   ├── main_config.json     # Main controller configuration
│   ├── device_configs/      # Device-specific configurations
│   │   ├── rear_camera_config.json
│   │   └── template_config.json
│   └── wifi/
│       ├── hostapd.conf     # WiFi access point config
│       └── dnsmasq.conf     # DHCP configuration
│
├── scripts/
│   ├── setup/
│   │   ├── setup_wifi_ap.sh     # WiFi access point setup
│   │   ├── install_dependencies.sh # System dependencies
│   │   └── create_services.sh   # Systemd service creation
│   ├── deployment/
│   │   ├── deploy_main.sh       # Deploy main controller
│   │   ├── deploy_device.sh     # Deploy device controller
│   │   └── update_system.sh     # System updates
│   └── maintenance/
│       ├── backup_database.sh   # Database backup
│       ├── clean_logs.sh        # Log rotation
│       └── health_check.sh      # System health check
│
├── data/
│   └── backups/             # Configuration backups
│
├── logs/
│   ├── main_controller.log  # Main controller logs
│   ├── devices/             # Device-specific logs
│   │   └── rear_camera.log
│   └── system.log           # System-wide logs
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test configuration
│   ├── test_main_controller.py
│   ├── test_device_registry.py
│   ├── test_rear_camera.py
│   └── integration/
│       ├── __init__.py
│       ├── test_device_registration.py
│       └── test_heartbeat_system.py
│
├── docs/
│   ├── api_documentation.md
│   ├── deployment_guide.md
│   ├── troubleshooting.md
│   └── hardware_setup.md
│
└── systemd/
    ├── camper-main-controller.service
    ├── camper-device-controller.service
    └── install_services.sh
```

## Key File Descriptions

### Core Application Files

#### `main_controller/app.py`

- Main Flask application for the Raspberry Pi controller
- Initializes database, starts cleanup service
- Registers API routes and error handlers

#### `main_controller/device_registry.py`

- Core device management logic
- Handles device registration, validation, and cleanup
- Manages device type restrictions

#### `device_controllers/base_controller.py`

- Abstract base class for all device controllers
- Provides common functionality: config loading, registration, heartbeat
- Template for creating new device types

#### `device_controllers/rear_camera/app.py`

- Specific Flask application for rear camera controller
- Implements camera control endpoints
- Inherits from base controller

### Configuration Files

#### `config/main_config.json`

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": false
  },
  "registry": {
    "cleanup_on_startup": true
  },
  "cleanup": {
    "inactive_threshold_minutes": 2,
    "removal_threshold_minutes": 5,
    "cleanup_interval_seconds": 60
  },
  "device_types": {
    "rear-camera": {
      "max_count": 1,
      "description": "Rear camera controller"
    }
  },
  "logging": {
    "level": "INFO",
    "file": "logs/main_controller.log",
    "max_size_mb": 10,
    "backup_count": 5
  }
}
```

#### `config/device_configs/rear_camera_config.json`

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
  "hardware": {
    "servo_pin": 18,
    "movement_speed": 0.5,
    "position_limits": {
      "up_degrees": 90,
      "down_degrees": -30
    }
  },
  "logging": {
    "level": "INFO",
    "file": "logs/devices/rear_camera.log"
  }
}
```

### Setup and Deployment Scripts

#### `scripts/setup/setup_wifi_ap.sh`

- Configures Raspberry Pi as WiFi access point
- Sets up hostapd and dnsmasq
- Creates isolated network for devices

#### `scripts/deployment/deploy_main.sh`

- Installs main controller on Raspberry Pi
- Creates necessary directories and permissions
- Configures and starts systemd service

#### `scripts/deployment/deploy_device.sh`

- Deploys device controller to ESP8266 or Pi
- Configures device-specific settings
- Sets up auto-start service

### Service Files

#### `systemd/camper-main-controller.service`

```ini
[Unit]
Description=Camper Main Controller API
After=network.target
Wants=network.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/home/pi/camper-control-system
ExecStart=/usr/bin/python3 -m main_controller.app
Restart=always
RestartSec=10
Environment=PYTHONPATH=/home/pi/camper-control-system

[Install]
WantedBy=multi-user.target
```

#### `systemd/camper-device-controller.service`

```ini
[Unit]
Description=Camper Device Controller
After=network.target
Wants=network.target

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/home/pi/camper-control-system
ExecStart=/usr/bin/python3 device_controllers/start_device.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=/home/pi/camper-control-system

[Install]
WantedBy=multi-user.target
```

## File Creation Priority

### Phase 1: Core Infrastructure

1. `requirements.txt` - Python dependencies
2. `shared/constants.py` - System constants
3. `shared/exceptions.py` - Custom exceptions
4. `shared/logging_config.py` - Logging setup
5. `main_controller/database.py` - Database operations

### Phase 2: Main Controller

1. `main_controller/device_registry.py` - Device management
2. `main_controller/cleanup_service.py` - Background tasks
3. `main_controller/api/device_routes.py` - Registration API
4. `main_controller/app.py` - Main Flask app

### Phase 3: Device Controllers

1. `device_controllers/base_controller.py` - Base class
2. `device_controllers/heartbeat_service.py` - Heartbeat logic
3. `device_controllers/rear_camera/camera_control.py` - Camera logic
4. `device_controllers/rear_camera/app.py` - Camera Flask app

### Phase 4: Configuration and Deployment

1. Configuration files in `config/`
2. Setup scripts in `scripts/setup/`
3. Systemd service files
4. Deployment scripts

### Phase 5: Testing and Documentation

1. Unit tests in `tests/`
2. Integration tests
3. Documentation in `docs/`
4. README and setup guides

This structure provides a clean, maintainable, and extensible foundation for the distributed device control system.
