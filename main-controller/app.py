#!/usr/bin/env python3
"""
Main Controller Flask API
A simple Flask API for Raspberry Pi device control
"""

from enum import Enum
from flask import Flask, json, request, jsonify
import logging
import os
from datetime import datetime 
import time
import config

app, logger = config.setupFlaskApp()

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


@app.route('/api/v1/device/<device_id>', methods=['PUT'])
def update_device(device_id):
    """
    If this device doesn't exist, register it with information from the client.
    If it does exist, update any info.
    
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

        if not request_data["device_type"]:
            logger.warning(f"Missing device type")
            return jsonify({"error": "Invalid device type"}), 400

        device_type = None
        try:
            device_type = DeviceType[str(request_data["device_type"])]
        except KeyError:
            logger.warning(f"Invalid Device Type")
            return jsonify({"error": "Invalid device type"}), 400
    
        device = devices.get(device_id)
        if device is None:
            devices[device_id] = Device(device_type, request.remote_addr)
            device = devices[device_id]
        else:
            # If the device is already registered and we get a put from a diff
            # IP, error out
            if device.addr != request.remote_addr:
                logger.warning(f"Device already registered, cannot register again")
                return jsonify({"error": "Device already registered"}), 400

            device.last_seen = time.time()

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