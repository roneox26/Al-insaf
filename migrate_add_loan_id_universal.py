# -*- coding: utf-8 -*-
"""
Universal migration script to add loan_id column to loan_collections table
Works with both SQLite and PostgreSQL
"""
from app import app, db
from sqlalchemy import text, inspect

def check_column_exists(table_name, column_name):
    """Check if column exists in table"""
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

with app.app_context():
    try:
        print("Checking database connection...")
        
        # Check if loan_collections table exists
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'loan_collections' not in tables:
            print("ERROR: loan_collections table does not exist!")
            print("Please run 'python create_db.py' first to create the database tables.")
            exit(1)
        
        # Check if loan_id column exists
        if not check_column_exists('loan_collections', 'loan_id'):
            print("Adding loan_id column to loan_collections table...")
            
            # Add the column
            db.session.execute(text("ALTER TABLE loan_collections ADD COLUMN loan_id INTEGER"))
            
            # Add foreign key constraint if supported
            try:
                db.session.execute(text("ALTER TABLE loan_collections ADD CONSTRAINT fk_loan_collections_loan_id FOREIGN KEY (loan_id) REFERENCES loans(id)"))
                print("Foreign key constraint added successfully!")
            except Exception as fk_error:
                print(f"Note: Could not add foreign key constraint: {fk_error}")
                print("This is normal for some database configurations.")
            
            db.session.commit()
            print("✅ [SUCCESS] loan_id column added successfully!")
            print("✅ Database migration completed!")
            print("✅ You can now use Individual Loan Sheets feature!")
            
        else:
            print("✅ [SUCCESS] loan_id column already exists!")
            print("✅ Database is up to date!")
            
        # Verify the column was added
        if check_column_exists('loan_collections', 'loan_id'):
            print("✅ Verification: loan_id column is present in the database.")
        else:
            print("❌ Verification failed: loan_id column not found!")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure the database is accessible")
        print("2. Check if you have proper database permissions")
        print("3. Try running 'python create_db.py' first")
        print("4. Contact support if the issue persists")
        db.session.rollback()