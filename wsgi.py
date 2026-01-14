#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

# Add project directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Import the Flask app
from app import app as application

# Initialize database on first run
try:
    from app import init_db
    init_db()
except Exception as e:
    print(f"Database initialization: {e}")

if __name__ == "__main__":
    application.run()
