# -*- coding: utf-8 -*-
from app import app, db
from models.user_model import User
from sqlalchemy import text

with app.app_context():
    try:
        with db.engine.connect() as conn:
            columns_to_add = [
                ("phone", "VARCHAR(20)"),
                ("address", "VARCHAR(200)"),
                ("photo", "VARCHAR(200)"),
                ("join_date", "DATETIME DEFAULT CURRENT_TIMESTAMP"),
                ("salary", "FLOAT DEFAULT 0.0"),
                ("status", "VARCHAR(20) DEFAULT 'active'"),
                ("nid", "VARCHAR(50)")
            ]
            
            for col_name, col_type in columns_to_add:
                try:
                    conn.execute(text(f"ALTER TABLE user ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
                    print(f"[OK] Added column: {col_name}")
                except Exception as e:
                    if "duplicate column name" in str(e).lower():
                        print(f"[SKIP] Column {col_name} already exists")
                    else:
                        print(f"[ERROR] Error adding {col_name}: {e}")
        
        print("\n[SUCCESS] Database updated!")
        print("Staff fields: phone, address, photo, join_date, salary, status, nid")
        
    except Exception as e:
        print(f"[ERROR] {e}")
