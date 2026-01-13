import os
import sys

# Create instance directory if not exists
if not os.path.exists('instance'):
    os.makedirs('instance')
    print("Created instance directory")

# Delete old database only if using SQLite
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
    try:
        # Drop all tables first
        db.drop_all()
        print("Dropped all existing tables")
    except Exception as e:
        print(f"Note: {e}")
    
    # Create all tables
    db.create_all()
    print("Created all tables")
    
    # Check if admin already exists
    existing_admin = User.query.filter_by(email='admin@example.com').first()
    if not existing_admin:
        # Add admin
        admin = User(
            name='Admin',
            email='admin@example.com',
            password=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            role='admin',
            is_office_staff=False
        )
        db.session.add(admin)
        print("Added admin user")
    
    # Check if staff already exists
    existing_staff = User.query.filter_by(email='staff@example.com').first()
    if not existing_staff:
        # Add staff
        staff = User(
            name='Staff',
            email='staff@example.com',
            password=bcrypt.generate_password_hash('staff123').decode('utf-8'),
            role='staff',
            is_office_staff=False
        )
        db.session.add(staff)
        print("Added staff user")
    
    # Check if cash balance exists
    existing_cash = CashBalance.query.first()
    if not existing_cash:
        # Add cash balance
        cash = CashBalance(balance=0)
        db.session.add(cash)
        print("Added cash balance")
    
    db.session.commit()
    print("Database setup completed!")
    
print("\n✅ Database created successfully!")
print("\n🔐 Login credentials:")
print("  Admin: admin@example.com / admin123")
print("  Staff: staff@example.com / staff123")
print("\n🚀 Run: python run.py")
