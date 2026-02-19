#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Deployment Health Check
Run this after deployment to check if everything is working
"""

import os
import sys

def check_deployment():
    print("=" * 60)
    print("DEPLOYMENT HEALTH CHECK")
    print("=" * 60)
    
    # Check 1: Python version
    print(f"\n✓ Python Version: {sys.version}")
    
    # Check 2: Environment variables
    print("\n📋 Environment Variables:")
    db_url = os.environ.get('DATABASE_URL', 'Not set')
    port = os.environ.get('PORT', '5000')
    flask_env = os.environ.get('FLASK_ENV', 'Not set')
    
    print(f"  - DATABASE_URL: {'Set ✓' if db_url != 'Not set' else 'Not set ✗'}")
    print(f"  - PORT: {port}")
    print(f"  - FLASK_ENV: {flask_env}")
    
    # Check 3: Database connection
    print("\n🗄️  Database Check:")
    try:
        from flask import Flask
        from models.user_model import db, User
        
        app = Flask(__name__)
        
        # Fix postgres:// to postgresql://
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
        
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        
        with app.app_context():
            # Try to query users
            user_count = User.query.count()
            print(f"  ✓ Database connected!")
            print(f"  ✓ Users in database: {user_count}")
            
            # Check if admin exists
            admin = User.query.filter_by(email='admin@example.com').first()
            if admin:
                print(f"  ✓ Admin user exists")
            else:
                print(f"  ✗ Admin user NOT found - creating...")
                from flask_bcrypt import Bcrypt
                bcrypt = Bcrypt(app)
                hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
                admin = User(name='Admin', email='admin@example.com', password=hashed_pw, role='admin')
                db.session.add(admin)
                db.session.commit()
                print(f"  ✓ Admin user created!")
                
    except Exception as e:
        print(f"  ✗ Database error: {str(e)}")
        return False
    
    # Check 4: Templates
    print("\n📄 Template Check:")
    if os.path.exists('templates/login.html'):
        print("  ✓ login.html exists")
    else:
        print("  ✗ login.html NOT found")
        return False
    
    # Check 5: Static files
    print("\n🎨 Static Files Check:")
    static_path = 'static'
    if os.path.exists(static_path):
        print(f"  ✓ static folder exists")
    else:
        print(f"  ✗ static folder NOT found")
    
    print("\n" + "=" * 60)
    print("✅ DEPLOYMENT CHECK COMPLETE!")
    print("=" * 60)
    print("\nYou can now access your application at:")
    print(f"http://localhost:{port}")
    print("\nDefault login:")
    print("  Email: admin@example.com")
    print("  Password: admin123")
    
    return True

if __name__ == '__main__':
    try:
        check_deployment()
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
