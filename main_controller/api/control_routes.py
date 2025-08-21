"""
Device control API routes for the main controller.
Handles sending commands to registered devices.
"""

import time
from flask import Blueprint, request, jsonify
from datetime import datetime

from shared.constants import *
from shared.exceptions import *
from shared.utils import make_device_request
from shared.logging_config import log_api_request


def create_control_routes(device_registry, logger):
    """
    Create device control API routes blueprint.
    
    Args:
        device_registry: DeviceRegistry instance
        logger: Logger instance
        
    Returns:
        Blueprint: Flask blueprint with control routes
    """
    control_bp = Blueprint('control_api', __name__)
    
    @control_bp.route(f'{MAIN_CONTROLLER_BASE_PATH}/control/<device_id>/<command>', methods=['POST'])
    def control_device(device_id, command):
        """
        Send a control command to a specific device.
        
        POST /api/v1/main-controller/control/{device_id}/{command}
        
        Request body (optional):
        {
            "parameters": {...}
        }
        """
        start_time = time.time()
        
        try:
            # Get device information
            device = device_registry.get_device(device_id)
            
            if not device:
                response = jsonify({
                    'error': f'Device not found: {device_id}',
                    'status': 'error'
                })
                response.status_code = 404
                
                log_api_request(
                    logger, request.method, request.path,
                    request.remote_addr, 404,
                    (time.time() - start_time) * 1000
                )
                
                return response
            
            # Check if device is active
            if device['status'] != DEVICE_STATUS_ACTIVE:
                response = jsonify({
                    'error': f'Device {device_id} is not active',
                    'status': 'error',
                    'device_status': device['status']
                })
                response.status_code = HTTP_BAD_REQUEST
                
                log_api_request(
                    logger, request.method, request.path,
                    request.remote_addr, HTTP_BAD_REQUEST,
                    (time.time() - start_time) * 1000
                )
                
                return response
            
            # Get request parameters if provided
            parameters = {}
            if request.is_json:
                data = request.get_json()
                parameters = data.get('parameters', {})
            
            # Build device command path based on device type and command
            device_type = device['device_type']
            command_path = _build_command_path(device_type, command)
            
            if not command_path:
                response = jsonify({
                    'error': f'Invalid command "{command}" for device type "{device_type}"',
                    'status': 'error'
                })
                response.status_code = HTTP_BAD_REQUEST
                
                log_api_request(
                    logger, request.method, request.path,
                    request.remote_addr, HTTP_BAD_REQUEST,
                    (time.time() - start_time) * 1000
                )
                
                return response
            
            # Send command to device
            try:
                device_response = make_device_request(
                    device['ip_address'],
                    device['port'],
                    'POST',
                    command_path,
                    parameters if parameters else None,
                    timeout=10
                )
                
                # Check if device responded successfully
                if device_response.status_code == 200:
                    response = jsonify({
                        'message': f'Command "{command}" sent successfully to device {device_id}',
                        'device_id': device_id,
                        'command': command,
                        'device_response': device_response.json() if device_response.content else None,
                        'status': 'success',
                        'timestamp': datetime.now().isoformat()
                    })
                    response.status_code = HTTP_OK
                    
                    log_api_request(
                        logger, request.method, request.path,
                        request.remote_addr, HTTP_OK,
                        (time.time() - start_time) * 1000
                    )
                    
                    return response
                else:
                    # Device returned an error
                    device_registry.increment_failure_count(device_id)
                    
                    response = jsonify({
                        'error': f'Device {device_id} returned error: {device_response.status_code}',
                        'device_id': device_id,
                        'command': command,
                        'device_status_code': device_response.status_code,
                        'device_response': device_response.text if device_response.content else None,
                        'status': 'error'
                    })
                    response.status_code = HTTP_BAD_REQUEST
                    
                    log_api_request(
                        logger, request.method, request.path,
                        request.remote_addr, HTTP_BAD_REQUEST,
                        (time.time() - start_time) * 1000
                    )
                    
                    return response
            
            except DeviceCommunicationError as e:
                # Device communication failed
                failure_count = device_registry.increment_failure_count(device_id)
                
                response = jsonify({
                    'error': f'Failed to communicate with device {device_id}: {str(e)}',
                    'device_id': device_id,
                    'command': command,
                    'failure_count': failure_count,
                    'status': 'error'
                })
                response.status_code = 503  # Service Unavailable
                
                log_api_request(
                    logger, request.method, request.path,
                    request.remote_addr, 503,
                    (time.time() - start_time) * 1000
                )
                
                return response
        
        except Exception as e:
            logger.error(f"Unexpected error in device control: {e}")
            
            response = jsonify({
                'error': 'Internal server error',
                'status': 'error'
            })
            response.status_code = HTTP_INTERNAL_SERVER_ERROR
            
            log_api_request(
                logger, request.method, request.path,
                request.remote_addr, HTTP_INTERNAL_SERVER_ERROR,
                (time.time() - start_time) * 1000
            )
            
            return response
    
    @control_bp.route(f'{MAIN_CONTROLLER_BASE_PATH}/cleanup', methods=['POST'])
    def force_cleanup():
        """
        Force an immediate cleanup of inactive devices.
        
        POST /api/v1/main-controller/cleanup
        """
        start_time = time.time()
        
        try:
            # This would need to be injected or accessed differently in a real implementation
            # For now, we'll just call the registry cleanup directly
            removed_devices = device_registry.cleanup_inactive_devices()
            
            response = jsonify({
                'message': 'Cleanup completed successfully',
                'removed_devices': removed_devices,
                'removed_count': len(removed_devices),
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            })
            response.status_code = HTTP_OK
            
            log_api_request(
                logger, request.method, request.path,
                request.remote_addr, HTTP_OK,
                (time.time() - start_time) * 1000
            )
            
            return response
        
        except Exception as e:
            logger.error(f"Error during forced cleanup: {e}")
            
            response = jsonify({
                'error': 'Internal server error',
                'status': 'error'
            })
            response.status_code = HTTP_INTERNAL_SERVER_ERROR
            
            log_api_request(
                logger, request.method, request.path,
                request.remote_addr, HTTP_INTERNAL_SERVER_ERROR,
                (time.time() - start_time) * 1000
            )
            
            return response
    
    return control_bp


def _build_command_path(device_type, command):
    """
    Build the API path for a device command based on device type.
    
    Args:
        device_type (str): Type of device
        command (str): Command to execute
        
    Returns:
        str: API path for the command, or None if invalid
    """
    # Define command mappings for each device type
    command_mappings = {
        DEVICE_TYPE_REAR_CAMERA: {
            'up': f'/api/{API_VERSION}/rear-camera/up',
            'down': f'/api/{API_VERSION}/rear-camera/down',
            'status': f'/api/{API_VERSION}/rear-camera/status'
        }
        # Add more device types and their commands here as needed
    }
    
    device_commands = command_mappings.get(device_type)
    if not device_commands:
        return None
    
    return device_commands.get(command)