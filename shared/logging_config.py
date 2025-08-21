"""
Logging configuration for the distributed device control system.
"""

import logging
import logging.handlers
import os
from datetime import datetime


def setup_logging(service_name, log_level="INFO", log_dir="logs"):
    """
    Set up logging configuration for a service.
    
    Args:
        service_name (str): Name of the service (e.g., 'main_controller', 'rear_camera')
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir (str): Directory to store log files
    
    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # File handler with rotation
    log_file = os.path.join(log_dir, f"{service_name}.log")
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(simple_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


def log_device_event(logger, event_type, device_id, device_type=None, **kwargs):
    """
    Log a device-related event with structured information.
    
    Args:
        logger: Logger instance
        event_type (str): Type of event (e.g., 'registration', 'heartbeat', 'cleanup')
        device_id (str): Device identifier
        device_type (str, optional): Type of device
        **kwargs: Additional event data
    """
    event_data = {
        'event': event_type,
        'device_id': device_id,
        'timestamp': datetime.now().isoformat()
    }
    
    if device_type:
        event_data['device_type'] = device_type
    
    event_data.update(kwargs)
    
    # Format the log message
    message_parts = [f"{k}={v}" for k, v in event_data.items()]
    message = " | ".join(message_parts)
    
    logger.info(message)


def log_api_request(logger, method, path, remote_addr, status_code, response_time_ms=None):
    """
    Log an API request with structured information.
    
    Args:
        logger: Logger instance
        method (str): HTTP method
        path (str): Request path
        remote_addr (str): Client IP address
        status_code (int): HTTP status code
        response_time_ms (float, optional): Response time in milliseconds
    """
    log_data = {
        'type': 'api_request',
        'method': method,
        'path': path,
        'remote_addr': remote_addr,
        'status_code': status_code,
        'timestamp': datetime.now().isoformat()
    }
    
    if response_time_ms is not None:
        log_data['response_time_ms'] = round(response_time_ms, 2)
    
    message_parts = [f"{k}={v}" for k, v in log_data.items()]
    message = " | ".join(message_parts)
    
    if status_code >= 400:
        logger.warning(message)
    else:
        logger.info(message)


def log_system_event(logger, event_type, message, **kwargs):
    """
    Log a system-level event.
    
    Args:
        logger: Logger instance
        event_type (str): Type of system event
        message (str): Event message
        **kwargs: Additional event data
    """
    event_data = {
        'type': 'system_event',
        'event': event_type,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }
    
    event_data.update(kwargs)
    
    message_parts = [f"{k}={v}" for k, v in event_data.items()]
    log_message = " | ".join(message_parts)
    
    logger.info(log_message)