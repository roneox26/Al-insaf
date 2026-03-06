# -*- coding: utf-8 -*-
"""
Auto Migration: Runs on application startup
Makes customer_id nullable in all collection tables
"""

from sqlalchemy import text, inspect

def auto_migrate_customer_id(app, db):
    """Automatically make customer_id nullable on startup"""
    try:
        with app.app_context():
            engine_name = db.engine.name
            
            if engine_name == 'postgresql':
                inspector = inspect(db.engine)
                
                tables_to_fix = {
                    'loan_collections': 'customer_id',
                    'saving_collections': 'customer_id',
                    'fee_collections': 'customer_id',
                    'withdrawals': 'customer_id'
                }
                
                for table_name, column_name in tables_to_fix.items():
                    try:
                        # Check if table exists
                        if not inspector.has_table(table_name):
                            continue
                        
                        # Check if column is nullable
                        columns = inspector.get_columns(table_name)
                        column_info = next((col for col in columns if col['name'] == column_name), None)
                        
                        if column_info and not column_info['nullable']:
                            # Make it nullable
                            sql = f"ALTER TABLE {table_name} ALTER COLUMN {column_name} DROP NOT NULL"
                            db.session.execute(text(sql))
                            db.session.commit()
                            print(f"✓ Auto-migrated: {table_name}.{column_name} is now nullable")
                    
                    except Exception as e:
                        db.session.rollback()
                        # Silently continue if already migrated
                        if 'does not exist' not in str(e).lower():
                            print(f"Migration note for {table_name}: {str(e)}")
            
            return True
            
    except Exception as e:
        print(f"Auto-migration error: {str(e)}")
        return False
