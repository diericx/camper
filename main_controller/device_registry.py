"""
In-memory device registry for the main controller.
Handles device registration, validation, and cleanup using Python dictionaries.
"""

import threading
from datetime import datetime
from typing import Dict, List, Optional, Any

from shared.constants import *
from shared.exceptions import *
from shared.utils import is_device_inactive, should_remove_device, validate_device_type, validate_ip_address, validate_port
from shared.logging_config import log_device_event


class DeviceRegistry:
    """
    In-memory device registry using Python dictionaries.
    Thread-safe implementation for concurrent access.
    """
    
    def __init__(self, logger=None):
        """
        Initialize the device registry.
        
        Args:
            logger: Logger instance for logging events
        """
        self.logger = logger
        self._lock = threading.RLock()  # Reentrant lock for thread safety
        
        # In-memory device storage
        self._devices: Dict[str, Dict[str, Any]] = {}
        
        # Device type limits configuration
        self._device_type_limits = DEVICE_TYPE_LIMITS.copy()
        
        if self.logger:
            self.logger.info("Device registry initialized with in-memory storage")
    
    def register_device(self, device_id: str, device_type: str, ip_address: str, port: int) -> bool:
        """
        Register or update a device in the registry.
        
        Args:
            device_id (str): Unique device identifier
            device_type (str): Type of device (e.g., 'rear-camera')
            ip_address (str): Device IP address
            port (int): Device port number
            
        Returns:
            bool: True if registration successful
            
        Raises:
            InvalidDeviceTypeError: If device type is not supported
            DeviceTypeLimitExceededError: If device type limit is exceeded
            DeviceRegistrationError: If registration data is invalid
        """
        with self._lock:
            # Validate input data
            if not device_id or not isinstance(device_id, str):
                raise DeviceRegistrationError("Device ID must be a non-empty string")
            
            if not validate_device_type(device_type):
                raise InvalidDeviceTypeError(f"Invalid device type: {device_type}")
            
            if not validate_ip_address(ip_address):
                raise DeviceRegistrationError(f"Invalid IP address: {ip_address}")
            
            if not validate_port(port):
                raise DeviceRegistrationError(f"Invalid port: {port}")
            
            # Check if this is a new device registration (not a heartbeat update)
            is_new_device = device_id not in self._devices
            
            if is_new_device:
                # Check device type limits for new devices
                if not self._can_register_device_type(device_type):
                    current_count = self._count_devices_by_type(device_type)
                    max_count = self._device_type_limits.get(device_type, 0)
                    raise DeviceTypeLimitExceededError(
                        f"Device type '{device_type}' limit exceeded. "
                        f"Current: {current_count}, Max: {max_count}"
                    )
            
            # Register or update device
            now = datetime.now()
            
            if is_new_device:
                self._devices[device_id] = {
                    'device_type': device_type,
                    'ip_address': ip_address,
                    'port': port,
                    'status': DEVICE_STATUS_ACTIVE,
                    'created_at': now,
                    'last_seen': now,
                    'failure_count': 0
                }
                
                if self.logger:
                    log_device_event(
                        self.logger, 'registration', device_id, device_type,
                        ip_address=ip_address, port=port, action='new_device'
                    )
            else:
                # Update existing device (heartbeat)
                device = self._devices[device_id]
                device['ip_address'] = ip_address
                device['port'] = port
                device['last_seen'] = now
                device['status'] = DEVICE_STATUS_ACTIVE
                device['failure_count'] = 0  # Reset failure count on successful heartbeat
                
                if self.logger:
                    log_device_event(
                        self.logger, 'heartbeat', device_id, device_type,
                        ip_address=ip_address, port=port, action='update'
                    )
            
            return True
    
    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Get device information by ID.
        
        Args:
            device_id (str): Device identifier
            
        Returns:
            Optional[Dict[str, Any]]: Device information or None if not found
        """
        with self._lock:
            return self._devices.get(device_id, {}).copy() if device_id in self._devices else None
    
    def get_all_devices(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered devices.
        
        Returns:
            Dict[str, Dict[str, Any]]: All devices in the registry
        """
        with self._lock:
            return {device_id: device.copy() for device_id, device in self._devices.items()}
    
    def get_active_devices(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active devices.
        
        Returns:
            Dict[str, Dict[str, Any]]: Active devices only
        """
        with self._lock:
            active_devices = {}
            for device_id, device in self._devices.items():
                if device['status'] == DEVICE_STATUS_ACTIVE and not is_device_inactive(device['last_seen']):
                    active_devices[device_id] = device.copy()
            return active_devices
    
    def get_devices_by_type(self, device_type: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all devices of a specific type.
        
        Args:
            device_type (str): Device type to filter by
            
        Returns:
            Dict[str, Dict[str, Any]]: Devices of the specified type
        """
        with self._lock:
            devices_by_type = {}
            for device_id, device in self._devices.items():
                if device['device_type'] == device_type:
                    devices_by_type[device_id] = device.copy()
            return devices_by_type
    
    def remove_device(self, device_id: str) -> bool:
        """
        Remove a device from the registry.
        
        Args:
            device_id (str): Device identifier
            
        Returns:
            bool: True if device was removed, False if not found
        """
        with self._lock:
            if device_id in self._devices:
                device = self._devices.pop(device_id)
                
                if self.logger:
                    log_device_event(
                        self.logger, 'removal', device_id, device['device_type'],
                        reason='manual_removal'
                    )
                
                return True
            return False
    
    def cleanup_inactive_devices(self) -> List[str]:
        """
        Remove devices that haven't been seen for too long.
        
        Returns:
            List[str]: List of removed device IDs
        """
        with self._lock:
            removed_devices = []
            devices_to_remove = []
            
            # First pass: identify devices to remove
            for device_id, device in self._devices.items():
                if should_remove_device(device['last_seen']):
                    devices_to_remove.append(device_id)
                elif is_device_inactive(device['last_seen']):
                    # Mark as inactive but don't remove yet
                    device['status'] = DEVICE_STATUS_INACTIVE
            
            # Second pass: remove devices
            for device_id in devices_to_remove:
                device = self._devices.pop(device_id)
                removed_devices.append(device_id)
                
                if self.logger:
                    log_device_event(
                        self.logger, 'cleanup', device_id, device['device_type'],
                        reason='inactive_timeout',
                        last_seen=device['last_seen'].isoformat()
                    )
            
            if removed_devices and self.logger:
                self.logger.info(f"Cleanup completed: removed {len(removed_devices)} inactive devices")
            
            return removed_devices
    
    def increment_failure_count(self, device_id: str) -> int:
        """
        Increment the failure count for a device.
        
        Args:
            device_id (str): Device identifier
            
        Returns:
            int: New failure count, or -1 if device not found
        """
        with self._lock:
            if device_id in self._devices:
                self._devices[device_id]['failure_count'] += 1
                failure_count = self._devices[device_id]['failure_count']
                
                if self.logger:
                    log_device_event(
                        self.logger, 'failure', device_id, 
                        self._devices[device_id]['device_type'],
                        failure_count=failure_count
                    )
                
                return failure_count
            return -1
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics.
        
        Returns:
            Dict[str, Any]: Registry statistics
        """
        with self._lock:
            stats = {
                'total_devices': len(self._devices),
                'active_devices': 0,
                'inactive_devices': 0,
                'devices_by_type': {},
                'device_type_limits': self._device_type_limits.copy()
            }
            
            for device in self._devices.values():
                device_type = device['device_type']
                
                # Count by status
                if device['status'] == DEVICE_STATUS_ACTIVE and not is_device_inactive(device['last_seen']):
                    stats['active_devices'] += 1
                else:
                    stats['inactive_devices'] += 1
                
                # Count by type
                if device_type not in stats['devices_by_type']:
                    stats['devices_by_type'][device_type] = 0
                stats['devices_by_type'][device_type] += 1
            
            return stats
    
    def _can_register_device_type(self, device_type: str) -> bool:
        """
        Check if a device type can be registered (within limits).
        
        Args:
            device_type (str): Device type to check
            
        Returns:
            bool: True if device type can be registered
        """
        current_count = self._count_devices_by_type(device_type)
        max_count = self._device_type_limits.get(device_type, 0)
        return current_count < max_count
    
    def _count_devices_by_type(self, device_type: str) -> int:
        """
        Count devices of a specific type.
        
        Args:
            device_type (str): Device type to count
            
        Returns:
            int: Number of devices of the specified type
        """
        count = 0
        for device in self._devices.values():
            if device['device_type'] == device_type:
                count += 1
        return count
    
    def clear_registry(self) -> None:
        """
        Clear all devices from the registry.
        Used for testing or system reset.
        """
        with self._lock:
            device_count = len(self._devices)
            self._devices.clear()
            
            if self.logger:
                self.logger.info(f"Registry cleared: removed {device_count} devices")