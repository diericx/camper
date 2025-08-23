# Initialize Flask app
import logging
from flask import Flask


def setupFlaskApp():
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
  app.config['PORT'] = 8080 

  return app, logger