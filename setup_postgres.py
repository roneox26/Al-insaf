import os
os.environ['DATABASE_URL'] = 'postgresql://ngoweb_db_user:REtACHujjdzbn0DspqewJgF4evtzHaDU@dpg-d43kkqgdl3ps73a1a430-a/ngoweb_db'

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
    print("URL: postgresql://dpg-d43kkqgdl3ps73a1a430-a")
