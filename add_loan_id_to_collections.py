# -*- coding: utf-8 -*-
"""
Add loan_id column to loan_collections table
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import config

app = Flask(__name__)
app.config.from_object(config)
db = SQLAlchemy(app)

def add_loan_id_column():
    with app.app_context():
        try:
            print("="*50)
            print("  Database Migration: Adding loan_id column")
            print("="*50)
            
            # Check if column exists
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('loan_collections')]
            
            if 'loan_id' not in columns:
                print("\n[1/2] Adding loan_id column...")
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE loan_collections ADD COLUMN loan_id INTEGER'))
                    conn.commit()
                print("      Column added successfully!")
            else:
                print("\nloan_id column already exists")
            
            # Auto-assign loan_id to existing collections
            print("\n[2/2] Assigning loan_id to existing collections...")
            
            with db.engine.connect() as conn:
                # Get all collections without loan_id
                result = conn.execute(text('SELECT id, customer_id, collection_date FROM loan_collections WHERE loan_id IS NULL'))
                collections_data = result.fetchall()
                
                updated = 0
                for coll_id, customer_id, coll_date in collections_data:
                    # Get customer name
                    customer = conn.execute(text(f'SELECT name FROM customers WHERE id = :cid'), {'cid': customer_id}).fetchone()
                    if customer:
                        customer_name = customer[0]
                        
                        # Find the most recent loan for this customer before collection date
                        loan = conn.execute(
                            text("SELECT id FROM loans WHERE customer_name = :cname AND loan_date <= :cdate ORDER BY loan_date DESC LIMIT 1"),
                            {'cname': customer_name, 'cdate': coll_date}
                        ).fetchone()
                        
                        if loan:
                            loan_id = loan[0]
                            conn.execute(text('UPDATE loan_collections SET loan_id = :lid WHERE id = :cid'), {'lid': loan_id, 'cid': coll_id})
                            updated += 1
                            print(f"      Collection {coll_id} -> Loan {loan_id}")
                
                conn.commit()
            
            print(f"\nUpdated {updated} collections")
            print("\n" + "="*50)
            print("  Migration completed successfully!")
            print("="*50)
            print("\nApp restart korun: python run.py")
            
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    add_loan_id_column()
