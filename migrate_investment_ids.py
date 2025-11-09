from app import app, db
from models.investment_model import Investment
from models.withdrawal_model import Withdrawal

with app.app_context():
    # Generate Investment IDs
    investments = Investment.query.filter_by(investment_id=None).all()
    
    if investments:
        print(f"Found {len(investments)} investments without ID. Generating IDs...")
        
        for idx, inv in enumerate(investments, start=1):
            inv.investment_id = f'INV-{idx:04d}'
            print(f"Generated ID: {inv.investment_id} for {inv.investor_name}")
        
        db.session.commit()
        print("✅ All investment IDs generated successfully!")
    else:
        print("✅ All investments already have IDs!")
    
    # Generate Withdrawal IDs
    withdrawals = Withdrawal.query.filter_by(withdrawal_id=None).all()
    
    if withdrawals:
        print(f"\nFound {len(withdrawals)} withdrawals without ID. Generating IDs...")
        
        for idx, wd in enumerate(withdrawals, start=1):
            wd.withdrawal_id = f'WD-{idx:04d}'
            print(f"Generated ID: {wd.withdrawal_id} for {wd.investor_name}")
        
        db.session.commit()
        print("✅ All withdrawal IDs generated successfully!")
    else:
        print("✅ All withdrawals already have IDs!")
