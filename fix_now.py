# -*- coding: utf-8 -*-
import sqlite3
import os

db_path = 'instance/loan.db'

print("Fixing database...")

# Close all connections
conn = sqlite3.connect(db_path)
conn.isolation_level = None
cursor = conn.cursor()

# Delete problematic records
cursor.execute("DELETE FROM fee_collections WHERE id IN (6, 7)")
print(f"Deleted records 6 and 7")

# Delete any NULL customer_id records
cursor.execute("DELETE FROM fee_collections WHERE customer_id IS NULL")
print(f"Deleted NULL records")

# Vacuum to clean up
cursor.execute("VACUUM")
print("Database cleaned")

conn.close()

print("\nDone! Now restart Flask app.")
