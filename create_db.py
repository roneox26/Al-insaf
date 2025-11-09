import os
import sys

# Delete old database
db_path = 'instance/loan.db'
if os.path.exists(db_path):
    try:
        os.remove(db_path)
        print(f"Deleted old database: {db_path}")
    except PermissionError:
        print("ERROR: Database is locked. Close all applications and try again.")
        sys.exit(1)

# Create new database
from app import app, db, bcrypt, User, CashBalance

with app.app_context():
    db.create_all()
    print("Created all tables")
    
    # Add admin
    admin = User(
        name='Admin',
        email='admin@example.com',
        password=bcrypt.generate_password_hash('admin123').decode('utf-8'),
        role='admin',
        is_office_staff=False
    )
    db.session.add(admin)
    
    # Add staff
    staff = User(
        name='Staff',
        email='staff@example.com',
        password=bcrypt.generate_password_hash('staff123').decode('utf-8'),
        role='staff',
        is_office_staff=False
    )
    db.session.add(staff)
    
    # Add cash balance
    cash = CashBalance(balance=0)
    db.session.add(cash)
    
    db.session.commit()
    print("Added default users and cash balance")
    
print("\nDatabase created successfully!")
print("\nLogin credentials:")
print("  Admin: admin@example.com / admin123")
print("  Staff: staff@example.com / staff123")
print("\nRun: python run.py")
