# -*- coding: utf-8 -*-
"""
Migration script to add plain_password field to existing users
Run this once to update the database schema
"""

from app import app, db
from models.user_model import User

def add_plain_password_field():
    with app.app_context():
        try:
            # Create all tables (will add new column if not exists)
            db.create_all()
            
            # Update existing staff without plain_password
            staffs = User.query.filter_by(role='staff').all()
            updated = 0
            
            for staff in staffs:
                if not staff.plain_password:
                    # Set a default password that admin should change
                    staff.plain_password = 'staff123'
                    updated += 1
            
            db.session.commit()
            print(f"✅ Successfully added plain_password field!")
            print(f"📝 Updated {updated} staff records with default password 'staff123'")
            print(f"⚠️  Admin should update staff passwords from the Edit Staff page")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    add_plain_password_field()
