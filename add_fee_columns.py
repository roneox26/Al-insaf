# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import sqlite3

def add_fee_columns():
    try:
        conn = sqlite3.connect('instance/loan.db')
        cursor = conn.cursor()
        
        # Check if columns exist
        cursor.execute("PRAGMA table_info(customers)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Add welfare_fee column if not exists
        if 'welfare_fee' not in columns:
            cursor.execute("ALTER TABLE customers ADD COLUMN welfare_fee REAL DEFAULT 0.0")
            print("Added welfare_fee column to customers table")
        else:
            print("welfare_fee column already exists")
        
        # Add application_fee column if not exists
        if 'application_fee' not in columns:
            cursor.execute("ALTER TABLE customers ADD COLUMN application_fee REAL DEFAULT 0.0")
            print("Added application_fee column to customers table")
        else:
            print("application_fee column already exists")
        
        # Create fee_collections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fee_collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                fee_type VARCHAR(50) NOT NULL,
                amount REAL NOT NULL,
                collection_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                collected_by INTEGER,
                note VARCHAR(200),
                FOREIGN KEY (customer_id) REFERENCES customers(id),
                FOREIGN KEY (collected_by) REFERENCES user(id)
            )
        """)
        print("Created fee_collections table")
        
        conn.commit()
        conn.close()
        
        print("\nDatabase updated successfully!")
        print("You can now use three separate fee types:")
        print("  1. Admission Fee")
        print("  2. Welfare Fee")
        print("  3. Application Fee")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    add_fee_columns()
