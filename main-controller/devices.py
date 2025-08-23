import time
from enum import Enum
import threading

from flask import json


DEVICE_EXPIRE_SECONDS = 30  

class DeviceType(Enum):
    REAR_CAMERA = "REAR_CAMERA"

class Device:
    def __init__(self, device_type: DeviceType, addr: str):
        self.device_type = device_type
        self.addr = addr
        self.last_seen = time.time()

    def __str__(self):
        return json.dumps({
            "device_type": self.device_type.value,  # Use .value to get the string
            "addr": self.addr,
            "last_seen": str(self.last_seen)
        })

devices: Device = {}

def start_stale_device_cleanup_thread(logger):
    """Remove devices that haven't been seen recently"""
    current_time = time.time()
    expired_devices = []
    
    for device_id, device in devices.items():
        if current_time - device.last_seen > DEVICE_EXPIRE_SECONDS:
            expired_devices.append(device_id)
    
    for device_id in expired_devices:
        logger.info(f"Removing stale device: {device_id}")
        del devices[device_id]
    
    # Schedule next cleanup
    threading.Timer(1.0, start_stale_device_cleanup_thread, args=[logger]).start()