import os
from app import app, db
from flask_bcrypt import Bcrypt
from models.user_model import User
from models.cash_balance_model import CashBalance

bcrypt = Bcrypt()

# Delete old database
db_path = 'instance/loan.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print("Old database deleted")

with app.app_context():
    db.create_all()
    print("New database created with investor system")
    
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
    print("Setup complete!")
    print("Login: admin@example.com / admin123")
