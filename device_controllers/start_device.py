"""
Device startup script that determines device type from configuration and starts the appropriate controller.
This script reads the device configuration to determine which device type to run.
"""

import os
import sys
import argparse
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from shared.utils import load_json_config
from shared.exceptions import ConfigurationError
from shared.constants import DEVICE_TYPE_REAR_CAMERA


def get_device_config_path(device_type=None, config_path=None):
    """
    Get the configuration file path for a device.
    
    Args:
        device_type (str, optional): Device type to get config for
        config_path (str, optional): Explicit config file path
        
    Returns:
        str: Path to configuration file
    """
    if config_path:
        return config_path
    
    if device_type:
        return os.path.join(project_root, 'config', 'device_configs', f'{device_type}_config.json')
    
    # Try to detect from environment
    if 'DEVICE_CONFIG' in os.environ:
        return os.environ['DEVICE_CONFIG']
    
    # Default to rear camera config
    return os.path.join(project_root, 'config', 'device_configs', 'rear_camera_config.json')


def determine_device_type(config_path):
    """
    Determine device type from configuration file.
    
    Args:
        config_path (str): Path to configuration file
        
    Returns:
        str: Device type identifier
        
    Raises:
        ConfigurationError: If device type cannot be determined
    """
    try:
        config = load_json_config(config_path)
        device_type = config.get('device_type')
        
        if not device_type:
            raise ConfigurationError("Device type not specified in configuration")
        
        return device_type
    
    except Exception as e:
        raise ConfigurationError(f"Failed to determine device type from {config_path}: {e}")


def start_device_controller(device_type, config_path):
    """
    Start the appropriate device controller based on device type.
    
    Args:
        device_type (str): Device type identifier
        config_path (str): Path to configuration file
    """
    print(f"Starting device controller for type: {device_type}")
    print(f"Using configuration: {config_path}")
    
    try:
        if device_type == DEVICE_TYPE_REAR_CAMERA:
            from device_controllers.rear_camera.app import RearCameraController
            controller = RearCameraController(config_path)
            controller.run()
        
        else:
            raise ConfigurationError(f"Unsupported device type: {device_type}")
    
    except KeyboardInterrupt:
        print(f"\n{device_type} controller stopped by user")
    except Exception as e:
        print(f"Error starting {device_type} controller: {e}")
        sys.exit(1)


def main():
    """
    Main entry point for device startup.
    """
    parser = argparse.ArgumentParser(
        description='Start a device controller based on configuration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start device using default config detection
  python start_device.py
  
  # Start specific device type
  python start_device.py --device-type rear-camera
  
  # Use specific config file
  python start_device.py --config /path/to/device_config.json
  
  # Start with environment variable
  DEVICE_CONFIG=/path/to/config.json python start_device.py
        """
    )
    
    parser.add_argument(
        '--device-type', '-t',
        help='Device type to start (rear-camera, etc.)',
        choices=[DEVICE_TYPE_REAR_CAMERA]
    )
    
    parser.add_argument(
        '--config', '-c',
        help='Path to device configuration file'
    )
    
    parser.add_argument(
        '--list-types', '-l',
        action='store_true',
        help='List available device types'
    )
    
    parser.add_argument(
        '--validate-config', '-v',
        action='store_true',
        help='Validate configuration file and exit'
    )
    
    args = parser.parse_args()
    
    # Handle list types
    if args.list_types:
        print("Available device types:")
        print(f"  - {DEVICE_TYPE_REAR_CAMERA}: Rear camera controller")
        return
    
    try:
        # Get configuration path
        config_path = get_device_config_path(args.device_type, args.config)
        
        if not os.path.exists(config_path):
            print(f"Error: Configuration file not found: {config_path}")
            print("\nAvailable configurations:")
            config_dir = os.path.join(project_root, 'config', 'device_configs')
            if os.path.exists(config_dir):
                for file in os.listdir(config_dir):
                    if file.endswith('_config.json'):
                        print(f"  - {os.path.join(config_dir, file)}")
            sys.exit(1)
        
        # Determine device type
        device_type = determine_device_type(config_path)
        
        # Validate configuration if requested
        if args.validate_config:
            print(f"Configuration file: {config_path}")
            print(f"Device type: {device_type}")
            print("Configuration is valid!")
            return
        
        # Start the device controller
        start_device_controller(device_type, config_path)
    
    except ConfigurationError as e:
        print(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()