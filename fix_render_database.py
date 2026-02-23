#!/usr/bin/env python3
"""
Render.com Database Fix Script
Run this in Render Shell to add loan_id column
"""
from app import app, db
from sqlalchemy import text

def fix_database():
    with app.app_context():
        try:
            # Check if loan_id column exists
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='loan_collections' AND column_name='loan_id'
            """))
            
            if result.fetchone() is None:
                print("Adding loan_id column to loan_collections table...")
                
                # Add loan_id column
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
                print("✅ Successfully added loan_id column!")
                print("✅ Database migration completed!")
            else:
                print("✅ loan_id column already exists!")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    fix_database()
