#!/usr/bin/env python3
"""
Main Controller Flask API
A simple Flask API for Raspberry Pi device control
"""

from flask import Flask, request, jsonify
import logging
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Configure logging for Raspberry Pi debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('main-controller.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Basic configuration
app.config['DEBUG'] = False
app.config['HOST'] = '0.0.0.0'  # Allow external connections for Pi
app.config['PORT'] = 8080  # Changed from 5000 to avoid conflicts with AirTunes

@app.route('/api/v1/device/<device_id>', methods=['PUT'])
def update_device(device_id):
    """
    Update device information
    
    Args:
        device_id (str): The device identifier
        
    Returns:
        JSON response with status
    """
    try:
        # Basic input validation
        if not device_id or not device_id.strip():
            logger.warning(f"Invalid device ID received: '{device_id}'")
            return jsonify({"error": "Invalid device ID"}), 400
        
        # Log the request for debugging
        logger.info(f"PUT request received for device ID: {device_id}")
        
        # Get request data (for future use)
        request_data = request.get_json() if request.is_json else {}
        logger.info(f"Request data: {request_data}")
        
        # TODO: Implement actual device update logic here
        # For now, just return success response
        
        logger.info(f"Device {device_id} updated successfully")
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        logger.error(f"Error updating device {device_id}: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "main-controller"
    }), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({"error": "Method not allowed"}), 405

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    logger.info("Starting Main Controller Flask API")
    logger.info(f"Running on {app.config['HOST']}:{app.config['PORT']}")
    
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )