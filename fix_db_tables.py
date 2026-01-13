"""
Fix Database - Creates tables without deleting existing data
"""
from app import app, db

with app.app_context():
    try:
        print("Creating/updating database tables...")
        db.create_all()
        print("✅ Database tables created/updated successfully!")
        print("\n🚀 You can now run: python run.py")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Try:")
        print("1. Close the application if running")
        print("2. Run this script again")
