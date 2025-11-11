#!/usr/bin/env python
"""Test script to check if app runs correctly"""

try:
    print("Testing imports...")
    from app import app
    print("✅ App imported successfully!")
    
    print("\nTesting app context...")
    with app.app_context():
        from models.user_model import db, User
        print("✅ Database models loaded!")
        
    print("\nTesting routes...")
    print(f"✅ Total routes: {len(app.url_map._rules)}")
    
    print("\n✅ All tests passed! App is ready to run.")
    print("\nTo start the app:")
    print("  python app.py")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("\nFix: Install missing dependencies")
    print("  pip install -r requirements.txt")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nCheck the error message above and fix the issue.")
