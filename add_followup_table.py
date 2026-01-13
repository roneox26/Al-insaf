"""
Add Follow-up Table to Database
This script creates the followups table for tracking customer follow-ups
"""

from app import app, db
from models.followup_model import FollowUp

def add_followup_table():
    with app.app_context():
        try:
            # Create the followups table
            db.create_all()
            print("✅ Follow-up table created successfully!")
            
            # Verify table creation
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'followups' in tables:
                print("✅ Verified: 'followups' table exists in database")
                
                # Show table columns
                columns = inspector.get_columns('followups')
                print("\n📋 Table Structure:")
                for col in columns:
                    print(f"  - {col['name']}: {col['type']}")
            else:
                print("❌ Error: 'followups' table not found")
                
        except Exception as e:
            print(f"❌ Error creating follow-up table: {e}")
            db.session.rollback()

if __name__ == '__main__':
    print("🚀 Adding Follow-up Table...")
    add_followup_table()
    print("\n✅ Migration completed!")
