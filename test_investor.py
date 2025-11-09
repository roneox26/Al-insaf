from app import app, db
from models.investor_model import Investor
from models.investment_model import Investment

with app.app_context():
    # Check if investors table exists
    try:
        count = Investor.query.count()
        print(f"Investors table exists. Total investors: {count}")
        
        # Create a test investor
        if count == 0:
            investor = Investor(investor_id='INV-0001', name='Test Investor', phone='01700000000')
            db.session.add(investor)
            db.session.commit()
            print("Test investor created: INV-0001")
        
        # Show all investors
        investors = Investor.query.all()
        for inv in investors:
            print(f"ID: {inv.investor_id}, Name: {inv.name}")
            
    except Exception as e:
        print(f"Error: {e}")
