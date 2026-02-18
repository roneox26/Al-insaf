# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import app, db, Customer, Loan, LoanCollection

def link_collections_to_loans():
    with app.app_context():
        print("Linking loan collections to loans...")
        
        customers = Customer.query.all()
        
        for customer in customers:
            # Get all loans for this customer
            loans = Loan.query.filter_by(customer_name=customer.name).order_by(Loan.loan_date).all()
            
            if not loans:
                continue
            
            # Get all collections for this customer
            collections = LoanCollection.query.filter_by(customer_id=customer.id).order_by(LoanCollection.collection_date).all()
            
            if not collections:
                continue
            
            # Link collections to the most recent loan
            latest_loan = loans[-1]
            
            for collection in collections:
                if not collection.loan_id:
                    collection.loan_id = latest_loan.id
                    print(f"  Linked collection for {customer.name} to loan #{latest_loan.id}")
        
        db.session.commit()
        print("\nDone!")

if __name__ == '__main__':
    link_collections_to_loans()
