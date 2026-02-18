# -*- coding: utf-8 -*-
"""
Check data consistency between customer.remaining_loan and actual collections
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

def check_data_consistency():
    with app.app_context():
        from models.customer_model import Customer
        from models.loan_model import Loan
        from models.loan_collection_model import LoanCollection
        
        print("="*70)
        print("  Data Consistency Check")
        print("="*70)
        
        customers = Customer.query.all()
        
        for customer in customers:
            print(f"\nCustomer: {customer.name} (ID: {customer.id})")
            print(f"  Database remaining_loan: ৳{customer.remaining_loan:,.0f}")
            
            # Get all loans
            loans = Loan.query.filter_by(customer_name=customer.name).all()
            
            if not loans:
                print(f"  No loans found")
                continue
            
            # Calculate actual remaining
            total_with_interest = 0
            total_collected = 0
            
            for loan in loans:
                loan_with_interest = loan.amount + (loan.amount * loan.interest / 100)
                loan_collections = LoanCollection.query.filter_by(customer_id=customer.id, loan_id=loan.id).all()
                loan_collected = sum(lc.amount for lc in loan_collections)
                
                total_with_interest += loan_with_interest
                total_collected += loan_collected
                
                print(f"  Loan #{loan.id}: ৳{loan.amount:,.0f} + {loan.interest}% = ৳{loan_with_interest:,.0f}")
                print(f"    Collected: ৳{loan_collected:,.0f}, Remaining: ৳{loan_with_interest - loan_collected:,.0f}")
            
            actual_remaining = total_with_interest - total_collected
            
            print(f"\n  Total with interest: ৳{total_with_interest:,.0f}")
            print(f"  Total collected: ৳{total_collected:,.0f}")
            print(f"  Actual remaining: ৳{actual_remaining:,.0f}")
            
            if abs(customer.remaining_loan - actual_remaining) > 0.01:
                print(f"  ⚠️  MISMATCH! Difference: ৳{customer.remaining_loan - actual_remaining:,.0f}")
            else:
                print(f"  ✓ Data is consistent")
        
        print("\n" + "="*70)

if __name__ == '__main__':
    check_data_consistency()
