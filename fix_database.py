# -*- coding: utf-8 -*-
"""
Quick fix for deployed database - adds missing loan_id column
Run this ONCE after deployment if you get "loan_id" error
"""

import sqlite3
import os
import sys

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def fix_database():
    # Try multiple database names
    db_names = ['loan.db', 'ngo.db', 'database.db']
    db_path = None
    
    for db_name in db_names:
        test_path = os.path.join('instance', db_name)
        if os.path.exists(test_path):
            db_path = test_path
            break
    
    if not db_path:
        print("[ERROR] Database not found!")
        print("Please run 'python create_db.py' first")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if loan_id column exists
        cursor.execute("PRAGMA table_info(loan_collections)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'loan_id' in columns:
            print("[OK] loan_id column already exists")
        else:
            print("[INFO] Adding loan_id column...")
            cursor.execute("ALTER TABLE loan_collections ADD COLUMN loan_id INTEGER")
            conn.commit()
            print("[SUCCESS] loan_id column added!")
            print("[SUCCESS] Database fixed! customer_loan_sheet will work now.")
        
    except Exception as e:
        print(f"[ERROR] {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 50)
    print("Database Fix Script")
    print("=" * 50)
    fix_database()
    print("=" * 50)
