#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Add Database Indexes for Performance"""

from app import app, db
from models.customer_model import Customer
from models.loan_collection_model import LoanCollection
from models.saving_collection_model import SavingCollection

def add_indexes():
    with app.app_context():
        print("Adding database indexes...")
        
        # Add indexes using raw SQL
        try:
            # Customer indexes
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_customer_member_no ON customer(member_no)')
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_customer_phone ON customer(phone)')
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_customer_staff_id ON customer(staff_id)')
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_customer_is_active ON customer(is_active)')
            
            # Collection indexes
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_loan_collection_date ON loan_collection(collection_date)')
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_loan_collection_customer ON loan_collection(customer_id)')
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_saving_collection_date ON saving_collection(collection_date)')
            db.engine.execute('CREATE INDEX IF NOT EXISTS idx_saving_collection_customer ON saving_collection(customer_id)')
            
            print("✓ Indexes added successfully!")
            print("\nIndexes created:")
            print("- customer: member_no, phone, staff_id, is_active")
            print("- loan_collection: collection_date, customer_id")
            print("- saving_collection: collection_date, customer_id")
            
        except Exception as e:
            print(f"Error: {e}")
            print("\nTry this SQL manually in Render Shell:")
            print("""
python -c "
from app import app, db
with app.app_context():
    db.engine.execute('CREATE INDEX IF NOT EXISTS idx_customer_member_no ON customer(member_no)')
    db.engine.execute('CREATE INDEX IF NOT EXISTS idx_customer_phone ON customer(phone)')
    db.engine.execute('CREATE INDEX IF NOT EXISTS idx_customer_staff_id ON customer(staff_id)')
    db.engine.execute('CREATE INDEX IF NOT EXISTS idx_loan_collection_date ON loan_collection(collection_date)')
    db.engine.execute('CREATE INDEX IF NOT EXISTS idx_loan_collection_customer ON loan_collection(customer_id)')
    print('Indexes created!')
"
            """)

if __name__ == '__main__':
    add_indexes()
