#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fix database by adding missing columns"""

from app import app, db
from sqlalchemy import text

print("Fixing database...")

with app.app_context():
    try:
        # Check and add missing columns to customers table
        with db.engine.connect() as conn:
            # Check if created_date column exists
            result = conn.execute(text("PRAGMA table_info(customers)"))
            columns = [row[1] for row in result]
            
            if 'created_date' not in columns:
                conn.execute(text("ALTER TABLE customers ADD COLUMN created_date DATETIME DEFAULT CURRENT_TIMESTAMP"))
                conn.commit()
                print("✓ Added created_date column to customers table")
            
            # Check withdrawals table
            result = conn.execute(text("PRAGMA table_info(withdrawals)"))
            columns = [row[1] for row in result]
            
            if 'customer_id' not in columns:
                conn.execute(text("ALTER TABLE withdrawals ADD COLUMN customer_id INTEGER"))
                conn.commit()
                print("✓ Added customer_id column to withdrawals table")
            
            if 'withdrawal_type' not in columns:
                conn.execute(text("ALTER TABLE withdrawals ADD COLUMN withdrawal_type VARCHAR(20) DEFAULT 'savings'"))
                conn.commit()
                print("✓ Added withdrawal_type column to withdrawals table")
        
        print("\n✓ Database fixed successfully!")
        print("\nYou can now run: python run.py")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nTry closing all applications using the database and run:")
        print("  python reset_database.py")
