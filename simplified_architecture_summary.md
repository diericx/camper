# Simplified Architecture Summary - In-Memory Design

## Key Architecture Changes Made

### ✅ **Removed SQLite Database Dependency**

- **Before**: SQLite database for device persistence
- **After**: Simple Python dictionaries for in-memory storage
- **Benefits**: Simpler deployment, no database setup, faster operations
- **Trade-off**: Device registry lost on restart (acceptable for this use case)

### ✅ **Simplified Data Storage**

```python
# Main device registry - simple dictionary
device_registry = {
    "rear-camera-001": {
        "device_type": "rear-camera",
        "ip_address": "192.168.4.100",
        "port": 5001,
        "last_seen": datetime.now(),
        "status": "active",
        "created_at": datetime.now()
    }
}

# Device type limits - simple configuration
device_type_limits = {
    "rear-camera": 1  # Only one rear-camera allowed
}
```

### ✅ **Updated Dependencies**

```
Flask==2.3.3          # Web framework
requests==2.31.0      # HTTP client for device communication
python-dotenv==1.0.0  # Environment configuration
APScheduler==3.10.4   # Background cleanup tasks
```

## System Behavior with In-Memory Storage

### **Device Registration Flow**

1. ESP8266 boots and connects to Pi's WiFi
2. Device calls `PUT /api/v1/main-controller/device/{id}`
3. Main controller checks `device_type_limits` dictionary
4. If allowed, stores device info in `device_registry` dictionary
5. Returns success/error response

### **Device Type Enforcement**

```python
def can_register_device(device_type):
    current_count = len([d for d in device_registry.values()
                        if d['device_type'] == device_type])
    max_allowed = device_type_limits.get(device_type, 0)
    return current_count < max_allowed
```

### **Automatic Cleanup**

- Background task runs every 60 seconds
- Removes devices not seen for 5 minutes
- No persistence needed - devices re-register on restart

### **Restart Behavior**

- Main controller starts with empty registry
- Devices automatically re-register within 30 seconds
- System reaches steady state quickly

## Advantages of In-Memory Approach

### **Simplicity**

- No database installation or configuration
- No schema migrations or data corruption issues
- Easier debugging and troubleshooting

### **Performance**

- Faster device lookups (dictionary access)
- No I/O overhead for device operations
- Minimal memory footprint

### **Reliability**

- No database lock issues
- No disk space concerns
- Self-healing on restart

### **Development Speed**

- Faster to implement and test
- No database mocking in tests
- Easier deployment process

## Acceptable Trade-offs

### **Data Loss on Restart**

- **Impact**: Device registry cleared on main controller restart
- **Mitigation**: Devices re-register automatically within 30 seconds
- **Acceptable**: For this IoT control system, temporary data loss is fine

### **No Historical Data**

- **Impact**: No device registration history
- **Mitigation**: Logging provides audit trail if needed
- **Acceptable**: Current system only needs active device tracking

### **Memory Limitations**

- **Impact**: Registry size limited by available RAM
- **Mitigation**: Cleanup removes inactive devices
- **Acceptable**: Expected device count is low (< 50 devices)

## Implementation Simplifications

### **No Database Layer**

```python
# Before: Complex database operations
def register_device(device_id, device_type, ip, port):
    cursor.execute("INSERT INTO devices...")
    connection.commit()

# After: Simple dictionary operations
def register_device(device_id, device_type, ip, port):
    device_registry[device_id] = {
        "device_type": device_type,
        "ip_address": ip,
        "port": port,
        "last_seen": datetime.now()
    }
```

### **Simplified Configuration**

```json
{
  "server": { "host": "0.0.0.0", "port": 5000 },
  "registry": { "cleanup_on_startup": true },
  "cleanup": {
    "inactive_threshold_minutes": 2,
    "removal_threshold_minutes": 5
  }
}
```

### **Easier Testing**

```python
# Simple test setup - no database mocking needed
def test_device_registration():
    registry = DeviceRegistry()
    result = registry.register_device("test-001", "rear-camera", "192.168.4.100", 5001)
    assert result == True
    assert "test-001" in registry.devices
```

## Updated File Structure

**Removed Files:**

- `main_controller/database.py` - No longer needed
- `data/devices.db` - No database file
- Database migration scripts

**Simplified Files:**

- `main_controller/device_registry.py` - Pure Python dictionaries
- `requirements.txt` - Removed SQLite dependency
- Configuration files - Simplified structure

This simplified architecture maintains all the core functionality while being much easier to implement, deploy, and maintain. The in-memory approach is perfect for this IoT control system where simplicity and reliability are more important than data persistence.
