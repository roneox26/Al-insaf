# -*- coding: utf-8 -*-
"""
পুরাতন Data Import করার Script
এই script দিয়ে আপনি পুরাতন customer, loan, collection data add করতে পারবেন
"""

from app import app, db
from models.customer_model import Customer
from models.loan_model import Loan
from models.loan_collection_model import LoanCollection
from models.saving_collection_model import SavingCollection
from models.cash_balance_model import CashBalance
from models.user_model import User
from datetime import datetime
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

def add_old_customer(name, phone, member_no=None, staff_id=1, village='', address='', 
                     total_loan=0, remaining_loan=0, savings_balance=0, created_date=None):
    """পুরাতন customer add করুন"""
    with app.app_context():
        customer = Customer(
            name=name,
            phone=phone,
            member_no=member_no,
            staff_id=staff_id,
            village=village,
            address=address,
            total_loan=total_loan,
            remaining_loan=remaining_loan,
            savings_balance=savings_balance,
            created_date=created_date or datetime.now()
        )
        db.session.add(customer)
        db.session.commit()
        print(f"✅ Customer added: {name} (ID: {customer.id})")
        return customer.id

def add_old_loan(customer_id, amount, interest=10, loan_date=None, installment_count=0, 
                 installment_amount=0, installment_type='Weekly', staff_id=1):
    """পুরাতন loan add করুন"""
    with app.app_context():
        customer = Customer.query.get(customer_id)
        if not customer:
            print(f"❌ Customer ID {customer_id} not found!")
            return None
        
        loan_date = loan_date or datetime.now()
        from datetime import timedelta
        due_date = loan_date + timedelta(days=installment_count * 7) if installment_type == 'Weekly' else loan_date + timedelta(days=30)
        
        loan = Loan(
            customer_name=customer.name,
            amount=amount,
            interest=interest,
            loan_date=loan_date,
            due_date=due_date,
            installment_count=installment_count,
            installment_amount=installment_amount,
            installment_type=installment_type,
            staff_id=staff_id
        )
        db.session.add(loan)
        db.session.commit()
        print(f"✅ Loan added: ৳{amount} for {customer.name}")
        return loan.id

def add_old_collection(customer_id, loan_amount=0, saving_amount=0, collection_date=None, staff_id=1):
    """পুরাতন collection add করুন"""
    with app.app_context():
        customer = Customer.query.get(customer_id)
        if not customer:
            print(f"❌ Customer ID {customer_id} not found!")
            return
        
        collection_date = collection_date or datetime.now()
        
        if loan_amount > 0:
            loan_col = LoanCollection(
                customer_id=customer_id,
                amount=loan_amount,
                staff_id=staff_id,
                collection_date=collection_date
            )
            db.session.add(loan_col)
        
        if saving_amount > 0:
            saving_col = SavingCollection(
                customer_id=customer_id,
                amount=saving_amount,
                staff_id=staff_id,
                collection_date=collection_date
            )
            db.session.add(saving_col)
        
        db.session.commit()
        print(f"✅ Collection added: Loan ৳{loan_amount}, Saving ৳{saving_amount} for {customer.name}")

def import_from_csv(csv_file_path):
    """CSV file থেকে data import করুন"""
    import csv
    with app.app_context():
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    customer_id = add_old_customer(
                        name=row['name'],
                        phone=row.get('phone', ''),
                        member_no=row.get('member_no', ''),
                        village=row.get('village', ''),
                        total_loan=float(row.get('total_loan', 0)),
                        remaining_loan=float(row.get('remaining_loan', 0)),
                        savings_balance=float(row.get('savings_balance', 0))
                    )
                    print(f"✅ Imported: {row['name']}")
                except Exception as e:
                    print(f"❌ Error importing {row.get('name', 'Unknown')}: {e}")

# ============ Example Usage ============

if __name__ == '__main__':
    print("🔄 Starting Old Data Import...")
    print("=" * 50)
    
    # Example 1: Add a single customer with old data
    # customer_id = add_old_customer(
    #     name="রহিম উদ্দিন",
    #     phone="01712345678",
    #     member_no="M001",
    #     village="গ্রাম নাম",
    #     total_loan=50000,
    #     remaining_loan=30000,
    #     savings_balance=5000,
    #     created_date=datetime(2023, 1, 15)  # পুরাতন তারিখ
    # )
    
    # Example 2: Add old loan for that customer
    # add_old_loan(
    #     customer_id=customer_id,
    #     amount=50000,
    #     interest=10,
    #     loan_date=datetime(2023, 1, 20),
    #     installment_count=50,
    #     installment_amount=1100,
    #     installment_type='Weekly'
    # )
    
    # Example 3: Add old collections
    # add_old_collection(
    #     customer_id=customer_id,
    #     loan_amount=1100,
    #     saving_amount=100,
    #     collection_date=datetime(2023, 1, 27)
    # )
    
    # Example 4: Import from CSV
    # import_from_csv('old_customers.csv')
    
    print("=" * 50)
    print("✅ Import Complete!")
    print("\nNote: Uncomment the examples above and modify as needed")
