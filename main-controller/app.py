#!/usr/bin/env python3
"""
Main Controller Flask API
A simple Flask API for Raspberry Pi device control
"""

from enum import Enum
from flask import Flask, json, request, jsonify
import logging
import os
from datetime import datetime , timedelta
import threading
import time

import requests
import config

from gpiozero import Button

from devices import start_stale_device_cleanup_thread, DeviceType, devices, Device

app, logger = config.setupFlaskApp()

start_stale_device_cleanup_thread(logger)

@app.route('/api/v1/device/<device_id>/<action>', methods=['POST'])
def perform_device_action(device_id, action):
    try:
        # Basic input validation
        if not device_id or not device_id.strip():
            logger.warning(f"Invalid device ID received: '{device_id}'")
            return jsonify({"error": "Invalid device ID"}), 400
        if not action or not action.strip():
            logger.warning(f"Invalid action received: '{action}'")
            return jsonify({"error": "Invalid action"}), 400

        device = devices.get(device_id)
        if device is None:
            logger.warning(f"Device does not exist: '{device}'")
            return jsonify({"error": "Invalid device ID"}), 400

        response = requests.post(f"http://{device.addr}/api/v1/{action}")
            
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Error listing devices: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

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

        if not request_data["device-type"]:
            logger.warning(f"Missing device type")
            return jsonify({"error": "Invalid device type"}), 400

        device_type = None
        try:
            device_type = DeviceType[str(request_data["device-type"])]
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

@app.route('/api/v1/devices', methods=['GET'])
def get_devices():
    try:
        devices_array = []
        for device_id, device in devices.items():
            device_data = json.loads(str(device))  # Parse the JSON string from __str__
            device_data['device_id'] = device_id
            devices_array.append(device_data)
        
        return jsonify(devices_array), 200
    except Exception as e:
        logger.error(f"Error listing devices: {str(e)}")
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

def moveCameraUp():
    print("Move Camera up!")

def moveCameraDown():
    print("Move Camera Down!")

if __name__ == '__main__':
    logger.info("Starting Main Controller Flask API")
    logger.info(f"Running on {app.config['HOST']}:{app.config['PORT']}")

    # Configure IO
    button = Button(4) 
    button.when_activated = moveCameraUp
    button.when_deactivated = moveCameraDown
    
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )
