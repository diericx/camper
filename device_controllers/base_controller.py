"""
Base device controller class providing common functionality for all device types.
Handles configuration loading, registration with main controller, and heartbeat service.
"""

import os
import sys
import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime
from flask import Flask

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.constants import *
from shared.exceptions import *
from shared.utils import load_json_config, make_device_request, retry_operation
from shared.logging_config import setup_logging, log_device_event, log_system_event
from device_controllers.heartbeat_service import HeartbeatService


class BaseDeviceController(ABC):
    """
    Abstract base class for all device controllers.
    Provides common functionality for device registration, heartbeat, and Flask app setup.
    """
    
    def __init__(self, config_path=None):
        """
        Initialize the base device controller.
        
        Args:
            config_path (str, optional): Path to device configuration file
        """
        self.config = None
        self.logger = None
        self.app = None
        self.heartbeat_service = None
        self._shutdown_event = threading.Event()
        
        # Load configuration
        self._load_configuration(config_path)
        
        # Set up logging
        self._setup_logging()
        
        # Initialize heartbeat service
        self._setup_heartbeat_service()
        
        log_system_event(
            self.logger, 'controller_init',
            f"Device controller initialized: {self.get_device_id()}"
        )
    
    def _load_configuration(self, config_path):
        """
        Load device configuration from file.
        
        Args:
            config_path (str, optional): Path to configuration file
        """
        if config_path is None:
            # Try to determine config path based on device type
            device_type = self.get_device_type()
            config_path = os.path.join(
                os.path.dirname(__file__), '..', 'config', 'device_configs',
                f'{device_type}_config.json'
            )
        
        try:
            self.config = load_json_config(config_path)
        except ConfigurationError as e:
            # Use default configuration if file not found
            self.config = self._get_default_config()
            print(f"Warning: Could not load config file {config_path}, using defaults: {e}")
    
    def _get_default_config(self):
        """
        Get default configuration for the device.
        
        Returns:
            Dict[str, Any]: Default configuration
        """
        return {
            "device_id": f"{self.get_device_type()}-001",
            "device_type": self.get_device_type(),
            "api_port": DEFAULT_DEVICE_PORT_START,
            "main_controller": {
                "ip": WIFI_AP_IP,
                "port": DEFAULT_MAIN_CONTROLLER_PORT
            },
            "heartbeat": {
                "interval_seconds": DEFAULT_HEARTBEAT_INTERVAL,
                "retry_attempts": 3,
                "retry_delay_seconds": 5
            },
            "logging": {
                "level": "INFO",
                "log_dir": "logs"
            }
        }
    
    def _setup_logging(self):
        """Set up logging for the device controller."""
        log_config = self.config.get('logging', {})
        service_name = f"{self.get_device_type()}_{self.get_device_id()}"
        
        self.logger = setup_logging(
            service_name,
            log_config.get('level', 'INFO'),
            log_config.get('log_dir', 'logs')
        )
    
    def _setup_heartbeat_service(self):
        """Set up the heartbeat service."""
        self.heartbeat_service = HeartbeatService(self, self.logger)
    
    def get_device_id(self):
        """
        Get the device ID from configuration.
        
        Returns:
            str: Device ID
        """
        return self.config.get('device_id', f"{self.get_device_type()}-unknown")
    
    @abstractmethod
    def get_device_type(self):
        """
        Get the device type identifier.
        
        Returns:
            str: Device type (e.g., 'rear-camera')
        """
        pass
    
    def get_api_port(self):
        """
        Get the API port for this device.
        
        Returns:
            int: API port number
        """
        return self.config.get('api_port', DEFAULT_DEVICE_PORT_START)
    
    def get_main_controller_info(self):
        """
        Get main controller connection information.
        
        Returns:
            Dict[str, Any]: Main controller IP and port
        """
        return self.config.get('main_controller', {
            'ip': WIFI_AP_IP,
            'port': DEFAULT_MAIN_CONTROLLER_PORT
        })
    
    def register_with_main_controller(self):
        """
        Register this device with the main controller.
        
        Returns:
            bool: True if registration successful
            
        Raises:
            DeviceRegistrationError: If registration fails
        """
        try:
            main_controller = self.get_main_controller_info()
            device_id = self.get_device_id()
            device_type = self.get_device_type()
            api_port = self.get_api_port()
            
            # Get our IP address (assume we're on the same network as main controller)
            # In a real implementation, you might want to detect this automatically
            ip_address = "192.168.4.100"  # This would be dynamically determined
            
            registration_data = {
                'device_type': device_type,
                'ip_address': ip_address,
                'port': api_port
            }
            
            # Make registration request
            response = make_device_request(
                main_controller['ip'],
                main_controller['port'],
                'PUT',
                f"{DEVICE_REGISTRATION_PATH}/{device_id}",
                registration_data,
                timeout=10
            )
            
            if response.status_code == HTTP_OK:
                log_device_event(
                    self.logger, 'registration_success', device_id, device_type,
                    main_controller_ip=main_controller['ip'],
                    main_controller_port=main_controller['port']
                )
                return True
            else:
                error_msg = f"Registration failed with status {response.status_code}"
                if response.content:
                    try:
                        error_data = response.json()
                        error_msg += f": {error_data.get('error', 'Unknown error')}"
                    except:
                        error_msg += f": {response.text}"
                
                raise DeviceRegistrationError(error_msg)
        
        except DeviceCommunicationError as e:
            raise DeviceRegistrationError(f"Failed to communicate with main controller: {e}")
        except Exception as e:
            raise DeviceRegistrationError(f"Unexpected error during registration: {e}")
    
    @abstractmethod
    def create_flask_app(self):
        """
        Create and configure the Flask application for this device.
        
        Returns:
            Flask: Configured Flask application
        """
        pass
    
    def start_heartbeat(self):
        """Start the heartbeat service."""
        if self.heartbeat_service:
            self.heartbeat_service.start()
    
    def stop_heartbeat(self):
        """Stop the heartbeat service."""
        if self.heartbeat_service:
            self.heartbeat_service.stop()
    
    def run(self):
        """
        Run the device controller.
        Main entry point that starts the Flask app and heartbeat service.
        """
        try:
            # Create Flask app
            self.app = self.create_flask_app()
            
            # Register with main controller
            log_system_event(self.logger, 'registration_attempt', 'Attempting to register with main controller')
            
            def register_with_retry():
                return self.register_with_main_controller()
            
            # Retry registration with exponential backoff
            retry_operation(register_with_retry, max_retries=5, delay=2.0, backoff=2.0)
            
            # Start heartbeat service
            self.start_heartbeat()
            
            # Get server configuration
            host = "0.0.0.0"
            port = self.get_api_port()
            debug = self.config.get('debug', False)
            
            log_system_event(
                self.logger, 'server_start',
                f"Starting device server on {host}:{port}",
                device_id=self.get_device_id(),
                device_type=self.get_device_type()
            )
            
            # Run Flask app
            self.app.run(
                host=host,
                port=port,
                debug=debug,
                threaded=True
            )
            
        except KeyboardInterrupt:
            log_system_event(self.logger, 'shutdown', 'Device controller stopped by user')
        except Exception as e:
            self.logger.error(f"Error running device controller: {e}")
            raise
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Shutdown the device controller gracefully."""
        try:
            log_system_event(self.logger, 'shutdown_start', 'Device controller shutting down')
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Stop heartbeat service
            self.stop_heartbeat()
            
            log_system_event(self.logger, 'shutdown_complete', 'Device controller shutdown completed')
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    def is_shutting_down(self):
        """
        Check if the controller is shutting down.
        
        Returns:
            bool: True if shutting down
        """
        return self._shutdown_event.is_set()
    
    def get_status(self):
        """
        Get the current status of the device controller.
        
        Returns:
            Dict[str, Any]: Status information
        """
        heartbeat_status = None
        if self.heartbeat_service:
            heartbeat_status = self.heartbeat_service.get_status()
        
        return {
            'device_id': self.get_device_id(),
            'device_type': self.get_device_type(),
            'api_port': self.get_api_port(),
            'status': 'running' if not self.is_shutting_down() else 'shutting_down',
            'heartbeat_service': heartbeat_status,
            'timestamp': datetime.now().isoformat()
        }