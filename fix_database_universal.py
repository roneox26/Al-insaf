#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Universal Database Fix Script
Fixes missing loan_id column in loan_collections table
Works for both PostgreSQL and SQLite
"""

import os
from flask import Flask
from models.user_model import db

# Create Flask app
app = Flask(__name__)

# Database configuration
database_url = os.environ.get('DATABASE_URL', 'sqlite:///instance/ngo.db')
if database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def fix_database():
    """Fix database schema issues"""
    with app.app_context():
        try:
            # Import all models to ensure they're registered
            from models.loan_collection_model import LoanCollection
            from models.loan_model import Loan
            
            print("Checking database schema...")
            
            # Try to query loan_id column
            try:
                result = db.session.execute(db.text("SELECT loan_id FROM loan_collections LIMIT 1"))
                result.fetchone()
                print("✓ loan_id column exists!")
                return
            except Exception as e:
                print(f"✗ loan_id column missing: {str(e)}")
                print("\nAdding loan_id column...")
            
            # Add the column
            try:
                db.session.execute(db.text("""
                    ALTER TABLE loan_collections 
                    ADD COLUMN loan_id INTEGER
                """))
                db.session.commit()
                print("✓ Successfully added loan_id column!")
                
                # Try to add foreign key (may fail on SQLite, that's OK)
                try:
                    db.session.execute(db.text("""
                        ALTER TABLE loan_collections 
                        ADD CONSTRAINT fk_loan_collections_loan_id 
                        FOREIGN KEY (loan_id) REFERENCES loans(id)
                    """))
                    db.session.commit()
                    print("✓ Added foreign key constraint!")
                except:
                    print("⚠ Could not add foreign key constraint (SQLite limitation)")
                    
            except Exception as e:
                db.session.rollback()
                print(f"✗ Error adding column: {str(e)}")
                raise
                
        except Exception as e:
            print(f"\n✗ Fatal error: {str(e)}")
            print("\nPlease run this command manually on your database:")
            print("ALTER TABLE loan_collections ADD COLUMN loan_id INTEGER;")
            return False
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("DATABASE FIX SCRIPT")
    print("=" * 60)
    print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}...")
    print()
    
    if fix_database():
        print("\n" + "=" * 60)
        print("✓ Database fixed successfully!")
        print("=" * 60)
        print("\nYou can now restart your application.")
    else:
        print("\n" + "=" * 60)
        print("✗ Fix failed - manual intervention required")
        print("=" * 60)
