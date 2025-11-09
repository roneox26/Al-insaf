from app import app, db
from models.investment_model import Investment
from models.withdrawal_model import Withdrawal

with app.app_context():
    # Add new columns to existing tables
    with db.engine.connect() as conn:
        try:
            conn.execute(db.text("ALTER TABLE investments ADD COLUMN investment_id VARCHAR(20)"))
            print("Added investment_id column to investments table")
        except Exception as e:
            print(f"investment_id column may already exist: {e}")
        
        try:
            conn.execute(db.text("ALTER TABLE withdrawals ADD COLUMN withdrawal_id VARCHAR(20)"))
            print("Added withdrawal_id column to withdrawals table")
        except Exception as e:
            print(f"withdrawal_id column may already exist: {e}")
        
        conn.commit()
    
    # Generate IDs for existing records
    investments = Investment.query.all()
    for idx, inv in enumerate(investments, start=1):
        if not inv.investment_id:
            inv.investment_id = f'INV-{idx:04d}'
    
    withdrawals = Withdrawal.query.all()
    for idx, wd in enumerate(withdrawals, start=1):
        if not wd.withdrawal_id:
            wd.withdrawal_id = f'WD-{idx:04d}'
    
    db.session.commit()
    print(f"Generated IDs for {len(investments)} investments and {len(withdrawals)} withdrawals")
    print("Database update completed successfully!")
