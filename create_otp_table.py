# -*- coding: utf-8 -*-
"""Create OTP table in database"""

from app import app, db

with app.app_context():
    try:
        print("Creating OTP table...")
        db.create_all()
        print("✓ OTP table created successfully!")
        print("\nYou can now use OTP system for Admin Settings.")
    except Exception as e:
        print(f"Error: {e}")
