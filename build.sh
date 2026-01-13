#!/usr/bin/env bash
# exit on error
set -o errexit

echo "=== Starting Build Process ==="

echo "Step 1: Upgrading pip..."
pip install --upgrade pip

echo "Step 2: Installing dependencies..."
pip install -r requirements.txt

echo "Step 3: Creating instance directory..."
mkdir -p instance

echo "Step 4: Setting up database..."
python -c "
from app import app, db
with app.app_context():
    print('Creating database tables...')
    db.create_all()
    print('Database tables created successfully!')
"

echo "Step 5: Creating default users..."
python -c "
from app import app, db, bcrypt, User, CashBalance
with app.app_context():
    # Check and create admin
    if not User.query.filter_by(email='admin@example.com').first():
        admin = User(
            name='Admin',
            email='admin@example.com',
            password=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            role='admin',
            is_office_staff=False
        )
        db.session.add(admin)
        print('Created admin user')
    
    # Check and create staff
    if not User.query.filter_by(email='staff@example.com').first():
        staff = User(
            name='Staff',
            email='staff@example.com',
            password=bcrypt.generate_password_hash('staff123').decode('utf-8'),
            role='staff',
            is_office_staff=False
        )
        db.session.add(staff)
        print('Created staff user')
    
    # Check and create cash balance
    if not CashBalance.query.first():
        cash = CashBalance(balance=0)
        db.session.add(cash)
        print('Created cash balance')
    
    db.session.commit()
    print('Default data setup completed!')
"

echo "=== Build Completed Successfully! ==="
