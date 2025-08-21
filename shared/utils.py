"""
Shared utility functions for the distributed device control system.
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import requests

from .constants import *
from .exceptions import *


def load_json_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a JSON file.
    
    Args:
        config_path (str): Path to the JSON configuration file
        
    Returns:
        Dict[str, Any]: Configuration dictionary
        
    Raises:
        ConfigurationError: If the file cannot be loaded or parsed
    """
    try:
        if not os.path.exists(config_path):
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        return config
    except json.JSONDecodeError as e:
        raise ConfigurationError(f"Invalid JSON in configuration file {config_path}: {e}")
    except Exception as e:
        raise ConfigurationError(f"Error loading configuration file {config_path}: {e}")


def save_json_config(config: Dict[str, Any], config_path: str) -> None:
    """
    Save configuration to a JSON file.
    
    Args:
        config (Dict[str, Any]): Configuration dictionary
        config_path (str): Path to save the JSON configuration file
        
    Raises:
        ConfigurationError: If the file cannot be saved
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2, default=str)
    except Exception as e:
        raise ConfigurationError(f"Error saving configuration file {config_path}: {e}")


def validate_device_type(device_type: str) -> bool:
    """
    Validate if a device type is supported.
    
    Args:
        device_type (str): Device type to validate
        
    Returns:
        bool: True if device type is valid
    """
    return device_type in DEVICE_TYPE_LIMITS


def validate_ip_address(ip_address: str) -> bool:
    """
    Basic validation for IP address format.
    
    Args:
        ip_address (str): IP address to validate
        
    Returns:
        bool: True if IP address format is valid
    """
    try:
        parts = ip_address.split('.')
        if len(parts) != 4:
            return False
        
        for part in parts:
            if not 0 <= int(part) <= 255:
                return False
        
        return True
    except (ValueError, AttributeError):
        return False


def validate_port(port: int) -> bool:
    """
    Validate if a port number is valid.
    
    Args:
        port (int): Port number to validate
        
    Returns:
        bool: True if port is valid
    """
    return isinstance(port, int) and 1 <= port <= 65535


def is_device_inactive(last_seen: datetime, threshold_seconds: int = DEVICE_INACTIVE_THRESHOLD) -> bool:
    """
    Check if a device is considered inactive based on last seen time.
    
    Args:
        last_seen (datetime): Last time the device was seen
        threshold_seconds (int): Threshold in seconds for considering device inactive
        
    Returns:
        bool: True if device is inactive
    """
    return datetime.now() - last_seen > timedelta(seconds=threshold_seconds)


def should_remove_device(last_seen: datetime, threshold_seconds: int = DEVICE_REMOVAL_THRESHOLD) -> bool:
    """
    Check if a device should be removed from registry based on last seen time.
    
    Args:
        last_seen (datetime): Last time the device was seen
        threshold_seconds (int): Threshold in seconds for removing device
        
    Returns:
        bool: True if device should be removed
    """
    return datetime.now() - last_seen > timedelta(seconds=threshold_seconds)


def make_device_request(ip_address: str, port: int, method: str, path: str, 
                       data: Optional[Dict] = None, timeout: int = 5) -> requests.Response:
    """
    Make an HTTP request to a device.
    
    Args:
        ip_address (str): Device IP address
        port (int): Device port
        method (str): HTTP method (GET, POST, PUT, DELETE)
        path (str): Request path
        data (Optional[Dict]): Request data for POST/PUT requests
        timeout (int): Request timeout in seconds
        
    Returns:
        requests.Response: HTTP response
        
    Raises:
        DeviceCommunicationError: If the request fails
    """
    try:
        url = f"http://{ip_address}:{port}{path}"
        
        if method.upper() == 'GET':
            response = requests.get(url, timeout=timeout)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, timeout=timeout)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, timeout=timeout)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, timeout=timeout)
        else:
            raise DeviceCommunicationError(f"Unsupported HTTP method: {method}")
        
        return response
    
    except requests.exceptions.Timeout:
        raise DeviceCommunicationError(f"Request timeout to {ip_address}:{port}")
    except requests.exceptions.ConnectionError:
        raise DeviceCommunicationError(f"Connection error to {ip_address}:{port}")
    except requests.exceptions.RequestException as e:
        raise DeviceCommunicationError(f"Request failed to {ip_address}:{port}: {e}")


def format_device_info(device_data: Dict[str, Any]) -> str:
    """
    Format device information for logging.
    
    Args:
        device_data (Dict[str, Any]): Device data dictionary
        
    Returns:
        str: Formatted device information string
    """
    return (f"Device(id={device_data.get('id', 'unknown')}, "
            f"type={device_data.get('device_type', 'unknown')}, "
            f"ip={device_data.get('ip_address', 'unknown')}, "
            f"port={device_data.get('port', 'unknown')}, "
            f"status={device_data.get('status', 'unknown')})")


def get_current_timestamp() -> str:
    """
    Get current timestamp in ISO format.
    
    Returns:
        str: Current timestamp in ISO format
    """
    return datetime.now().isoformat()


def parse_timestamp(timestamp_str: str) -> datetime:
    """
    Parse ISO timestamp string to datetime object.
    
    Args:
        timestamp_str (str): ISO timestamp string
        
    Returns:
        datetime: Parsed datetime object
        
    Raises:
        ValueError: If timestamp format is invalid
    """
    try:
        return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except ValueError as e:
        raise ValueError(f"Invalid timestamp format: {timestamp_str}") from e


def retry_operation(operation, max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Retry an operation with exponential backoff.
    
    Args:
        operation: Function to retry
        max_retries (int): Maximum number of retries
        delay (float): Initial delay between retries in seconds
        backoff (float): Backoff multiplier for delay
        
    Returns:
        Any: Result of the operation
        
    Raises:
        Exception: Last exception if all retries fail
    """
    last_exception = None
    current_delay = delay
    
    for attempt in range(max_retries + 1):
        try:
            return operation()
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                time.sleep(current_delay)
                current_delay *= backoff
            else:
                break
    
    raise last_exception