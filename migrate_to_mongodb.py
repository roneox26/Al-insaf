"""
SQLite থেকে MongoDB তে Data Migration Script
"""
import sys
from flask import Flask
from flask_mongoengine import MongoEngine
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# SQLite Configuration
app_sqlite = Flask(__name__)
app_sqlite.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/loan.db'
app_sqlite.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db_sqlite = SQLAlchemy(app_sqlite)

# MongoDB Configuration
app_mongo = Flask(__name__)
app_mongo.config['MONGODB_SETTINGS'] = {
    'host': 'mongodb://localhost:27017/ngo_db'
}
db_mongo = MongoEngine(app_mongo)

# Import SQLite Models
from models.user_model import User as SQLiteUser
from models.customer_model import Customer as SQLiteCustomer
from models.loan_model import Loan as SQLiteLoan, LoanCollection as SQLiteLoanCollection
from models.saving_model import Saving as SQLiteSaving, SavingCollection as SQLiteSavingCollection
from models.cash_balance_model import CashBalance as SQLiteCashBalance
from models.investor_model import Investor as SQLiteInvestor
from models.investment_model import Investment as SQLiteInvestment
from models.expense_model import Expense as SQLiteExpense
from models.withdrawal_model import Withdrawal as SQLiteWithdrawal

# Import MongoDB Models
from models_mongodb.user_model import User as MongoUser
from models_mongodb.customer_model import Customer as MongoCustomer
from models_mongodb.loan_model import Loan as MongoLoan, LoanCollection as MongoLoanCollection
from models_mongodb.saving_model import Saving as MongoSaving, SavingCollection as MongoSavingCollection
from models_mongodb.other_models import (
    CashBalance as MongoCashBalance,
    Investor as MongoInvestor,
    Investment as MongoInvestment,
    Expense as MongoExpense,
    Withdrawal as MongoWithdrawal
)

def migrate_users():
    print("Migrating Users...")
    with app_sqlite.app_context():
        users = SQLiteUser.query.all()
        user_map = {}
        
        for user in users:
            mongo_user = MongoUser(
                name=user.name,
                email=user.email,
                password=user.password,
                role=user.role,
                is_office_staff=user.is_office_staff,
                is_monitor=user.is_monitor,
                phone=user.phone,
                address=user.address,
                photo=user.photo,
                join_date=user.join_date,
                salary=user.salary,
                status=user.status,
                nid=user.nid,
                plain_password=user.plain_password
            )
            mongo_user.save()
            user_map[user.id] = mongo_user
            print(f"✓ Migrated user: {user.name}")
    
    return user_map

def migrate_customers(user_map):
    print("\nMigrating Customers...")
    with app_sqlite.app_context():
        customers = SQLiteCustomer.query.all()
        customer_map = {}
        
        for customer in customers:
            mongo_customer = MongoCustomer(
                name=customer.name,
                member_no=customer.member_no,
                phone=customer.phone,
                father_husband=customer.father_husband,
                village=customer.village,
                post=customer.post,
                thana=customer.thana,
                district=customer.district,
                granter=customer.granter,
                profession=customer.profession,
                nid_no=customer.nid_no,
                admission_fee=customer.admission_fee,
                welfare_fee=customer.welfare_fee,
                application_fee=customer.application_fee,
                address=customer.address,
                photo=customer.photo,
                staff_id=user_map.get(customer.staff_id),
                total_loan=customer.total_loan,
                remaining_loan=customer.remaining_loan,
                savings_balance=customer.savings_balance,
                created_date=customer.created_date,
                is_active=customer.is_active
            )
            mongo_customer.save()
            customer_map[customer.id] = mongo_customer
            print(f"✓ Migrated customer: {customer.name}")
    
    return customer_map

def migrate_loans(customer_map):
    print("\nMigrating Loans...")
    with app_sqlite.app_context():
        loans = SQLiteLoan.query.all()
        loan_map = {}
        
        for loan in loans:
            mongo_loan = MongoLoan(
                customer_id=customer_map.get(loan.customer_id),
                amount=loan.amount,
                interest_rate=loan.interest_rate,
                duration_months=loan.duration_months,
                installment_amount=loan.installment_amount,
                remaining_amount=loan.remaining_amount,
                loan_date=loan.loan_date,
                status=loan.status
            )
            mongo_loan.save()
            loan_map[loan.id] = mongo_loan
            print(f"✓ Migrated loan: ৳{loan.amount}")
    
    return loan_map

