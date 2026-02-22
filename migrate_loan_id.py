"""
Migration script to add loan_id column to loan_collections table
Run this on Render.com after deployment
"""
from app import app, db
from models.loan_collection_model import LoanCollection
from models.loan_model import Loan
from sqlalchemy import text

def migrate():
    with app.app_context():
        try:
            # Check if column exists
            result = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='loan_collections' AND column_name='loan_id'"))
            if result.fetchone():
                print("✅ loan_id column already exists!")
                return
            
            print("Adding loan_id column...")
            
            # Add loan_id column
            db.session.execute(text("ALTER TABLE loan_collections ADD COLUMN loan_id INTEGER"))
            db.session.commit()
            print("✅ loan_id column added successfully!")
            
            # Link existing collections to loans
            print("Linking existing collections to loans...")
            collections = LoanCollection.query.all()
            for collection in collections:
                # Find the loan for this customer
                loan = Loan.query.filter_by(customer_name=collection.customer.name).first()
                if loan:
                    collection.loan_id = loan.id
            
            db.session.commit()
            print(f"✅ Linked {len(collections)} collections to loans!")
            print("✅ Migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {e}")
            raise

if __name__ == '__main__':
    migrate()
