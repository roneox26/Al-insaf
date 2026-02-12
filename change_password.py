#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Change user password"""

from app import app, db, bcrypt, User

def change_password():
    print("=" * 50)
    print("Change User Password")
    print("=" * 50)
    
    email = input("\nEnter user email: ").strip()
    
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"\nError: User with email '{email}' not found!")
            return
        
        print(f"\nUser found: {user.name} ({user.role})")
        new_password = input("Enter new password: ").strip()
        
        if len(new_password) < 6:
            print("\nError: Password must be at least 6 characters!")
            return
        
        confirm_password = input("Confirm new password: ").strip()
        
        if new_password != confirm_password:
            print("\nError: Passwords do not match!")
            return
        
        # Update password
        user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        db.session.commit()
        
        print("\n" + "=" * 50)
        print("Password changed successfully!")
        print("=" * 50)
        print(f"\nUser: {user.name}")
        print(f"Email: {user.email}")

if __name__ == '__main__':
    try:
        change_password()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled.")
    except Exception as e:
        print(f"\nError: {e}")
