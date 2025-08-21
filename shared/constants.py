"""
System constants for the distributed device control system.
"""

# API Configuration
DEFAULT_MAIN_CONTROLLER_PORT = 5000
DEFAULT_DEVICE_PORT_START = 5001

# Device Types
DEVICE_TYPE_REAR_CAMERA = "rear-camera"

# Device Type Limits
DEVICE_TYPE_LIMITS = {
    DEVICE_TYPE_REAR_CAMERA: 1  # Only one rear-camera allowed
}

# Timing Configuration (in seconds)
DEFAULT_HEARTBEAT_INTERVAL = 30
DEVICE_INACTIVE_THRESHOLD = 120  # 2 minutes
DEVICE_REMOVAL_THRESHOLD = 300   # 5 minutes
CLEANUP_INTERVAL = 60           # 1 minute

# Network Configuration
WIFI_AP_IP = "192.168.4.1"
WIFI_AP_NETWORK = "192.168.4.0/24"

# API Endpoints
API_VERSION = "v1"
MAIN_CONTROLLER_BASE_PATH = f"/api/{API_VERSION}/main-controller"
DEVICE_REGISTRATION_PATH = f"{MAIN_CONTROLLER_BASE_PATH}/device"

# Device Status
DEVICE_STATUS_ACTIVE = "active"
DEVICE_STATUS_INACTIVE = "inactive"

# HTTP Status Codes
HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_CONFLICT = 409
HTTP_INTERNAL_SERVER_ERROR = 500