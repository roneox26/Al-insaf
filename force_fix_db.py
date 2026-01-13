# -*- coding: utf-8 -*-
import sqlite3
import os
import shutil

db_path = 'instance/loan.db'

# Create backup
if os.path.exists(db_path):
    backup_path = 'instance/loan_backup.db'
    shutil.copy2(db_path, backup_path)
    print(f"Backup created: {backup_path}")

# Force close any connections and fix
try:
    conn = sqlite3.connect(db_path, timeout=30)
    conn.execute("PRAGMA journal_mode=DELETE")
    cursor = conn.cursor()
    
    # Check current state
    cursor.execute("SELECT id, customer_id FROM fee_collections WHERE id IN (6, 7)")
    records = cursor.fetchall()
    print(f"Current records 6 & 7: {records}")
    
    # Force delete if they have NULL
    cursor.execute("DELETE FROM fee_collections WHERE id IN (6, 7) AND customer_id IS NULL")
    deleted = cursor.rowcount
    print(f"Deleted {deleted} records")
    
    # Also delete any other NULL records
    cursor.execute("DELETE FROM fee_collections WHERE customer_id IS NULL")
    deleted2 = cursor.rowcount
    print(f"Deleted {deleted2} additional NULL records")
    
    conn.commit()
    
    # Verify
    cursor.execute("SELECT COUNT(*) FROM fee_collections WHERE customer_id IS NULL")
    null_count = cursor.fetchone()[0]
    print(f"Remaining NULL records: {null_count}")
    
    conn.close()
    print("\nDatabase fixed! Please restart your Flask app.")
    
except Exception as e:
    print(f"Error: {e}")
    print("\nPlease:")
    print("1. Stop your Flask app completely (Ctrl+C)")
    print("2. Run this script again")
    print("3. Start Flask app")
