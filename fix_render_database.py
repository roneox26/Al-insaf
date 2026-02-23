#!/usr/bin/env python3
"""
Render.com Database Fix Script
Run this in Render Shell to add loan_id column
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text, inspect

def fix_database():
    with app.app_context():
        try:
            print("🔍 Checking database connection...")
            print(f"Database URL: {db.engine.url}")
            
            # Check if loan_id column exists
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('loan_collections')]
            
            print(f"\n📋 Current columns in loan_collections: {columns}")
            
            if 'loan_id' not in columns:
                print("\n➕ Adding loan_id column to loan_collections table...")
                
                # Add loan_id column (nullable)
                db.session.execute(text("""
                    ALTER TABLE loan_collections 
                    ADD COLUMN loan_id INTEGER NULL
                """))
                db.session.commit()
                print("✅ loan_id column added successfully!")
                
                # Try to add foreign key constraint
                try:
                    print("\n🔗 Adding foreign key constraint...")
                    db.session.execute(text("""
                        ALTER TABLE loan_collections 
                        ADD CONSTRAINT fk_loan_collections_loan_id 
                        FOREIGN KEY (loan_id) REFERENCES loans(id) ON DELETE SET NULL
                    """))
                    db.session.commit()
                    print("✅ Foreign key constraint added!")
                except Exception as fk_error:
                    print(f"⚠️  Foreign key constraint failed (not critical): {fk_error}")
                    db.session.rollback()
                
                print("\n✅ Database migration completed successfully!")
                print("\n🔄 Please restart your Render service now.")
            else:
                print("\n✅ loan_id column already exists!")
                print("\n📊 Verifying column details...")
                result = db.session.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name='loan_collections' AND column_name='loan_id'
                """))
                col_info = result.fetchone()
                if col_info:
                    print(f"   Column: {col_info[0]}")
                    print(f"   Type: {col_info[1]}")
                    print(f"   Nullable: {col_info[2]}")
                print("\n✅ Database is already up to date!")
                
        except Exception as e:
            print(f"\n❌ Error occurred: {e}")
            print(f"\n📝 Error details: {type(e).__name__}")
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    print("="*60)
    print("🔧 Render.com Database Migration Script")
    print("="*60)
    fix_database()
    print("="*60)
