import os
import sys

# Get DATABASE_URL from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable not set")
    print("Usage: set DATABASE_URL=postgresql://user:password@host/dbname")
    sys.exit(1)

os.environ['DATABASE_URL'] = DATABASE_URL

from app import app, db
from models import User, Customer, Loan, Saving, Collection, Investor, Investment, Withdrawal, Expense, ScheduledExpense, Note
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt(app)

with app.app_context():
    print("Creating tables...")
    db.create_all()
    
    # Create default admin if not exists
    if not User.query.filter_by(email='admin@example.com').first():
        admin = User(
            name='Admin',
            email='admin@example.com',
            password=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("✓ Admin user created")
    
    print("✓ Database setup complete!")
