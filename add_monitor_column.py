# -*- coding: utf-8 -*-
from app import app, db
from sqlalchemy import text
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with app.app_context():
    try:
        # Add is_monitor column
        with db.engine.connect() as conn:
            conn.execute(text('ALTER TABLE user ADD COLUMN is_monitor BOOLEAN DEFAULT 0'))
            conn.commit()
        print("SUCCESS: is_monitor column added!")
        
        # Update existing records
        with db.engine.connect() as conn:
            conn.execute(text("UPDATE user SET is_monitor = 0 WHERE is_monitor IS NULL"))
            conn.commit()
        print("SUCCESS: Updated existing staff records!")
        
    except Exception as e:
        if "duplicate column" in str(e).lower():
            print("INFO: is_monitor column already exists!")
        else:
            print(f"ERROR: {e}")
            print("\nIf column doesn't exist, run this SQL manually:")
            print("ALTER TABLE user ADD COLUMN is_monitor BOOLEAN DEFAULT 0;")
            print("UPDATE user SET is_monitor = 0 WHERE is_monitor IS NULL;")
