#!/bin/bash

# Main Controller Flask API Startup Script
# For Raspberry Pi deployment

echo "Starting Main Controller Flask API..."

source setup-pyenv.sh

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=production

# Start the Flask application
echo "Starting Flask API on port 8080..."
echo "API will be accessible at http://0.0.0.0:8080"
echo "Health check: http://0.0.0.0:8080/health"
echo "Device endpoint: PUT http://0.0.0.0:8080/api/v1/device/{id}"
echo ""
echo "Press Ctrl+C to stop the server"
echo "Logs will be written to main-controller.log"

python3 app.py