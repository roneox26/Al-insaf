# -*- coding: utf-8 -*-
"""
Migration script to add loan_id column to loan_collections table
Run this on deployed server to fix the database schema
"""

from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        try:
            # Check if loan_id column exists
            result = db.session.execute(text(
                "SELECT COUNT(*) FROM pragma_table_info('loan_collections') WHERE name='loan_id'"
            ))
            exists = result.scalar() > 0
            
            if not exists:
                print("Adding loan_id column to loan_collections table...")
                db.session.execute(text(
                    "ALTER TABLE loan_collections ADD COLUMN loan_id INTEGER"
                ))
                db.session.commit()
                print("✓ loan_id column added successfully!")
            else:
                print("✓ loan_id column already exists")
                
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()

if __name__ == '__main__':
    print("Starting database migration...")
    migrate()
    print("Migration completed!")
