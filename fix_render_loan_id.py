# -*- coding: utf-8 -*-
"""
Quick fix for Render.com PostgreSQL deployment
Adds missing loan_id column to loan_collections table
"""
import os
from app import app, db
from sqlalchemy import text

def fix_render_database():
    """Fix database for Render.com deployment"""
    with app.app_context():
        try:
            print("🔧 Starting Render.com database fix...")
            
            # Check if we're on Render (has DATABASE_URL)
            if 'DATABASE_URL' in os.environ:
                print("✅ Detected Render.com environment")
            else:
                print("⚠️  Not on Render.com, but proceeding anyway...")
            
            # Check if column exists
            try:
                result = db.session.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='loan_collections' AND column_name='loan_id'
                """))
                
                if result.fetchone():
                    print("✅ loan_id column already exists!")
                    return True
                    
            except Exception as check_error:
                print(f"Could not check column existence: {check_error}")
            
            # Add the missing column
            print("➕ Adding loan_id column...")
            db.session.execute(text("ALTER TABLE loan_collections ADD COLUMN loan_id INTEGER"))
            
            # Update existing records with default loan_id
            print("🔄 Updating existing records...")
            db.session.execute(text("UPDATE loan_collections SET loan_id = 1 WHERE loan_id IS NULL"))
            
            db.session.commit()
            
            print("✅ SUCCESS! Database fixed successfully!")
            print("✅ loan_id column added to loan_collections table")
            print("✅ Individual Loan Sheets will now work properly")
            print("✅ Please restart your Render.com application")
            
            return True
            
        except Exception as e:
            print(f"❌ Fix failed: {e}")
            print("\n🔧 Manual fix instructions for Render.com:")
            print("1. Go to your Render.com dashboard")
            print("2. Open your service")
            print("3. Go to 'Shell' tab")
            print("4. Run: python migrate_add_loan_id_universal.py")
            print("5. Restart your application")
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = fix_render_database()
    if success:
        print("\n🎉 Fix completed successfully!")
    else:
        print("\n❌ Fix failed. Please try manual steps.")