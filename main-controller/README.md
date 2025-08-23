# Main Controller Flask API

A simple Flask API designed for Raspberry Pi device control as part of the camper project.

## Features

- **PUT /api/v1/device/{id}** - Update device information
- **GET /health** - Health check endpoint
- Basic error handling and validation
- Logging for debugging on Raspberry Pi
- Network accessible (0.0.0.0:8080)
- Minimal dependencies

## Quick Start

### On Raspberry Pi

1. **Clone and navigate to the project:**

   ```bash
   cd main-controller
   ```

2. **Run the startup script:**

   ```bash
   ./run.sh
   ```

   This script will:

   - Create a virtual environment if needed
   - Install dependencies
   - Start the Flask API on port 5000

### Manual Setup

1. **Create virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python3 app.py
   ```

## API Endpoints

### Update Device

- **URL:** `PUT /api/v1/device/{id}`
- **Description:** Update device information
- **Parameters:**
  - `id` (path parameter): Device identifier
- **Request Body:** JSON (optional)
- **Success Response:**
  ```json
  { "status": "success" }
  ```
- **Error Responses:**
  - `400`: `{"error": "Invalid device ID"}`
  - `500`: `{"error": "Internal server error"}`

### Health Check

- **URL:** `GET /health`
- **Description:** Check API health status
- **Success Response:**
  ```json
  {
    "status": "healthy",
    "timestamp": "2024-01-01T12:00:00.000000",
    "service": "main-controller"
  }
  ```

## Usage Examples

### Using curl

```bash
# Health check
curl http://localhost:8080/health

# Update device
curl -X PUT http://localhost:8080/api/v1/device/sensor-01 \
  -H "Content-Type: application/json" \
  -d '{"status": "active"}'
```

### From another device on the network

```bash
# Replace RASPBERRY_PI_IP with your Pi's IP address
curl -X PUT http://RASPBERRY_PI_IP:8080/api/v1/device/sensor-01 \
  -H "Content-Type: application/json" \
  -d '{"status": "active"}'
```

## Configuration

The API is configured for Raspberry Pi deployment:

- **Host:** 0.0.0.0 (accepts connections from any IP)
- **Port:** 8080
- **Debug:** False (production mode)
- **Logging:** File (`main-controller.log`) and console output

## Logging

Logs are written to:

- **File:** `main-controller.log` in the same directory
- **Console:** Standard output

Log format includes timestamp, log level, and message for easy debugging.

## File Structure

```
main-controller/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── run.sh             # Startup script (executable)
├── README.md          # This file
└── main-controller.log # Log file (created when running)
```

## Development

To extend the API:

1. Add new routes in `app.py`
2. Update logging as needed
3. Test with the health endpoint first
4. Use the existing error handling patterns

## Troubleshooting

### Common Issues

1. **Port already in use:**

   ```bash
   # Find process using port 5000
   lsof -i :5000
   # Kill the process if needed
   kill -9 <PID>
   ```

2. **Permission denied on run.sh:**

   ```bash
   chmod +x run.sh
   ```

3. **Python/pip not found:**
   ```bash
   # Install Python 3 and pip on Raspberry Pi
   sudo apt update
   sudo apt install python3 python3-pip python3-venv
   ```

### Logs

Check `main-controller.log` for detailed error information and request logs.

## Network Access

The API is configured to accept connections from any IP address (0.0.0.0). To access from other devices:

1. Find your Raspberry Pi's IP address:

   ```bash
   hostname -I
   ```

2. Access the API from other devices using:
   ```
   http://RASPBERRY_PI_IP:5000/api/v1/device/{id}
   ```

## Security Note

This is a basic implementation. For production use, consider adding:

- Authentication/authorization
- HTTPS/TLS encryption
- Rate limiting
- Input sanitization
- Firewall rules
