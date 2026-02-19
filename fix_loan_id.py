#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fix loan_id column in loan_collections table
This script adds the loan_id column if it doesn't exist
"""

import os
import sys
from flask import Flask
from models.user_model import db
from sqlalchemy import text

# Create Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///instance/ngo.db')
if app.config['SQLALCHEMY_DATABASE_URI'].startswith('postgres://'):
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'].replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def fix_loan_id_column():
    """Add loan_id column to loan_collections table if it doesn't exist"""
    with app.app_context():
        try:
            # Check if column exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='loan_collections' AND column_name='loan_id'
            """))
            
            if result.fetchone() is None:
                print("Adding loan_id column to loan_collections table...")
                
                # Add the column
                db.session.execute(text("""
                    ALTER TABLE loan_collections 
                    ADD COLUMN loan_id INTEGER
                """))
                
                # Add foreign key constraint
                db.session.execute(text("""
                    ALTER TABLE loan_collections 
                    ADD CONSTRAINT fk_loan_collections_loan_id 
                    FOREIGN KEY (loan_id) REFERENCES loans(id)
                """))
                
                db.session.commit()
                print("✓ Successfully added loan_id column!")
            else:
                print("✓ loan_id column already exists!")
                
        except Exception as e:
            db.session.rollback()
            print(f"Error: {str(e)}")
            print("\nTrying alternative method for SQLite...")
            
            try:
                # For SQLite, we need to check differently
                db.session.execute(text("SELECT loan_id FROM loan_collections LIMIT 1"))
                print("✓ loan_id column already exists!")
            except:
                print("Adding loan_id column (SQLite method)...")
                db.session.execute(text("""
                    ALTER TABLE loan_collections 
                    ADD COLUMN loan_id INTEGER
                """))
                db.session.commit()
                print("✓ Successfully added loan_id column!")

if __name__ == '__main__':
    print("=" * 50)
    print("Fixing loan_id column in loan_collections table")
    print("=" * 50)
    fix_loan_id_column()
    print("\nDone! You can now run your application.")
