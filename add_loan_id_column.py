# -*- coding: utf-8 -*-
"""
Migration script to add loan_id column to loan_collections table
Run this after updating the model
"""

from app import app, db
from models.loan_collection_model import LoanCollection
from models.loan_model import Loan
from models.customer_model import Customer
from sqlalchemy import text

def add_loan_id_column():
    with app.app_context():
        try:
            # Check if column exists
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('loan_collections')]
            
            if 'loan_id' not in columns:
                print("Adding loan_id column to loan_collections table...")
                
                # Add the column
                with db.engine.connect() as conn:
                    conn.execute(text('ALTER TABLE loan_collections ADD COLUMN loan_id INTEGER'))
                    conn.commit()
                
                print("✓ loan_id column added successfully!")
                
                # Now link existing collections to loans
                print("\nLinking existing collections to loans...")
                
                collections = LoanCollection.query.all()
                updated = 0
                
                for collection in collections:
                    if collection.loan_id is None:
                        # Find the most recent loan for this customer before this collection
                        loan = Loan.query.filter(
                            Loan.customer_name == collection.customer.name,
                            Loan.loan_date <= collection.collection_date
                        ).order_by(Loan.loan_date.desc()).first()
                        
                        if loan:
                            collection.loan_id = loan.id
                            updated += 1
                
                db.session.commit()
                print(f"✓ Linked {updated} collections to their loans!")
                
            else:
                print("✓ loan_id column already exists!")
                
        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    print("=" * 50)
    print("Loan ID Column Migration")
    print("=" * 50)
    add_loan_id_column()
    print("\n✓ Migration completed!")
