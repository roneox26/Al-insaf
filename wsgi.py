import sys
import os

# Add your project directory to the sys.path
project_home = '/home/yourusername/Al-insaf'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Import flask app
from app import app as application
