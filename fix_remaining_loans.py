# -*- coding: utf-8 -*-
"""
Fix customer.remaining_loan to match actual loan-wise collections
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models.customer_model import Customer
from models.loan_model import Loan
from models.loan_collection_model import LoanCollection

def fix_remaining_loans():
    with app.app_context():
        print("="*70)
        print("  Fixing customer.remaining_loan")
        print("="*70)
        
        customers = Customer.query.all()
        fixed_count = 0
        
        for customer in customers:
            print(f"\nCustomer: {customer.name} (ID: {customer.id})")
            print(f"  Current remaining_loan: {customer.remaining_loan:,.0f}")
            
            # Get all loans
            loans = Loan.query.filter_by(customer_name=customer.name).all()
            
            if not loans:
                if customer.remaining_loan != 0:
                    print(f"  No loans but remaining_loan = {customer.remaining_loan}")
                    print(f"  Setting to 0")
                    customer.remaining_loan = 0
                    customer.total_loan = 0
                    fixed_count += 1
                continue
            
            # Calculate actual remaining loan-wise
            total_with_interest = 0
            total_collected = 0
            
            for loan in loans:
                loan_with_interest = loan.amount + (loan.amount * loan.interest / 100)
                loan_collections = LoanCollection.query.filter_by(
                    customer_id=customer.id, 
                    loan_id=loan.id
                ).all()
                loan_collected = sum(lc.amount for lc in loan_collections)
                
                total_with_interest += loan_with_interest
                total_collected += loan_collected
            
            actual_remaining = total_with_interest - total_collected
            
            print(f"  Total with interest: {total_with_interest:,.0f}")
            print(f"  Total collected: {total_collected:,.0f}")
            print(f"  Actual remaining: {actual_remaining:,.0f}")
            
            if abs(customer.remaining_loan - actual_remaining) > 0.01:
                print(f"  FIXING: {customer.remaining_loan:,.0f} -> {actual_remaining:,.0f}")
                customer.remaining_loan = actual_remaining
                customer.total_loan = total_with_interest
                fixed_count += 1
            else:
                print(f"  Already correct")
        
        db.session.commit()
        
        print("\n" + "="*70)
        print(f"  Fixed {fixed_count} customers")
        print("="*70)

if __name__ == '__main__':
    fix_remaining_loans()
