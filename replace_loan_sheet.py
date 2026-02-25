import re

# Read the file
with open(r'e:\ngo\app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# New FIFO-based loan_sheet function
new_function = '''@app.route('/loan_sheet/<int:loan_id>')
@login_required
def loan_sheet(loan_id):
    """Individual loan sheet with FIFO collection tracking"""
    try:
        loan = Loan.query.get_or_404(loan_id)
        customer = Customer.query.filter_by(name=loan.customer_name).first()
        
        if not customer:
            flash('Customer not found!', 'danger')
            return redirect(url_for('manage_loans'))
        
        # Get all loans for this customer (FIFO order)
        all_loans = Loan.query.filter_by(customer_name=customer.name).order_by(Loan.loan_date).all()
        all_collections = LoanCollection.query.filter_by(customer_id=customer.id).order_by(LoanCollection.collection_date).all()
        
        # FIFO: Allocate collections to loans in order
        loan_collections = []
        remaining_collections = list(all_collections)
        
        for l in all_loans:
            loan_total = l.amount + (l.amount * l.interest / 100)
            loan_paid = 0
            
            for lc in list(remaining_collections):
                if loan_paid >= loan_total:
                    break
                
                if l.id == loan.id:
                    loan_collections.append(lc)
                
                loan_paid += lc.amount
                remaining_collections.remove(lc)
            
            if l.id == loan.id:
                break
        
        saving_collections = SavingCollection.query.filter_by(customer_id=customer.id).order_by(SavingCollection.collection_date).all()
        withdrawals = Withdrawal.query.filter_by(customer_id=customer.id).order_by(Withdrawal.date).all()
        
        loan_with_interest = loan.amount + (loan.amount * loan.interest / 100)
        total_collected = sum(lc.amount for lc in loan_collections)
        remaining = loan_with_interest - total_collected
        
        total_savings_collected = sum(sc.amount for sc in saving_collections)
        total_withdrawn = sum(w.amount for w in withdrawals)
        actual_savings_balance = total_savings_collected - total_withdrawn
        
        collections_with_savings = []
        for lc in loan_collections:
            saving_on_date = sum(sc.amount for sc in saving_collections if sc.collection_date.date() == lc.collection_date.date())
            collections_with_savings.append({
                'collection': lc,
                'loan_amount': lc.amount,
                'saving_amount': saving_on_date
            })
        
        from models.fee_model import FeeCollection
        admission_fee = db.session.query(db.func.sum(FeeCollection.amount)).filter_by(customer_id=customer.id, fee_type='admission').scalar() or 0
        welfare_fee = db.session.query(db.func.sum(FeeCollection.amount)).filter_by(customer_id=customer.id, fee_type='welfare').scalar() or 0
        application_fee = db.session.query(db.func.sum(FeeCollection.amount)).filter_by(customer_id=customer.id, fee_type='application').scalar() or 0
        
        loan_date = loan.loan_date.strftime('%d-%m-%Y')
        loan_end_date = ''
        if loan.installment_count > 0:
            from datetime import timedelta
            if loan.installment_type in ['Daily', 'দৈনিক']:
                loan_end_date = (loan.loan_date + timedelta(days=loan.installment_count)).strftime('%d-%m-%Y')
            elif loan.installment_type in ['Weekly', 'সাপ্তাহিক']:
                loan_end_date = (loan.loan_date + timedelta(weeks=loan.installment_count)).strftime('%d-%m-%Y')
            else:
                loan_end_date = (loan.loan_date + timedelta(days=30*loan.installment_count)).strftime('%d-%m-%Y')
        
        staff = User.query.get(customer.staff_id) if customer.staff_id else None
        
        return render_template('customer_loan_sheet.html',
                             customer=customer,
                             loans=all_loans,
                             loans_with_collections=[{
                                 'loan': loan,
                                 'collections': collections_with_savings,
                                 'total_collected': total_collected,
                                 'total_with_interest': loan_with_interest,
                                 'remaining': remaining,
                                 'status': 'পরিশোধিত' if remaining <= 0 else 'বাকি'
                             }],
                             total_loan_disbursed=loan.amount,
                             total_interest=loan.amount * loan.interest / 100,
                             total_loan_collected=total_collected,
                             total_savings=total_savings_collected,
                             total_withdrawn=total_withdrawn,
                             actual_savings_balance=actual_savings_balance,
                             actual_remaining=remaining,
                             admission_fee=admission_fee,
                             welfare_fee=welfare_fee,
                             application_fee=application_fee,
                             loan_principal=loan.amount,
                             interest_amount=loan.amount * loan.interest / 100,
                             loan_date=loan_date,
                             loan_end_date=loan_end_date,
                             interest_rate=loan.interest,
                             installment_count=loan.installment_count,
                             weekly_installment=loan.installment_amount,
                             staff=staff,
                             now=datetime.now())
    except Exception as e:
        import traceback
        print(f"Error in loan_sheet: {e}")
        traceback.print_exc()
        flash(f'Error loading loan sheet: {str(e)}', 'danger')
        return redirect(url_for('manage_loans'))'''

# Find and replace the old loan_sheet function
pattern = r"@app\.route\('/loan_sheet/<int:loan_id>'\).*?(?=\n@app\.route\('/customer_loan_sheet)"
content = re.sub(pattern, new_function + '\n\n', content, flags=re.DOTALL)

# Write back
with open(r'e:\ngo\app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("loan_sheet function updated with FIFO logic!")
