# -*- coding: utf-8 -*-
from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        with db.engine.connect() as conn:
            # Add join_date column without default
            try:
                conn.execute(text("ALTER TABLE user ADD COLUMN join_date DATETIME"))
                conn.commit()
                print("[OK] Added join_date column")
            except Exception as e:
                if "duplicate column" in str(e).lower():
                    print("[SKIP] join_date already exists")
                else:
                    print(f"[ERROR] {e}")
            
            # Update existing NULL values to current timestamp
            try:
                conn.execute(text("UPDATE user SET join_date = CURRENT_TIMESTAMP WHERE join_date IS NULL"))
                conn.commit()
                print("[OK] Updated NULL join_date values")
            except Exception as e:
                print(f"[ERROR] {e}")
        
        print("\n[SUCCESS] join_date column fixed!")
        
    except Exception as e:
        print(f"[ERROR] {e}")
