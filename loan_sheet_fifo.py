@app.route('/loan_sheet/<int:loan_id>')
@login_required
def loan_sheet(loan_id):
    """Individual loan sheet for a specific loan with FIFO collection tracking"""
    try:
        loan = Loan.query.get_or_404(loan_id)
        customer = Customer.query.filter_by(name=loan.customer_name).first()
        
        if not customer:
            flash('Customer not found!', 'danger')
            return redirect(url_for('manage_loans'))
        
        # Get all loans for this customer (FIFO order)
        all_loans = Loan.query.filter_by(customer_name=customer.name).order_by(Loan.loan_date).all()
        
        # Get all loan collections
        all_loan_collections = LoanCollection.query.filter_by(customer_id=customer.id).order_by(LoanCollection.collection_date).all()
        
        # Calculate collections for THIS specific loan using FIFO
        loan_collections = []
        total_allocated = 0
        
        for l in all_loans:
            loan_total = l.amount + (l.amount * l.interest / 100)
            
            if l.id == loan.id:
                # This is our target loan - allocate collections
                for lc in all_loan_collections:
                    if total_allocated >= loan_total:
                        break  # This loan is fully paid
                    
                    if total_allocated + lc.amount <= loan_total:
                        loan_collections.append(lc)
                        total_allocated += lc.amount
                    else:
                        # Partial allocation
                        remaining_space = loan_total - total_allocated
                        if remaining_space > 0:
                            loan_collections.append(lc)
                            total_allocated += remaining_space
                break
            else:
                # Previous loan - skip collections allocated to it
                loan_allocated = 0
                for lc in all_loan_collections:
                    if loan_allocated >= loan_total:
                        break
                    loan_allocated += lc.amount
                    all_loan_collections = [c for c in all_loan_collections if c.id != lc.id]
        
        saving_collections = SavingCollection.query.filter_by(customer_id=customer.id).order_by(SavingCollection.collection_date).all()
        withdrawals = Withdrawal.query.filter_by(customer_id=customer.id).order_by(Withdrawal.date).all()
        
        # Calculate loan specific data
        loan_with_interest = loan.amount + (loan.amount * loan.interest / 100)
        total_collected = sum(lc.amount for lc in loan_collections)
        remaining = loan_with_interest - total_collected
        
        # Savings data
        total_savings_collected = sum(sc.amount for sc in saving_collections)
        total_withdrawn = sum(w.amount for w in withdrawals)
        actual_savings_balance = total_savings_collected - total_withdrawn
        
        # Create collection list with savings
        collections_with_savings = []
        for lc in loan_collections:
            saving_on_date = sum(sc.amount for sc in saving_collections if sc.collection_date.date() == lc.collection_date.date())
            collections_with_savings.append({
                'collection': lc,
                'loan_amount': lc.amount,
                'saving_amount': saving_on_date
            })
        
        # Get fees
        from models.fee_model import FeeCollection
        admission_fee = db.session.query(db.func.sum(FeeCollection.amount)).filter_by(customer_id=customer.id, fee_type='admission').scalar() or 0
        welfare_fee = db.session.query(db.func.sum(FeeCollection.amount)).filter_by(customer_id=customer.id, fee_type='welfare').scalar() or 0
        application_fee = db.session.query(db.func.sum(FeeCollection.amount)).filter_by(customer_id=customer.id, fee_type='application').scalar() or 0
        
        # Loan details
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
        return redirect(url_for('manage_loans'))
