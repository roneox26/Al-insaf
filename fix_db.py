from app import app, db
from sqlalchemy import text

print("Fixing database...")

with app.app_context():
    try:
        with db.engine.connect() as conn:
            # Add missing columns
            try:
                conn.execute(text("ALTER TABLE customers ADD COLUMN created_date DATETIME DEFAULT CURRENT_TIMESTAMP"))
                conn.commit()
                print("Added created_date to customers")
            except:
                print("created_date already exists")
            
            try:
                conn.execute(text("ALTER TABLE withdrawals ADD COLUMN customer_id INTEGER"))
                conn.commit()
                print("Added customer_id to withdrawals")
            except:
                print("customer_id already exists")
            
            try:
                conn.execute(text("ALTER TABLE withdrawals ADD COLUMN withdrawal_type VARCHAR(20) DEFAULT 'savings'"))
                conn.commit()
                print("Added withdrawal_type to withdrawals")
            except:
                print("withdrawal_type already exists")
        
        print("\nDatabase fixed! Run: python run.py")
        
    except Exception as e:
        print(f"Error: {e}")
