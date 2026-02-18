from app import app, db, Customer, Loan, LoanCollection

app.app_context().push()

print("=== Fixing Jane Smith's Data ===\n")

# Get Jane Smith
customer = Customer.query.get(15)
if not customer:
    print("Customer not found!")
    exit()

print(f"Customer: {customer.name}")

# Get her loan
loan = Loan.query.filter_by(customer_name=customer.name).first()
if loan:
    print(f"Loan ID: {loan.id}, Amount: {loan.amount}")
    
    # Get collection without loan_id
    collection = LoanCollection.query.filter_by(customer_id=customer.id, loan_id=None).first()
    if collection:
        print(f"Found collection without loan_id: {collection.amount}")
        collection.loan_id = loan.id
        print(f"Assigned loan_id={loan.id} to collection")
    
    # Recalculate remaining_loan
    total_with_interest = loan.amount + (loan.amount * loan.interest / 100)
    total_collected = sum(lc.amount for lc in LoanCollection.query.filter_by(customer_id=customer.id).all())
    correct_remaining = total_with_interest - total_collected
    
    print(f"\nRecalculating remaining_loan:")
    print(f"  Total with interest: {total_with_interest}")
    print(f"  Total collected: {total_collected}")
    print(f"  Correct remaining: {correct_remaining}")
    print(f"  Current DB value: {customer.remaining_loan}")
    
    customer.remaining_loan = correct_remaining
    
    db.session.commit()
    print("\nFixed successfully!")
else:
    print("No loan found!")
