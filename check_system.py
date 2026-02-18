from app import app, db, Customer, Loan, LoanCollection

app.app_context().push()

print("=== System Health Check ===\n")

# 1. Check customers with loans but no loan_id in collections
customers = Customer.query.all()
print(f"Total customers: {len(customers)}")

issues = []
for c in customers:
    loans = Loan.query.filter_by(customer_name=c.name).all()
    lcs = LoanCollection.query.filter_by(customer_id=c.id).all()
    
    if loans and lcs:
        lcs_with_loan_id = [lc for lc in lcs if lc.loan_id]
        lcs_without_loan_id = [lc for lc in lcs if not lc.loan_id]
        
        if lcs_without_loan_id:
            issues.append({
                'customer_id': c.id,
                'name': c.name,
                'loans': len(loans),
                'collections_without_loan_id': len(lcs_without_loan_id)
            })

if issues:
    print(f"\nWARNING: Found {len(issues)} customers with collections missing loan_id:")
    for issue in issues[:10]:
        print(f"  - Customer {issue['customer_id']}: {issue['name']} - {issue['collections_without_loan_id']} collections need loan_id")
else:
    print("\nOK: All collections have loan_id assigned")

# 2. Check data consistency
print("\n=== Data Consistency Check ===")
inconsistent = []
for c in customers:
    loans = Loan.query.filter_by(customer_name=c.name).all()
    if not loans:
        continue
    
    # Calculate expected values
    total_loan_amount = sum(l.amount + (l.amount * l.interest / 100) for l in loans)
    total_collected = sum(lc.amount for lc in LoanCollection.query.filter_by(customer_id=c.id).all())
    expected_remaining = total_loan_amount - total_collected
    
    # Check if customer.remaining_loan matches
    if abs(c.remaining_loan - expected_remaining) > 0.01:
        inconsistent.append({
            'id': c.id,
            'name': c.name,
            'db_remaining': c.remaining_loan,
            'calculated_remaining': expected_remaining,
            'difference': c.remaining_loan - expected_remaining
        })

if inconsistent:
    print(f"\nWARNING: Found {len(inconsistent)} customers with inconsistent remaining_loan:")
    for item in inconsistent[:5]:
        print(f"  - {item['name']}: DB={item['db_remaining']}, Calculated={item['calculated_remaining']}, Diff={item['difference']}")
else:
    print("\nOK: All remaining_loan values are consistent")

# 3. Summary
print("\n=== Summary ===")
total_loans = Loan.query.count()
total_collections = LoanCollection.query.count()
collections_with_loan_id = LoanCollection.query.filter(LoanCollection.loan_id != None).count()
collections_without_loan_id = LoanCollection.query.filter(LoanCollection.loan_id == None).count()

print(f"Total Loans: {total_loans}")
print(f"Total Collections: {total_collections}")
print(f"  - With loan_id: {collections_with_loan_id}")
print(f"  - Without loan_id: {collections_without_loan_id}")

if collections_without_loan_id > 0:
    print(f"\nACTION NEEDED: Run migration to assign loan_id to {collections_without_loan_id} collections")
else:
    print("\nOK: System is healthy!")
