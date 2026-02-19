#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quick Fix for loan_id column - Run this on Render.com Shell"""
import os
from flask import Flask
from models.user_model import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///instance/ngo.db').replace('postgres://', 'postgresql://', 1) if os.environ.get('DATABASE_URL', '').startswith('postgres://') else os.environ.get('DATABASE_URL', 'sqlite:///instance/ngo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    try:
        db.session.execute(db.text("ALTER TABLE loan_collections ADD COLUMN loan_id INTEGER"))
        db.session.commit()
        print("✓ Fixed! loan_id column added successfully!")
    except Exception as e:
        if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
            print("✓ Column already exists - no fix needed!")
        else:
            print(f"Error: {e}")
