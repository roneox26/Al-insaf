from app import app, db
from models.customer_model import Customer
from models.loan_model import Loan
from models.loan_collection_model import LoanCollection

with app.app_context():
    try:
        # Get first customer
        customer = Customer.query.first()
        if customer:
            print(f"Customer: {customer.name}")
            print(f"ID: {customer.id}")
            
            # Test the route logic
            loans = Loan.query.filter_by(customer_name=customer.name).all()
            print(f"Loans: {len(loans)}")
            
            loan_collections = LoanCollection.query.filter_by(customer_id=customer.id).all()
            print(f"Collections: {len(loan_collections)}")
            
            # Test fee query
            from models.fee_model import FeeCollection
            admission_fee = db.session.query(db.func.sum(FeeCollection.amount)).filter_by(customer_id=customer.id, fee_type='admission').scalar() or 0
            print(f"Admission Fee: {admission_fee}")
            
            print("\nAll tests passed!")
        else:
            print("No customers found")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
