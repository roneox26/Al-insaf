#!/usr/bin/env python
"""
Complete Database Fix Script for Render.com
Run this in Render Shell: python render_fix.py
"""

def fix_database():
    print("=" * 60)
    print("🔧 Al-Insaf Database Fix Script")
    print("=" * 60)
    
    try:
        from app import app, db
        from sqlalchemy import text, inspect
        
        with app.app_context():
            print("\n✅ Connected to database")
            
            # Check if loan_id column exists
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('loan_collections')]
            
            print(f"\n📋 Current columns in loan_collections: {', '.join(columns)}")
            
            if 'loan_id' in columns:
                print("\n✅ loan_id column already exists!")
                print("✅ Database is ready!")
                return True
            
            print("\n🔧 Adding loan_id column...")
            
            # Add the column
            try:
                db.session.execute(text("ALTER TABLE loan_collections ADD COLUMN loan_id INTEGER"))
                db.session.commit()
                print("✅ loan_id column added successfully!")
            except Exception as e:
                print(f"⚠️  Column add error (may already exist): {e}")
                db.session.rollback()
            
            # Link existing collections to loans
            print("\n🔗 Linking existing collections to loans...")
            
            result = db.session.execute(text("""
                UPDATE loan_collections lc
                SET loan_id = (
                    SELECT l.id 
                    FROM loans l
                    JOIN customers c ON c.name = l.customer_name
                    WHERE c.id = lc.customer_id
                    LIMIT 1
                )
                WHERE loan_id IS NULL
            """))
            
            db.session.commit()
            print(f"✅ Updated {result.rowcount} collection records!")
            
            # Verify
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('loan_collections')]
            
            if 'loan_id' in columns:
                print("\n" + "=" * 60)
                print("✅ DATABASE FIX COMPLETED SUCCESSFULLY!")
                print("=" * 60)
                print("\n📝 Next steps:")
                print("1. Restart your Render service")
                print("2. Individual loan sheets will now work!")
                return True
            else:
                print("\n❌ Column was not added. Please contact support.")
                return False
                
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n📝 Troubleshooting:")
        print("1. Make sure you're running this in Render Shell")
        print("2. Check if database is PostgreSQL")
        print("3. Try restarting the service first")
        return False

if __name__ == '__main__':
    success = fix_database()
    exit(0 if success else 1)