def migrate_loan_collections(customer_map, user_map, loan_map):
    print("\nMigrating Loan Collections...")
    with app_sqlite.app_context():
        collections = SQLiteLoanCollection.query.all()
        
        for collection in collections:
            mongo_collection = MongoLoanCollection(
                customer_id=customer_map.get(collection.customer_id),
                loan_id=loan_map.get(collection.loan_id) if hasattr(collection, 'loan_id') else None,
                staff_id=user_map.get(collection.staff_id),
                amount=collection.amount,
                collection_date=collection.collection_date
            )
            mongo_collection.save()
            print(f"✓ Migrated loan collection: ৳{collection.amount}")

def migrate_savings(customer_map):
    print("\nMigrating Savings...")
    with app_sqlite.app_context():
        savings = SQLiteSaving.query.all()
        
        for saving in savings:
            mongo_saving = MongoSaving(
                customer_id=customer_map.get(saving.customer_id),
                amount=saving.amount,
                saving_date=saving.saving_date
            )
            mongo_saving.save()
            print(f"✓ Migrated saving: ৳{saving.amount}")

def migrate_saving_collections(customer_map, user_map):
    print("\nMigrating Saving Collections...")
    with app_sqlite.app_context():
        collections = SQLiteSavingCollection.query.all()
        
        for collection in collections:
            mongo_collection = MongoSavingCollection(
                customer_id=customer_map.get(collection.customer_id),
                staff_id=user_map.get(collection.staff_id),
                amount=collection.amount,
                collection_date=collection.collection_date
            )
            mongo_collection.save()
            print(f"✓ Migrated saving collection: ৳{collection.amount}")

def migrate_cash_balance():
    print("\nMigrating Cash Balance...")
    with app_sqlite.app_context():
        cash_balance = SQLiteCashBalance.query.first()
        if cash_balance:
            mongo_cash = MongoCashBalance(
                balance=cash_balance.balance,
                last_updated=cash_balance.last_updated
            )
            mongo_cash.save()
            print(f"✓ Migrated cash balance: ৳{cash_balance.balance}")

def migrate_investors():
    print("\nMigrating Investors...")
    with app_sqlite.app_context():
        investors = SQLiteInvestor.query.all()
        investor_map = {}
        
        for investor in investors:
            mongo_investor = MongoInvestor(
                name=investor.name,
                phone=investor.phone,
                address=investor.address,
                total_investment=investor.total_investment,
                created_date=investor.created_date
            )
            mongo_investor.save()
            investor_map[investor.id] = mongo_investor
            print(f"✓ Migrated investor: {investor.name}")
    
    return investor_map

def migrate_investments(investor_map):
    print("\nMigrating Investments...")
    with app_sqlite.app_context():
        investments = SQLiteInvestment.query.all()
        
        for investment in investments:
            mongo_investment = MongoInvestment(
                investor_id=investor_map.get(investment.investor_id),
                amount=investment.amount,
                investment_date=investment.investment_date
            )
            mongo_investment.save()
            print(f"✓ Migrated investment: ৳{investment.amount}")

def migrate_expenses(user_map):
    print("\nMigrating Expenses...")
    with app_sqlite.app_context():
        expenses = SQLiteExpense.query.all()
        
        for expense in expenses:
            mongo_expense = MongoExpense(
                title=expense.title,
                amount=expense.amount,
                category=expense.category,
                expense_date=expense.expense_date,
                created_by=user_map.get(expense.created_by) if hasattr(expense, 'created_by') else None
            )
            mongo_expense.save()
            print(f"✓ Migrated expense: {expense.title}")

def migrate_withdrawals(customer_map, user_map):
    print("\nMigrating Withdrawals...")
    with app_sqlite.app_context():
        withdrawals = SQLiteWithdrawal.query.all()
        
        for withdrawal in withdrawals:
            mongo_withdrawal = MongoWithdrawal(
                customer_id=customer_map.get(withdrawal.customer_id),
                amount=withdrawal.amount,
                withdrawal_date=withdrawal.withdrawal_date,
                approved_by=user_map.get(withdrawal.approved_by) if hasattr(withdrawal, 'approved_by') else None
            )
            mongo_withdrawal.save()
            print(f"✓ Migrated withdrawal: ৳{withdrawal.amount}")

def main():
    print("=" * 60)
    print("SQLite থেকে MongoDB তে Data Migration শুরু হচ্ছে...")
    print("=" * 60)
    
    try:
        user_map = migrate_users()
        customer_map = migrate_customers(user_map)
        loan_map = migrate_loans(customer_map)
        migrate_loan_collections(customer_map, user_map, loan_map)
        migrate_savings(customer_map)
        migrate_saving_collections(customer_map, user_map)
        migrate_cash_balance()
        investor_map = migrate_investors()
        migrate_investments(investor_map)
        migrate_expenses(user_map)
        migrate_withdrawals(customer_map, user_map)
        
        print("\n" + "=" * 60)
        print("✅ Migration সফলভাবে সম্পন্ন হয়েছে!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
