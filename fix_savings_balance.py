# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import app, db, Customer, SavingCollection, Withdrawal

def fix_savings_balance():
    with app.app_context():
        print("Fixing customer savings_balance...")
        
        customers = Customer.query.all()
        
        for customer in customers:
            # Calculate actual balance
            total_savings = sum(s.amount for s in SavingCollection.query.filter_by(customer_id=customer.id).all())
            total_withdrawn = sum(w.amount for w in Withdrawal.query.filter_by(customer_id=customer.id).all())
            actual_balance = total_savings - total_withdrawn
            
            old_balance = customer.savings_balance
            customer.savings_balance = actual_balance
            
            print(f"{customer.name}: {old_balance} -> {actual_balance}")
        
        db.session.commit()
        print("\nDone! All customer savings_balance updated.")

if __name__ == '__main__':
    fix_savings_balance()
