from app import app, db, Customer, Loan, LoanCollection, SavingCollection, User
from models.fee_model import FeeCollection

app.app_context().push()

id = 2
customer = db.session.get(Customer, id)
loans = Loan.query.filter_by(customer_name=customer.name).order_by(Loan.loan_date).all()

print(f"Customer: {customer.name}")
print(f"Loans found: {len(loans)}")

loans_with_collections = []
for loan in loans:
    loan_collections = LoanCollection.query.filter_by(customer_id=id, loan_id=loan.id).order_by(LoanCollection.collection_date).all()
    
    if not loan_collections:
        latest_loan = loans[-1] if loans else None
        if loan == latest_loan:
            loan_collections = LoanCollection.query.filter_by(customer_id=id, loan_id=None).order_by(LoanCollection.collection_date).all()
    
    loan_collected = sum(lc.amount for lc in loan_collections)
    loan_with_interest = loan.amount + (loan.amount * loan.interest / 100)
    loan_remaining = loan_with_interest - loan_collected
    
    loans_with_collections.append({
        'loan': loan,
        'collections': loan_collections,
        'total_collected': loan_collected,
        'total_with_interest': loan_with_interest,
        'remaining': loan_remaining,
        'status': 'পরিশোধিত' if loan_remaining <= 0 else 'চলমান'
    })
    
    print(f"\nLoan {loan.id}:")
    print(f"  Collections: {len(loan_collections)}")
    print(f"  Total collected: {loan_collected}")
    print(f"  With interest: {loan_with_interest}")
    print(f"  Remaining: {loan_remaining}")

print(f"\nTotal loans_with_collections: {len(loans_with_collections)}")
print(f"Will template show data: {'YES' if loans_with_collections else 'NO - will show else block'}")
