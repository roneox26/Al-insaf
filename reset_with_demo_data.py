# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from app import app, db, User, Customer, LoanCollection, SavingCollection, Withdrawal, Investor, Investment, Expense, CashBalance, bcrypt
from datetime import datetime, timedelta
import random

def reset_database():
    with app.app_context():
        print("Deleting old data...")
        db.drop_all()
        
        print("Creating new database...")
        db.create_all()
        
        print("Creating users...")
        admin = User(
            name='Admin User',
            email='admin@example.com',
            password=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            role='admin'
        )
        
        office_staff = User(
            name='Office Staff',
            email='office@example.com',
            password=bcrypt.generate_password_hash('office123').decode('utf-8'),
            role='office_staff'
        )
        
        field_staff1 = User(
            name='Karim Mia',
            email='karim@example.com',
            password=bcrypt.generate_password_hash('staff123').decode('utf-8'),
            role='field_staff'
        )
        
        field_staff2 = User(
            name='Rahim Uddin',
            email='rahim@example.com',
            password=bcrypt.generate_password_hash('staff123').decode('utf-8'),
            role='field_staff'
        )
        
        monitor = User(
            name='Monitor Staff',
            email='monitor@example.com',
            password=bcrypt.generate_password_hash('monitor123').decode('utf-8'),
            role='monitor'
        )
        
        db.session.add_all([admin, office_staff, field_staff1, field_staff2, monitor])
        db.session.commit()
        
        print("Creating cash balance...")
        cash_balance = CashBalance(balance=50000.0)
        db.session.add(cash_balance)
        db.session.commit()
        
        print("Creating investors...")
        investors_data = [
            {'name': 'Abdul Karim', 'phone': '01711111111', 'amount': 100000.0},
            {'name': 'Rahim Uddin', 'phone': '01722222222', 'amount': 150000.0},
            {'name': 'Salma Begum', 'phone': '01733333333', 'amount': 75000.0},
        ]
        
        investor_counter = 1
        for inv_data in investors_data:
            investor = Investor(
                investor_id=f'INV{investor_counter:03d}',
                name=inv_data['name'],
                phone=inv_data['phone'],
                total_investment=inv_data['amount'],
                current_balance=inv_data['amount'],
                created_date=datetime.now() - timedelta(days=random.randint(30, 90))
            )
            db.session.add(investor)
            db.session.flush()
            
            investment = Investment(
                investor_id=investor.id,
                investor_name=inv_data['name'],
                amount=inv_data['amount'],
                date=investor.created_date
            )
            db.session.add(investment)
            investor_counter += 1
        
        db.session.commit()
        
        print("Creating customers...")
        customers_data = [
            {'name': 'Hasina Begum', 'phone': '01811111111', 'village': 'East Para', 'member_no': 'M001', 'staff': field_staff1},
            {'name': 'Amina Khatun', 'phone': '01822222222', 'village': 'West Para', 'member_no': 'M002', 'staff': field_staff1},
            {'name': 'Rokeya Begum', 'phone': '01833333333', 'village': 'North Para', 'member_no': 'M003', 'staff': field_staff1},
            {'name': 'Jorina Khatun', 'phone': '01844444444', 'village': 'South Para', 'member_no': 'M004', 'staff': field_staff2},
            {'name': 'Sabina Akter', 'phone': '01855555555', 'village': 'Middle Para', 'member_no': 'M005', 'staff': field_staff2},
            {'name': 'Nasima Begum', 'phone': '01866666666', 'village': 'East Para', 'member_no': 'M006', 'staff': field_staff2},
            {'name': 'Fatema Khatun', 'phone': '01877777777', 'village': 'West Para', 'member_no': 'M007', 'staff': field_staff1},
            {'name': 'Rabeya Begum', 'phone': '01888888888', 'village': 'North Para', 'member_no': 'M008', 'staff': field_staff2},
        ]
        
        customers = []
        for cust_data in customers_data:
            loan_amount = random.choice([10000, 15000, 20000, 25000, 30000])
            savings = random.randint(500, 2000)
            
            customer = Customer(
                name=cust_data['name'],
                phone=cust_data['phone'],
                village=cust_data['village'],
                address=f"{cust_data['village']}, Dhaka",
                member_no=cust_data['member_no'],
                staff_id=cust_data['staff'].id,
                total_loan=loan_amount,
                remaining_loan=loan_amount * 0.7,
                savings_balance=savings,
                created_date=datetime.now() - timedelta(days=random.randint(60, 180))
            )
            customers.append(customer)
            db.session.add(customer)
        
        db.session.commit()
        
        print("Creating loan collections...")
        for customer in customers:
            num_collections = random.randint(10, 20)
            for i in range(num_collections):
                collection = LoanCollection(
                    customer_id=customer.id,
                    amount=random.choice([200, 300, 400, 500]),
                    staff_id=customer.staff_id,
                    collection_date=datetime.now() - timedelta(days=random.randint(1, 30))
                )
                db.session.add(collection)
        
        db.session.commit()
        
        print("Creating saving collections...")
        for customer in customers:
            num_savings = random.randint(5, 10)
            for i in range(num_savings):
                saving = SavingCollection(
                    customer_id=customer.id,
                    amount=random.choice([50, 100, 150, 200]),
                    staff_id=customer.staff_id,
                    collection_date=datetime.now() - timedelta(days=random.randint(1, 30))
                )
                db.session.add(saving)
        
        db.session.commit()
        
        print("Creating withdrawals...")
        for i in range(3):
            customer = random.choice(customers)
            withdrawal = Withdrawal(
                customer_id=customer.id,
                amount=random.choice([500, 1000, 1500]),
                date=datetime.now() - timedelta(days=random.randint(1, 20)),
                withdrawal_type='savings'
            )
            db.session.add(withdrawal)
        
        db.session.commit()
        
        print("Creating expenses...")
        expenses_data = [
            {'category': 'Office', 'description': 'Office Rent', 'amount': 5000},
            {'category': 'Office', 'description': 'Electricity Bill', 'amount': 1200},
            {'category': 'Office', 'description': 'Stationery', 'amount': 800},
            {'category': 'Transport', 'description': 'Transport Cost', 'amount': 1500},
            {'category': 'Other', 'description': 'Mobile Bill', 'amount': 600},
        ]
        
        for exp_data in expenses_data:
            expense = Expense(
                category=exp_data['category'],
                description=exp_data['description'],
                amount=exp_data['amount'],
                date=datetime.now() - timedelta(days=random.randint(1, 15))
            )
            db.session.add(expense)
        
        db.session.commit()
        
        print("\n=== Demo data created successfully! ===")
        print("\nSummary:")
        print(f"   Users: {User.query.count()}")
        print(f"   Customers: {Customer.query.count()}")
        print(f"   Investors: {Investor.query.count()}")
        print(f"   Loan Collections: {LoanCollection.query.count()}")
        print(f"   Saving Collections: {SavingCollection.query.count()}")
        print(f"   Withdrawals: {Withdrawal.query.count()}")
        print(f"   Expenses: {Expense.query.count()}")
        print(f"   Cash Balance: Tk {CashBalance.query.first().balance:,.2f}")
        
        print("\nLogin Credentials:")
        print("   Admin: admin@example.com / admin123")
        print("   Office Staff: office@example.com / office123")
        print("   Field Staff 1: karim@example.com / staff123")
        print("   Field Staff 2: rahim@example.com / staff123")
        print("   Monitor: monitor@example.com / monitor123")

if __name__ == '__main__':
    reset_database()
