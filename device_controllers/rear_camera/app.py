"""
Flask application for the rear camera controller.
Implements the rear camera API endpoints for up/down movement control.
"""

import os
import sys
import time
from flask import Flask, request, jsonify
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from shared.constants import *
from shared.logging_config import log_api_request
from device_controllers.base_controller import BaseDeviceController
from device_controllers.rear_camera.camera_control import CameraController, CameraMovementError


class RearCameraController(BaseDeviceController):
    """
    Rear camera device controller implementing camera movement APIs.
    """
    
    def __init__(self, config_path=None):
        """
        Initialize the rear camera controller.
        
        Args:
            config_path (str, optional): Path to configuration file
        """
        super().__init__(config_path)
        
        # Initialize camera controller
        camera_config = self.config.get('device_specific', {}).get('camera', {})
        self.camera_controller = CameraController(self.logger, camera_config)
    
    def get_device_type(self):
        """Get the device type identifier."""
        return DEVICE_TYPE_REAR_CAMERA
    
    def create_flask_app(self):
        """
        Create and configure the Flask application for the rear camera.
        
        Returns:
            Flask: Configured Flask application
        """
        app = Flask(__name__)
        
        # Store references for use in routes
        app.camera_controller = self.camera_controller
        app.device_controller = self
        app.logger = self.logger
        
        # API endpoints
        @app.route(f'/api/{API_VERSION}/rear-camera/up', methods=['POST'])
        def move_camera_up():
            """
            Move the rear camera to the up position.
            
            POST /api/v1/rear-camera/up
            """
            start_time = time.time()
            
            try:
                result = app.camera_controller.move_up()
                
                response = jsonify({
                    'message': 'Camera moved up successfully',
                    'movement_result': result,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                })
                response.status_code = HTTP_OK
                
                log_api_request(
                    app.logger, request.method, request.path,
                    request.remote_addr, HTTP_OK,
                    (time.time() - start_time) * 1000
                )
                
                return response
            
            except CameraMovementError as e:
                response = jsonify({
                    'error': str(e),
                    'status': 'error',
                    'error_type': 'camera_movement_error'
                })
                response.status_code = HTTP_BAD_REQUEST
                
                log_api_request(
                    app.logger, request.method, request.path,
                    request.remote_addr, HTTP_BAD_REQUEST,
                    (time.time() - start_time) * 1000
                )
                
                return response
            
            except Exception as e:
                app.logger.error(f"Unexpected error in move_camera_up: {e}")
                
                response = jsonify({
                    'error': 'Internal server error',
                    'status': 'error'
                })
                response.status_code = HTTP_INTERNAL_SERVER_ERROR
                
                log_api_request(
                    app.logger, request.method, request.path,
                    request.remote_addr, HTTP_INTERNAL_SERVER_ERROR,
                    (time.time() - start_time) * 1000
                )
                
                return response
        
        @app.route(f'/api/{API_VERSION}/rear-camera/down', methods=['POST'])
        def move_camera_down():
            """
            Move the rear camera to the down position.
            
            POST /api/v1/rear-camera/down
            """
            start_time = time.time()
            
            try:
                result = app.camera_controller.move_down()
                
                response = jsonify({
                    'message': 'Camera moved down successfully',
                    'movement_result': result,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                })
                response.status_code = HTTP_OK
                
                log_api_request(
                    app.logger, request.method, request.path,
                    request.remote_addr, HTTP_OK,
                    (time.time() - start_time) * 1000
                )
                
                return response
            
            except CameraMovementError as e:
                response = jsonify({
                    'error': str(e),
                    'status': 'error',
                    'error_type': 'camera_movement_error'
                })
                response.status_code = HTTP_BAD_REQUEST
                
                log_api_request(
                    app.logger, request.method, request.path,
                    request.remote_addr, HTTP_BAD_REQUEST,
                    (time.time() - start_time) * 1000
                )
                
                return response
            
            except Exception as e:
                app.logger.error(f"Unexpected error in move_camera_down: {e}")
                
                response = jsonify({
                    'error': 'Internal server error',
                    'status': 'error'
                })
                response.status_code = HTTP_INTERNAL_SERVER_ERROR
                
                log_api_request(
                    app.logger, request.method, request.path,
                    request.remote_addr, HTTP_INTERNAL_SERVER_ERROR,
                    (time.time() - start_time) * 1000
                )
                
                return response
        
        @app.route(f'/api/{API_VERSION}/rear-camera/status', methods=['GET'])
        def get_camera_status():
            """
            Get the current camera status.
            
            GET /api/v1/rear-camera/status
            """
            start_time = time.time()
            
            try:
                camera_status = app.camera_controller.get_status()
                device_status = app.device_controller.get_status()
                
                response = jsonify({
                    'camera_status': camera_status,
                    'device_status': device_status,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                })
                response.status_code = HTTP_OK
                
                log_api_request(
                    app.logger, request.method, request.path,
                    request.remote_addr, HTTP_OK,
                    (time.time() - start_time) * 1000
                )
                
                return response
            
            except Exception as e:
                app.logger.error(f"Error getting camera status: {e}")
                
                response = jsonify({
                    'error': 'Internal server error',
                    'status': 'error'
                })
                response.status_code = HTTP_INTERNAL_SERVER_ERROR
                
                log_api_request(
                    app.logger, request.method, request.path,
                    request.remote_addr, HTTP_INTERNAL_SERVER_ERROR,
                    (time.time() - start_time) * 1000
                )
                
                return response
        
        @app.route(f'/api/{API_VERSION}/rear-camera/reset', methods=['POST'])
        def reset_camera_position():
            """
            Reset the camera to the middle position.
            
            POST /api/v1/rear-camera/reset
            """
            start_time = time.time()
            
            try:
                result = app.camera_controller.reset_position()
                
                response = jsonify({
                    'message': 'Camera position reset successfully',
                    'reset_result': result,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                })
                response.status_code = HTTP_OK
                
                log_api_request(
                    app.logger, request.method, request.path,
                    request.remote_addr, HTTP_OK,
                    (time.time() - start_time) * 1000
                )
                
                return response
            
            except CameraMovementError as e:
                response = jsonify({
                    'error': str(e),
                    'status': 'error',
                    'error_type': 'camera_movement_error'
                })
                response.status_code = HTTP_BAD_REQUEST
                
                log_api_request(
                    app.logger, request.method, request.path,
                    request.remote_addr, HTTP_BAD_REQUEST,
                    (time.time() - start_time) * 1000
                )
                
                return response
            
            except Exception as e:
                app.logger.error(f"Unexpected error in reset_camera_position: {e}")
                
                response = jsonify({
                    'error': 'Internal server error',
                    'status': 'error'
                })
                response.status_code = HTTP_INTERNAL_SERVER_ERROR
                
                log_api_request(
                    app.logger, request.method, request.path,
                    request.remote_addr, HTTP_INTERNAL_SERVER_ERROR,
                    (time.time() - start_time) * 1000
                )
                
                return response
        
        # Health check endpoint
        @app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint for the rear camera device."""
            try:
                camera_status = app.camera_controller.get_status()
                device_status = app.device_controller.get_status()
                
                return jsonify({
                    'status': 'healthy',
                    'service': 'rear_camera_controller',
                    'device_id': app.device_controller.get_device_id(),
                    'camera_status': camera_status,
                    'device_status': device_status,
                    'timestamp': datetime.now().isoformat(),
                    'version': '1.0.0'
                })
            except Exception as e:
                app.logger.error(f"Health check failed: {e}")
                return jsonify({
                    'status': 'unhealthy',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }), 500
        
        # Root endpoint
        @app.route('/', methods=['GET'])
        def root():
            """Root endpoint with device information."""
            return jsonify({
                'service': 'Camper Device Control System - Rear Camera Controller',
                'device_id': app.device_controller.get_device_id(),
                'device_type': app.device_controller.get_device_type(),
                'version': '1.0.0',
                'status': 'running',
                'timestamp': datetime.now().isoformat(),
                'endpoints': {
                    'health': '/health',
                    'move_up': f'/api/{API_VERSION}/rear-camera/up',
                    'move_down': f'/api/{API_VERSION}/rear-camera/down',
                    'status': f'/api/{API_VERSION}/rear-camera/status',
                    'reset': f'/api/{API_VERSION}/rear-camera/reset'
                }
            })
        
        # Error handlers
        @app.errorhandler(404)
        def not_found(error):
            return jsonify({
                'error': 'Endpoint not found',
                'status': 'error',
                'timestamp': datetime.now().isoformat()
            }), 404
        
        @app.errorhandler(405)
        def method_not_allowed(error):
            return jsonify({
                'error': 'Method not allowed',
                'status': 'error',
                'timestamp': datetime.now().isoformat()
            }), 405
        
        @app.errorhandler(500)
        def internal_error(error):
            app.logger.error(f"Internal server error: {error}")
            return jsonify({
                'error': 'Internal server error',
                'status': 'error',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        return app


def main():
    """
    Main entry point for the rear camera controller.
    """
    # Get configuration file path from environment or use default
    config_path = os.environ.get('REAR_CAMERA_CONFIG')
    
    try:
        # Create and run the rear camera controller
        controller = RearCameraController(config_path)
        controller.run()
        
    except KeyboardInterrupt:
        print("Rear camera controller stopped by user")
    except Exception as e:
        print(f"Error starting rear camera controller: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()