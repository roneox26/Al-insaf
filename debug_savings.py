from app import app, db
from models.customer_model import Customer
from models.saving_collection_model import SavingCollection
from models.loan_collection_model import LoanCollection
from models.loan_model import Loan

with app.app_context():
    # Get all customers
    customers = Customer.query.all()
    
    print("\n=== Customer Savings Analysis ===\n")
    
    for customer in customers:
        print(f"\nCustomer: {customer.name} (ID: {customer.id})")
        print(f"  Member No: {customer.member_no}")
        
        # Get all savings collections
        savings = SavingCollection.query.filter_by(customer_id=customer.id).all()
        total_savings = sum(s.amount for s in savings)
        
        print(f"  Total Savings Collections: {len(savings)}")
        print(f"  Total Savings Amount: {total_savings}")
        
        # Get all loan collections
        loan_collections = LoanCollection.query.filter_by(customer_id=customer.id).all()
        print(f"  Total Loan Collections: {len(loan_collections)}")
        
        # Show each savings collection
        if savings:
            print(f"  Savings Details:")
            for s in savings:
                date = s.collection_date.strftime('%Y-%m-%d')
                # Check if there's a loan collection on same date
                loan_on_date = any(lc.collection_date.date() == s.collection_date.date() for lc in loan_collections)
                print(f"    - {date}: Tk {s.amount} (Loan on same date: {loan_on_date})")
        
        # Get loans
        loans = Loan.query.filter_by(customer_name=customer.name).all()
        print(f"  Total Loans: {len(loans)}")
        
        print("-" * 60)
