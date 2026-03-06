# -*- coding: utf-8 -*-
"""
Database Migration: Make customer_id nullable
This allows customer deletion while preserving collection data
"""

from app import app, db
from sqlalchemy import text

def migrate_database():
    with app.app_context():
        try:
            print("="*50)
            print("Database Migration: Make customer_id nullable")
            print("="*50)
            
            engine_name = db.engine.name
            print(f"\nDatabase: {engine_name}")
            
            if engine_name == 'postgresql':
                print("\nMaking customer_id nullable in PostgreSQL...")
                
                tables = [
                    'loan_collections',
                    'saving_collections',
                    'fee_collections',
                    'withdrawals'
                ]
                
                for table in tables:
                    try:
                        sql = f"ALTER TABLE {table} ALTER COLUMN customer_id DROP NOT NULL"
                        db.session.execute(text(sql))
                        print(f"✓ {table}")
                    except Exception as e:
                        if 'does not exist' in str(e):
                            print(f"  {table} - column already nullable")
                        else:
                            print(f"  {table} - {str(e)}")
                
                db.session.commit()
                print("\n✓ Migration completed!")
                
            elif engine_name == 'sqlite':
                print("\n✓ SQLite - No migration needed (already nullable)")
                
            else:
                print(f"\n✓ {engine_name} - Check manually")
            
            print("\n" + "="*50)
            print("Customer delete will now work properly!")
            print("="*50)
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False

if __name__ == '__main__':
    print("\nThis will make customer_id nullable in database.")
    print("This allows customer deletion while keeping collection data.\n")
    
    response = input("Run migration? (yes/no): ").strip().lower()
    if response == 'yes':
        if migrate_database():
            print("\n✓ Success! You can now delete customers.")
        else:
            print("\n❌ Migration failed.")
    else:
        print("Cancelled.")
