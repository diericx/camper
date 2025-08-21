"""
Device registration and management API routes for the main controller.
"""

import time
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime

from shared.constants import *
from shared.exceptions import *
from shared.logging_config import log_api_request


def create_device_routes(device_registry, logger):
    """
    Create device API routes blueprint.
    
    Args:
        device_registry: DeviceRegistry instance
        logger: Logger instance
        
    Returns:
        Blueprint: Flask blueprint with device routes
    """
    device_bp = Blueprint('device_api', __name__)
    
    @device_bp.route(f'{DEVICE_REGISTRATION_PATH}/<device_id>', methods=['PUT'])
    def register_device(device_id):
        """
        Register or update a device in the registry.
        
        PUT /api/v1/main-controller/device/{device_id}
        
        Request body:
        {
            "device_type": "rear-camera",
            "ip_address": "192.168.4.100",
            "port": 5001
        }
        """
        start_time = time.time()
        
        try:
            # Validate request content type
            if not request.is_json:
                response = jsonify({
                    'error': 'Content-Type must be application/json',
                    'status': 'error'
                })
                response.status_code = HTTP_BAD_REQUEST
                
                log_api_request(
                    logger, request.method, request.path, 
                    request.remote_addr, HTTP_BAD_REQUEST,
                    (time.time() - start_time) * 1000
                )
                
                return response
            
            # Get request data
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['device_type', 'ip_address', 'port']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                response = jsonify({
                    'error': f'Missing required fields: {", ".join(missing_fields)}',
                    'status': 'error'
                })
                response.status_code = HTTP_BAD_REQUEST
                
                log_api_request(
                    logger, request.method, request.path,
                    request.remote_addr, HTTP_BAD_REQUEST,
                    (time.time() - start_time) * 1000
                )
                
                return response
            
            # Extract device information
            device_type = data['device_type']
            ip_address = data['ip_address']
            port = data['port']
            
            # Register the device
            success = device_registry.register_device(device_id, device_type, ip_address, port)
            
            if success:
                response = jsonify({
                    'message': 'Device registered successfully',
                    'device_id': device_id,
                    'device_type': device_type,
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
                response = jsonify({
                    'error': 'Device registration failed',
                    'status': 'error'
                })
                response.status_code = HTTP_INTERNAL_SERVER_ERROR
                
                log_api_request(
                    logger, request.method, request.path,
                    request.remote_addr, HTTP_INTERNAL_SERVER_ERROR,
                    (time.time() - start_time) * 1000
                )
                
                return response
        
        except DeviceTypeLimitExceededError as e:
            response = jsonify({
                'error': str(e),
                'status': 'error',
                'error_type': 'device_type_limit_exceeded'
            })
            response.status_code = HTTP_CONFLICT
            
            log_api_request(
                logger, request.method, request.path,
                request.remote_addr, HTTP_CONFLICT,
                (time.time() - start_time) * 1000
            )
            
            return response
        
        except (InvalidDeviceTypeError, DeviceRegistrationError) as e:
            response = jsonify({
                'error': str(e),
                'status': 'error',
                'error_type': 'validation_error'
            })
            response.status_code = HTTP_BAD_REQUEST
            
            log_api_request(
                logger, request.method, request.path,
                request.remote_addr, HTTP_BAD_REQUEST,
                (time.time() - start_time) * 1000
            )
            
            return response
        
        except Exception as e:
            logger.error(f"Unexpected error in device registration: {e}")
            
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
    
    @device_bp.route(f'{MAIN_CONTROLLER_BASE_PATH}/devices', methods=['GET'])
    def get_devices():
        """
        Get all registered devices.
        
        GET /api/v1/main-controller/devices
        
        Query parameters:
        - active_only: true/false (default: false)
        - device_type: filter by device type
        """
        start_time = time.time()
        
        try:
            # Get query parameters
            active_only = request.args.get('active_only', 'false').lower() == 'true'
            device_type_filter = request.args.get('device_type')
            
            # Get devices based on filters
            if active_only:
                devices = device_registry.get_active_devices()
            else:
                devices = device_registry.get_all_devices()
            
            # Filter by device type if specified
            if device_type_filter:
                devices = {
                    device_id: device for device_id, device in devices.items()
                    if device['device_type'] == device_type_filter
                }
            
            # Convert datetime objects to ISO strings for JSON serialization
            for device in devices.values():
                device['created_at'] = device['created_at'].isoformat()
                device['last_seen'] = device['last_seen'].isoformat()
            
            response = jsonify({
                'devices': devices,
                'count': len(devices),
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
            logger.error(f"Error getting devices: {e}")
            
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
    
    @device_bp.route(f'{DEVICE_REGISTRATION_PATH}/<device_id>', methods=['GET'])
    def get_device(device_id):
        """
        Get information about a specific device.
        
        GET /api/v1/main-controller/device/{device_id}
        """
        start_time = time.time()
        
        try:
            device = device_registry.get_device(device_id)
            
            if device:
                # Convert datetime objects to ISO strings
                device['created_at'] = device['created_at'].isoformat()
                device['last_seen'] = device['last_seen'].isoformat()
                
                response = jsonify({
                    'device': device,
                    'device_id': device_id,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                })
                response.status_code = HTTP_OK
            else:
                response = jsonify({
                    'error': f'Device not found: {device_id}',
                    'status': 'error'
                })
                response.status_code = 404
            
            log_api_request(
                logger, request.method, request.path,
                request.remote_addr, response.status_code,
                (time.time() - start_time) * 1000
            )
            
            return response
        
        except Exception as e:
            logger.error(f"Error getting device {device_id}: {e}")
            
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
    
    @device_bp.route(f'{DEVICE_REGISTRATION_PATH}/<device_id>', methods=['DELETE'])
    def remove_device(device_id):
        """
        Remove a device from the registry.
        
        DELETE /api/v1/main-controller/device/{device_id}
        """
        start_time = time.time()
        
        try:
            success = device_registry.remove_device(device_id)
            
            if success:
                response = jsonify({
                    'message': f'Device {device_id} removed successfully',
                    'device_id': device_id,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                })
                response.status_code = HTTP_OK
            else:
                response = jsonify({
                    'error': f'Device not found: {device_id}',
                    'status': 'error'
                })
                response.status_code = 404
            
            log_api_request(
                logger, request.method, request.path,
                request.remote_addr, response.status_code,
                (time.time() - start_time) * 1000
            )
            
            return response
        
        except Exception as e:
            logger.error(f"Error removing device {device_id}: {e}")
            
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
    
    @device_bp.route(f'{MAIN_CONTROLLER_BASE_PATH}/stats', methods=['GET'])
    def get_registry_stats():
        """
        Get registry statistics.
        
        GET /api/v1/main-controller/stats
        """
        start_time = time.time()
        
        try:
            stats = device_registry.get_registry_stats()
            
            response = jsonify({
                'stats': stats,
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
            logger.error(f"Error getting registry stats: {e}")
            
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
    
    return device_bp