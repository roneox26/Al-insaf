#!/usr/bin/env python3
"""
Emergency Fix: Make loan_id column optional in queries
This will allow the app to work even if loan_id column doesn't exist
"""
from app import app, db
from sqlalchemy import inspect, text

def check_and_fix():
    with app.app_context():
        try:
            # Check if loan_id exists
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('loan_collections')]
            
            if 'loan_id' not in columns:
                print("⚠️  loan_id column NOT found!")
                print("🔧 Adding loan_id column now...")
                
                # Add the column
                db.session.execute(text("""
                    ALTER TABLE loan_collections 
                    ADD COLUMN IF NOT EXISTS loan_id INTEGER
                """))
                db.session.commit()
                
                print("✅ loan_id column added!")
                print("🔄 Please restart the application")
                return True
            else:
                print("✅ loan_id column exists!")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    check_and_fix()
