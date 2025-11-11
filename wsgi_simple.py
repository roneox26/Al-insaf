import sys
import os

# Add project directory to path
project_home = '/home/rone12/Al-insaf'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Import the Flask app
from app import app as application

# That's it! Keep it simple for PythonAnywhere
