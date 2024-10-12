import sys
import os
from os.path import join, dirname, abspath

# Calculate the path based on the location of the WSGI script
PROJECT_DIR = dirname(dirname(abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

# Add the virtual environment site-packages directory to the path
VENV_DIR = join(PROJECT_DIR, 'venv', 'lib', 'python3.10', 'site-packages')
sys.path.insert(0, VENV_DIR)

# Import the Flask app
from AppCisco import app as application  # Adjust this line based on your app structure

