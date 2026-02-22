"""
Auto-migration script for loan_id column
This will run automatically and fix the database
"""
import os
import sys

def auto_migrate():
    try:
        from app import app, db
        from sqlalchemy import text, inspect
        
        with app.app_context():
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('loan_collections')]
            
            if 'loan_id' not in columns:
                print("🔧 Adding loan_id column...")
                db.session.execute(text("ALTER TABLE loan_collections ADD COLUMN loan_id INTEGER"))
                db.session.commit()
                print("✅ loan_id column added!")
                
                # Link existing collections
                from models.loan_collection_model import LoanCollection
                from models.loan_model import Loan
                from models.customer_model import Customer
                
                collections = LoanCollection.query.all()
                for collection in collections:
                    customer = Customer.query.get(collection.customer_id)
                    if customer:
                        loan = Loan.query.filter_by(customer_name=customer.name).first()
                        if loan:
                            # Manually update without using the model attribute
                            db.session.execute(
                                text("UPDATE loan_collections SET loan_id = :loan_id WHERE id = :id"),
                                {"loan_id": loan.id, "id": collection.id}
                            )
                
                db.session.commit()
                print(f"✅ Linked {len(collections)} collections!")
                print("⚠️ Please uncomment loan_id in loan_collection_model.py and restart!")
            else:
                print("✅ Database is up to date!")
                
    except Exception as e:
        print(f"⚠️ Migration error (may be safe to ignore): {e}")

if __name__ == '__main__':
    auto_migrate()
