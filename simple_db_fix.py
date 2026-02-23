#!/usr/bin/env python3
"""
Simple Database Fix - Just add the column
"""
import os
from sqlalchemy import create_engine, text

def simple_fix():
    # Get database URL from environment
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment!")
        print("💡 This script should be run on Render.com")
        return
    
    # Fix postgres:// to postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    print(f"🔗 Connecting to database...")
    engine = create_engine(database_url)
    
    with engine.connect() as conn:
        try:
            # Check if column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='loan_collections' AND column_name='loan_id'
            """))
            
            if result.fetchone() is None:
                print("➕ Adding loan_id column...")
                
                # Add column
                conn.execute(text("""
                    ALTER TABLE loan_collections 
                    ADD COLUMN loan_id INTEGER
                """))
                conn.commit()
                
                print("✅ Column added successfully!")
                print("🔄 Please restart your Render service!")
            else:
                print("✅ Column already exists!")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            conn.rollback()

if __name__ == '__main__':
    simple_fix()
