# -*- coding: utf-8 -*-
from app import app, db
from models.fee_model import FeeCollection

with app.app_context():
    # Delete fee collections with NULL customer_id
    null_fees = FeeCollection.query.filter(FeeCollection.customer_id == None).all()
    
    if null_fees:
        print(f"Found {len(null_fees)} fee collections with NULL customer_id")
        for fee in null_fees:
            print(f"Deleting fee ID {fee.id}: {fee.fee_type} - Amount: {fee.amount}")
            db.session.delete(fee)
        
        db.session.commit()
        print("Fixed! All NULL customer_id fee collections have been deleted.")
    else:
        print("No issues found. All fee collections have valid customer_id.")
