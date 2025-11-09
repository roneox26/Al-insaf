from app import app, db
from models.investor_model import Investor
from models.investment_model import Investment
from models.withdrawal_model import Withdrawal

with app.app_context():
    db.create_all()
    
    # Migrate existing investments to create investors
    investments = Investment.query.all()
    investor_map = {}
    
    for inv in investments:
        if inv.investor_name not in investor_map:
            investor = Investor.query.filter_by(name=inv.investor_name).first()
            if not investor:
                last_investor = Investor.query.order_by(Investor.id.desc()).first()
                if last_investor:
                    last_num = int(last_investor.investor_id.split('-')[1])
                    investor_id = f'INV-{last_num + 1:04d}'
                else:
                    investor_id = f'INV-{len(investor_map) + 1:04d}'
                
                investor = Investor(investor_id=investor_id, name=inv.investor_name)
                db.session.add(investor)
                db.session.flush()
            
            investor_map[inv.investor_name] = investor.id
        
        inv.investor_id = investor_map[inv.investor_name]
    
    # Migrate withdrawals
    withdrawals = Withdrawal.query.all()
    for wd in withdrawals:
        if wd.investor_name:
            investor = Investor.query.filter_by(name=wd.investor_name).first()
            if investor:
                wd.investor_id = investor.id
    
    db.session.commit()
    print(f"Setup complete! Created {len(investor_map)} investors")
