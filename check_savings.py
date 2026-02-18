# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import app, db, Customer, SavingCollection, Withdrawal

def check_savings():
    with app.app_context():
        customers = Customer.query.all()
        
        for customer in customers:
            print(f"\n{'='*60}")
            print(f"Customer: {customer.name} (ID: {customer.id})")
            print(f"{'='*60}")
            
            # Get savings collections
            savings = SavingCollection.query.filter_by(customer_id=customer.id).all()
            print(f"\nSavings Collections: {len(savings)}")
            total_savings = 0
            for s in savings:
                print(f"  {s.collection_date.strftime('%Y-%m-%d')}: Tk {s.amount}")
                total_savings += s.amount
            print(f"Total Savings Collected: Tk {total_savings}")
            
            # Get withdrawals
            withdrawals = Withdrawal.query.filter_by(customer_id=customer.id).all()
            print(f"\nWithdrawals: {len(withdrawals)}")
            total_withdrawn = 0
            for w in withdrawals:
                print(f"  {w.date.strftime('%Y-%m-%d')}: Tk {w.amount}")
                total_withdrawn += w.amount
            print(f"Total Withdrawn: Tk {total_withdrawn}")
            
            # Calculate balance
            actual_balance = total_savings - total_withdrawn
            print(f"\nCalculated Balance: Tk {actual_balance}")
            print(f"Customer.savings_balance: Tk {customer.savings_balance}")
            
            if actual_balance != customer.savings_balance:
                print(f"⚠️  MISMATCH! Difference: Tk {actual_balance - customer.savings_balance}")

if __name__ == '__main__':
    check_savings()
