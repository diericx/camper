"""
Main Flask application for the distributed device control system.
Raspberry Pi main controller that manages ESP8266 devices.
"""

import os
import sys
from flask import Flask, jsonify
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.constants import *
from shared.logging_config import setup_logging, log_system_event
from shared.utils import load_json_config
from main_controller.device_registry import DeviceRegistry
from main_controller.cleanup_service import CleanupService
from main_controller.api.device_routes import create_device_routes
from main_controller.api.control_routes import create_control_routes


def create_app(config_path=None):
    """
    Create and configure the Flask application.
    
    Args:
        config_path (str, optional): Path to configuration file
        
    Returns:
        Flask: Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_path is None:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'main_config.json')
    
    try:
        config = load_json_config(config_path)
    except Exception as e:
        # Use default configuration if file not found
        config = {
            "server": {
                "host": "0.0.0.0",
                "port": DEFAULT_MAIN_CONTROLLER_PORT,
                "debug": False
            },
            "registry": {
                "cleanup_on_startup": True
            },
            "cleanup": {
                "inactive_threshold_minutes": DEVICE_INACTIVE_THRESHOLD // 60,
                "removal_threshold_minutes": DEVICE_REMOVAL_THRESHOLD // 60,
                "cleanup_interval_seconds": CLEANUP_INTERVAL
            },
            "logging": {
                "level": "INFO",
                "log_dir": "logs"
            }
        }
        print(f"Warning: Could not load config file {config_path}, using defaults: {e}")
    
    # Set up logging
    logger = setup_logging(
        'main_controller',
        config.get('logging', {}).get('level', 'INFO'),
        config.get('logging', {}).get('log_dir', 'logs')
    )
    
    # Store logger and config in app context
    app.logger = logger
    app.config.update(config)
    
    log_system_event(logger, 'startup', 'Main controller starting up', config=config)
    
    # Initialize device registry
    device_registry = DeviceRegistry(logger)
    app.device_registry = device_registry
    
    # Initialize cleanup service
    cleanup_service = CleanupService(
        device_registry,
        logger,
        config.get('cleanup', {}).get('cleanup_interval_seconds', CLEANUP_INTERVAL)
    )
    app.cleanup_service = cleanup_service
    
    # Register API blueprints
    device_routes = create_device_routes(device_registry, logger)
    control_routes = create_control_routes(device_registry, logger)
    
    app.register_blueprint(device_routes)
    app.register_blueprint(control_routes)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        try:
            stats = device_registry.get_registry_stats()
            cleanup_status = cleanup_service.get_status()
            
            return jsonify({
                'status': 'healthy',
                'service': 'main_controller',
                'timestamp': datetime.now().isoformat(),
                'registry_stats': stats,
                'cleanup_service': cleanup_status,
                'version': '1.0.0'
            })
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint with system information."""
        return jsonify({
            'service': 'Camper Device Control System - Main Controller',
            'version': '1.0.0',
            'status': 'running',
            'timestamp': datetime.now().isoformat(),
            'endpoints': {
                'health': '/health',
                'device_registration': f'{DEVICE_REGISTRATION_PATH}/<device_id>',
                'devices': f'{MAIN_CONTROLLER_BASE_PATH}/devices',
                'stats': f'{MAIN_CONTROLLER_BASE_PATH}/stats',
                'control': f'{MAIN_CONTROLLER_BASE_PATH}/control/<device_id>/<command>',
                'cleanup': f'{MAIN_CONTROLLER_BASE_PATH}/cleanup'
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
        logger.error(f"Internal server error: {error}")
        return jsonify({
            'error': 'Internal server error',
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500
    
    # Startup tasks
    @app.before_first_request
    def startup_tasks():
        """Tasks to run before the first request."""
        try:
            # Start cleanup service
            cleanup_service.start()
            log_system_event(logger, 'startup_complete', 'Main controller startup completed')
            
        except Exception as e:
            logger.error(f"Error during startup tasks: {e}")
            raise
    
    # Shutdown tasks
    def shutdown_tasks():
        """Tasks to run during shutdown."""
        try:
            log_system_event(logger, 'shutdown', 'Main controller shutting down')
            
            # Stop cleanup service
            if hasattr(app, 'cleanup_service'):
                app.cleanup_service.stop()
            
            log_system_event(logger, 'shutdown_complete', 'Main controller shutdown completed')
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    # Register shutdown handler
    import atexit
    atexit.register(shutdown_tasks)
    
    return app


def main():
    """
    Main entry point for the application.
    """
    # Get configuration file path from environment or use default
    config_path = os.environ.get('MAIN_CONTROLLER_CONFIG')
    
    # Create Flask app
    app = create_app(config_path)
    
    # Get server configuration
    server_config = app.config.get('server', {})
    host = server_config.get('host', '0.0.0.0')
    port = server_config.get('port', DEFAULT_MAIN_CONTROLLER_PORT)
    debug = server_config.get('debug', False)
    
    try:
        app.logger.info(f"Starting main controller on {host}:{port}")
        
        # Run the Flask application
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True  # Enable threading for concurrent requests
        )
        
    except KeyboardInterrupt:
        app.logger.info("Main controller stopped by user")
    except Exception as e:
        app.logger.error(f"Error starting main controller: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()