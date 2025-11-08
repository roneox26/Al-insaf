from app import app, db
from models.user_model import User
from models.customer_model import Customer
from models.loan_model import Loan
from models.loan_collection_model import LoanCollection
from models.saving_collection_model import SavingCollection
from models.expense_model import Expense
from models.withdrawal_model import Withdrawal
from models.cash_balance_model import CashBalance
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

with app.app_context():
    # Drop all tables
    db.drop_all()
    
    # Recreate all tables
    db.create_all()
    
    # Add admin
    hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
    admin = User(name='Admin', email='admin@example.com', password=hashed_pw, role='admin')
    db.session.add(admin)
    
    # Add staff
    hashed_pw = bcrypt.generate_password_hash('staff123').decode('utf-8')
    staff = User(name='Staff', email='staff@example.com', password=hashed_pw, role='staff')
    db.session.add(staff)
    
    # Initialize cash balance
    initial_balance = CashBalance(balance=0)
    db.session.add(initial_balance)
    
    db.session.commit()
    
    print("Data cleared successfully!")
    print("Admin: admin@example.com / admin123")
    print("Staff: staff@example.com / staff123")
