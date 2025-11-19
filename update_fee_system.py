# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import app, db
from models.customer_model import Customer
from models.fee_model import FeeCollection
from models.user_model import User

def update_fee_system():
    with app.app_context():
        try:
            # Create all tables (including new fee_collections table)
            db.create_all()
            print("Database tables created/updated successfully!")
            
            # Migrate existing admission fees to fee_collections
            customers = Customer.query.all()
            admin = User.query.filter_by(role='admin').first()
            
            for customer in customers:
                # Check if admission fee already migrated
                existing = FeeCollection.query.filter_by(
                    customer_id=customer.id, 
                    fee_type='admission'
                ).first()
                
                if not existing and customer.admission_fee > 0:
                    fee_col = FeeCollection(
                        customer_id=customer.id,
                        fee_type='admission',
                        amount=customer.admission_fee,
                        collected_by=admin.id if admin else None,
                        collection_date=customer.created_date
                    )
                    db.session.add(fee_col)
                    print(f"Migrated admission fee for {customer.name}: {customer.admission_fee}")
            
            db.session.commit()
            print("\nFee system updated successfully!")
            print("Three fee types are now available:")
            print("   1. Admission Fee")
            print("   2. Welfare Fee")
            print("   3. Application Fee")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")

if __name__ == '__main__':
    update_fee_system()
