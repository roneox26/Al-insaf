#!/usr/bin/env bash
set -o errexit

echo "=== Build Started ==="

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Creating instance directory..."
mkdir -p instance

echo "Initializing database..."
python << 'PYTHON_SCRIPT'
import sys
sys.path.insert(0, '.')

try:
    from app import app, db, bcrypt, User, CashBalance
    
    with app.app_context():
        print("Creating tables...")
        db.create_all()
        print("Tables created!")
        
        if not User.query.filter_by(email='admin@example.com').first():
            admin = User(
                name='Admin',
                email='admin@example.com',
                password=bcrypt.generate_password_hash('admin123').decode('utf-8'),
                role='admin',
                is_office_staff=False
            )
            db.session.add(admin)
            print("Admin created")
        
        if not User.query.filter_by(email='staff@example.com').first():
            staff = User(
                name='Staff',
                email='staff@example.com',
                password=bcrypt.generate_password_hash('staff123').decode('utf-8'),
                role='staff',
                is_office_staff=False
            )
            db.session.add(staff)
            print("Staff created")
        
        if not CashBalance.query.first():
            cash = CashBalance(balance=0)
            db.session.add(cash)
            print("Cash balance created")
        
        db.session.commit()
        print("Database setup complete!")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYTHON_SCRIPT

echo "=== Build Complete ==="
