#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Initialize database for Render deployment"""

from app import app, db, User, CashBalance, bcrypt

def init_render_db():
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        
        # Create default admin
        if not User.query.filter_by(email='admin@example.com').first():
            print("Creating admin user...")
            hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = User(name='Admin', email='admin@example.com', password=hashed_pw, role='admin')
            db.session.add(admin)
        
        # Create default staff
        if not User.query.filter_by(email='staff@example.com').first():
            print("Creating staff user...")
            hashed_pw = bcrypt.generate_password_hash('staff123').decode('utf-8')
            staff = User(name='Staff', email='staff@example.com', password=hashed_pw, role='staff')
            db.session.add(staff)
        
        db.session.commit()
        
        # Initialize cash balance
        if not CashBalance.query.first():
            print("Creating cash balance record...")
            initial_balance = CashBalance(balance=0)
            db.session.add(initial_balance)
            db.session.commit()
        
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_render_db()
