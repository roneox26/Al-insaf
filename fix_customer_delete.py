# -*- coding: utf-8 -*-
"""Fix Customer Delete - Make customer_id nullable in collections"""

from app import app, db
from sqlalchemy import text

def fix_customer_delete():
    with app.app_context():
        try:
            print("Cleaning up old migration attempts...")
            # Drop any existing temp tables
            try:
                db.session.execute(text("DROP TABLE IF EXISTS loan_collections_new"))
                db.session.execute(text("DROP TABLE IF EXISTS saving_collections_new"))
                db.session.execute(text("DROP TABLE IF EXISTS fee_collections_new"))
                db.session.commit()
            except:
                db.session.rollback()
            
            print("Updating loan_collections...")
            db.session.execute(text("""
                CREATE TABLE loan_collections_new (
                    id INTEGER PRIMARY KEY,
                    customer_id INTEGER,
                    loan_id INTEGER,
                    amount FLOAT NOT NULL,
                    collection_date DATETIME,
                    staff_id INTEGER NOT NULL,
                    FOREIGN KEY (customer_id) REFERENCES customers(id),
                    FOREIGN KEY (staff_id) REFERENCES user(id)
                )
            """))
            
            db.session.execute(text("INSERT INTO loan_collections_new SELECT * FROM loan_collections"))
            db.session.execute(text("DROP TABLE loan_collections"))
            db.session.execute(text("ALTER TABLE loan_collections_new RENAME TO loan_collections"))
            db.session.commit()
            print("OK loan_collections updated")
            
            print("Updating saving_collections...")
            db.session.execute(text("""
                CREATE TABLE saving_collections_new (
                    id INTEGER PRIMARY KEY,
                    customer_id INTEGER,
                    amount FLOAT NOT NULL,
                    collection_date DATETIME,
                    staff_id INTEGER NOT NULL,
                    FOREIGN KEY (customer_id) REFERENCES customers(id),
                    FOREIGN KEY (staff_id) REFERENCES user(id)
                )
            """))
            
            db.session.execute(text("INSERT INTO saving_collections_new SELECT * FROM saving_collections"))
            db.session.execute(text("DROP TABLE saving_collections"))
            db.session.execute(text("ALTER TABLE saving_collections_new RENAME TO saving_collections"))
            db.session.commit()
            print("OK saving_collections updated")
            
            print("Updating fee_collections...")
            db.session.execute(text("""
                CREATE TABLE fee_collections_new (
                    id INTEGER PRIMARY KEY,
                    customer_id INTEGER,
                    fee_type VARCHAR(50),
                    amount FLOAT NOT NULL,
                    collection_date DATETIME,
                    collected_by INTEGER,
                    note VARCHAR(200),
                    FOREIGN KEY (customer_id) REFERENCES customers(id),
                    FOREIGN KEY (collected_by) REFERENCES user(id)
                )
            """))
            
            db.session.execute(text("INSERT INTO fee_collections_new SELECT * FROM fee_collections"))
            db.session.execute(text("DROP TABLE fee_collections"))
            db.session.execute(text("ALTER TABLE fee_collections_new RENAME TO fee_collections"))
            db.session.commit()
            print("OK fee_collections updated")
            
            print("\nSUCCESS Database updated!")
            print("Customer deletion will now preserve collection history.")
            
        except Exception as e:
            db.session.rollback()
            print(f"\nERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("=" * 60)
    print("Fix Customer Delete - Database Migration")
    print("=" * 60)
    fix_customer_delete()
