# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import app, db, Customer, Loan
from datetime import datetime, timedelta
import random

def add_demo_loans():
    with app.app_context():
        print("Adding demo loans to customers...")
        
        customers = Customer.query.all()
        
        for customer in customers:
            # Add 1-2 loans per customer
            num_loans = random.randint(1, 2)
            
            for i in range(num_loans):
                loan_amount = random.choice([10000, 15000, 20000, 25000, 30000])
                interest_rate = 10.0
                installment_count = random.choice([20, 30, 40, 50])
                installment_amount = (loan_amount + (loan_amount * interest_rate / 100)) / installment_count
                
                loan_date = datetime.now() - timedelta(days=random.randint(30, 120))
                due_date = loan_date + timedelta(weeks=installment_count)
                
                loan = Loan(
                    customer_name=customer.name,
                    amount=loan_amount,
                    interest=interest_rate,
                    loan_date=loan_date,
                    due_date=due_date,
                    installment_count=installment_count,
                    installment_amount=installment_amount,
                    installment_type='Weekly',
                    service_charge=0,
                    staff_id=customer.staff_id,
                    status='Active'
                )
                db.session.add(loan)
                print(f"  Added loan for {customer.name}: Tk {loan_amount}")
        
        db.session.commit()
        print(f"\nTotal loans added: {Loan.query.count()}")
        print("Done!")

if __name__ == '__main__':
    add_demo_loans()
