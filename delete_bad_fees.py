# -*- coding: utf-8 -*-
import sqlite3

# Connect to database
conn = sqlite3.connect('instance/loan.db')
cursor = conn.cursor()

# Delete fee collections with NULL customer_id
cursor.execute("DELETE FROM fee_collections WHERE customer_id IS NULL")
deleted = cursor.rowcount

conn.commit()
conn.close()

print(f"Deleted {deleted} fee collection records with NULL customer_id")
print("Database fixed!")
