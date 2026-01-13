# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('instance/loan.db')
cursor = conn.cursor()

# Check table structure
cursor.execute("PRAGMA table_info(fee_collections)")
columns = cursor.fetchall()

print("Fee Collections Table Structure:")
for col in columns:
    print(f"  {col[1]} - Type: {col[2]}, NotNull: {col[3]}, Default: {col[4]}")

# Check for any records
cursor.execute("SELECT id, customer_id, fee_type, amount FROM fee_collections")
records = cursor.fetchall()

print(f"\nTotal records: {len(records)}")
if records:
    print("\nAll records:")
    for rec in records:
        print(f"  ID: {rec[0]}, Customer ID: {rec[1]}, Type: {rec[2]}, Amount: {rec[3]}")

conn.close()
