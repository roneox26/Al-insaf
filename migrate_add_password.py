# -*- coding: utf-8 -*-
"""
Simple migration to add plain_password column to user table
"""

import sqlite3
import os

def migrate_database():
    db_path = os.path.join('instance', 'loan.db')
    
    if not os.path.exists(db_path):
        print("Database not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(user)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'plain_password' not in columns:
            # Add the column
            cursor.execute("ALTER TABLE user ADD COLUMN plain_password VARCHAR(100)")
            
            # Note: Existing users will need to reset their passwords
            # Do not set default passwords for security reasons
            
            conn.commit()
            print("Successfully added plain_password column!")
            print("Note: Existing users need to reset their passwords via admin panel")
        else:
            print("Column plain_password already exists!")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    migrate_database()
