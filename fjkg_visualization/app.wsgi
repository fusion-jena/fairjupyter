import sys
import os

# Set the path to the Flask app
sys.path.insert(0, '/var/www/flaskapp')

# Adjust script_name to match the application root
os.environ['SCRIPT_NAME'] = '/fj'

# Import the Flask app
from app import app as application
