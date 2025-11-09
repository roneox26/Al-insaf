import sys
import os

# IMPORTANT: Replace 'rone12' with your actual PythonAnywhere username
project_home = '/home/rone12/Al-insaf'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment variable
os.environ['FLASK_APP'] = 'app.py'

try:
    # Import Flask app
    from app import app as application
    
    # Initialize database
    from app import db, bcrypt, User, CashBalance
    
    with application.app_context():
        try:
            db.create_all()
            
            # Create default users if they don't exist
            if not User.query.filter_by(email='admin@example.com').first():
                hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
                admin = User(name='Admin', email='admin@example.com', password=hashed_pw, role='admin')
                db.session.add(admin)
            
            if not User.query.filter_by(email='office@example.com').first():
                hashed_pw = bcrypt.generate_password_hash('office123').decode('utf-8')
                office = User(name='Office Staff', email='office@example.com', password=hashed_pw, role='staff', is_office_staff=True)
                db.session.add(office)
            
            if not User.query.filter_by(email='staff@example.com').first():
                hashed_pw = bcrypt.generate_password_hash('staff123').decode('utf-8')
                staff = User(name='Field Staff', email='staff@example.com', password=hashed_pw, role='staff', is_office_staff=False)
                db.session.add(staff)
            
            db.session.commit()
            
            # Initialize cash balance
            if not CashBalance.query.first():
                initial_balance = CashBalance(balance=0)
                db.session.add(initial_balance)
                db.session.commit()
        except Exception as e:
            print(f"Database initialization error: {e}")
except Exception as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()
