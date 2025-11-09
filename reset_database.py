#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Reset and recreate database"""

import os
from app import app, db
from models.user_model import User
from models.customer_model import Customer
from models.loan_model import Loan
from models.saving_model import Saving
from models.loan_collection_model import LoanCollection
from models.saving_collection_model import SavingCollection
from models.cash_balance_model import CashBalance
from models.investor_model import Investor
from models.investment_model import Investment
from models.withdrawal_model import Withdrawal
from models.expense_model import Expense
from models.message_model import Message
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

# Delete old database
db_path = 'instance/loan.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"✓ Deleted old database: {db_path}")

# Create all tables
with app.app_context():
    db.create_all()
    print("✓ Created all database tables")
    
    # Add admin user
    admin = User(
        name='Admin',
        email='admin@example.com',
        password=bcrypt.generate_password_hash('admin123').decode('utf-8'),
        role='admin'
    )
    db.session.add(admin)
    
    # Add staff user
    staff = User(
        name='Staff',
        email='staff@example.com',
        password=bcrypt.generate_password_hash('staff123').decode('utf-8'),
        role='staff'
    )
    db.session.add(staff)
    
    # Initialize cash balance
    cash_balance = CashBalance(balance=0)
    db.session.add(cash_balance)
    
    db.session.commit()
    print("✓ Added default users (admin & staff)")
    print("✓ Initialized cash balance")
    
print("\n" + "="*50)
print("Database reset complete!")
print("="*50)
print("\nLogin credentials:")
print("  Admin: admin@example.com / admin123")
print("  Staff: staff@example.com / staff123")
print("\nRun the application:")
print("  python run.py")
