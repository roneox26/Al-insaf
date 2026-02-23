# -*- coding: utf-8 -*-
"""
Migration script to add loan_id column to loan_collections table
"""
from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Check if column exists
        result = db.session.execute(text("PRAGMA table_info(loan_collections)"))
        columns = [row[1] for row in result]
        
        if 'loan_id' not in columns:
            print("Adding loan_id column to loan_collections table...")
            db.session.execute(text("ALTER TABLE loan_collections ADD COLUMN loan_id INTEGER"))
            db.session.commit()
            print("✓ loan_id column added successfully!")
        else:
            print("✓ loan_id column already exists!")
            
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
