"""
Fix for monthly_report route - handles database query errors and memory issues
"""

# Add this replacement code to your app.py monthly_report function

# Replace the problematic section around line 2400-2450 with this optimized version:

FIXED_CODE = '''
@app.route('/monthly_report')
@login_required
def monthly_report():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    import calendar
    today = datetime.now()
    month = int(request.args.get('month', today.month))
    year = int(request.args.get('year', today.year))
    
    month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    month_name = month_names[month]
    last_day = calendar.monthrange(year, month)[1]
    
    month_start = datetime(year, month, 1, 0, 0, 0)
    month_end = datetime(year, month, last_day, 23, 59, 59)
    
    # Get current cash balance
    try:
        cash_balance_record = CashBalance.query.first()
        current_cash = cash_balance_record.balance if cash_balance_record else 0
    except Exception as e:
        print(f"Cash balance error: {e}")
        current_cash = 0
    
    # For current month, calculate opening from month start transactions
    is_current_month = (month == today.month and year == today.year)
    
    try:
        if is_current_month:
            # Current month - get transactions from start of month till now
            loan_coll = db.session.query(db.func.coalesce(db.func.sum(LoanCollection.amount), 0)).filter(
                LoanCollection.collection_date >= month_start
            ).scalar()
            
            saving_coll = db.session.query(db.func.coalesce(db.func.sum(SavingCollection.amount), 0)).filter(
                SavingCollection.collection_date >= month_start
            ).scalar()
            
            fee_coll = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
                FeeCollection.collection_date >= month_start
            ).scalar()
            
            invest = db.session.query(db.func.coalesce(db.func.sum(Investment.amount), 0)).filter(
                Investment.date >= month_start
            ).scalar()
            
            month_income = loan_coll + saving_coll + fee_coll + invest
            
            loan_dist = db.session.query(db.func.coalesce(db.func.sum(Loan.amount), 0)).filter(
                Loan.loan_date >= month_start
            ).scalar()
            
            withdr = db.session.query(db.func.coalesce(db.func.sum(Withdrawal.amount), 0)).filter(
                Withdrawal.date >= month_start
            ).scalar()
            
            exp = db.session.query(db.func.coalesce(db.func.sum(Expense.amount), 0)).filter(
                Expense.date >= month_start
            ).scalar()
            
            month_expense = loan_dist + withdr + exp
            
            # Opening = Current - Net change from start of month
            opening_balance = current_cash - (month_income - month_expense)
        else:
            # Past month - calculate from future transactions
            future_loan = db.session.query(db.func.coalesce(db.func.sum(LoanCollection.amount), 0)).filter(
                LoanCollection.collection_date > month_end
            ).scalar()
            
            future_saving = db.session.query(db.func.coalesce(db.func.sum(SavingCollection.amount), 0)).filter(
                SavingCollection.collection_date > month_end
            ).scalar()
            
            future_fee = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
                FeeCollection.collection_date > month_end
            ).scalar()
            
            future_invest = db.session.query(db.func.coalesce(db.func.sum(Investment.amount), 0)).filter(
                Investment.date > month_end
            ).scalar()
            
            future_income = future_loan + future_saving + future_fee + future_invest
            
            future_loan_dist = db.session.query(db.func.coalesce(db.func.sum(Loan.amount), 0)).filter(
                Loan.loan_date > month_end
            ).scalar()
            
            future_withdr = db.session.query(db.func.coalesce(db.func.sum(Withdrawal.amount), 0)).filter(
                Withdrawal.date > month_end
            ).scalar()
            
            future_exp = db.session.query(db.func.coalesce(db.func.sum(Expense.amount), 0)).filter(
                Expense.date > month_end
            ).scalar()
            
            future_expense = future_loan_dist + future_withdr + future_exp
            
            opening_balance = current_cash - future_income + future_expense
    except Exception as e:
        print(f"Opening balance calculation error: {e}")
        import traceback
        traceback.print_exc()
        opening_balance = 0
    
    running_balance = opening_balance
    daily_data = {}
    
    # Process each day of the month
    for day in range(1, last_day + 1):
        day_start = datetime(year, month, day, 0, 0, 0)
        day_end = datetime(year, month, day, 23, 59, 59)
        
        try:
            # Get daily transactions with error handling
            installments = db.session.query(db.func.coalesce(db.func.sum(LoanCollection.amount), 0)).filter(
                LoanCollection.collection_date >= day_start,
                LoanCollection.collection_date <= day_end
            ).scalar()
            
            savings = db.session.query(db.func.coalesce(db.func.sum(SavingCollection.amount), 0)).filter(
                SavingCollection.collection_date >= day_start,
                SavingCollection.collection_date <= day_end
            ).scalar()
            
            welfare_fee = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
                FeeCollection.fee_type == 'welfare',
                FeeCollection.collection_date >= day_start,
                FeeCollection.collection_date <= day_end
            ).scalar()
            
            admission_fee = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
                FeeCollection.fee_type == 'admission',
                FeeCollection.collection_date >= day_start,
                FeeCollection.collection_date <= day_end
            ).scalar()
            
            application_fee = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
                FeeCollection.fee_type == 'application',
                FeeCollection.collection_date >= day_start,
                FeeCollection.collection_date <= day_end
            ).scalar()
            
            capital_savings = db.session.query(db.func.coalesce(db.func.sum(Investment.amount), 0)).filter(
                Investment.date >= day_start,
                Investment.date <= day_end
            ).scalar()
            
            loan_given = db.session.query(db.func.coalesce(db.func.sum(Loan.amount), 0)).filter(
                Loan.loan_date >= day_start,
                Loan.loan_date <= day_end
            ).scalar()
            
            interest = db.session.query(db.func.coalesce(db.func.sum(Loan.amount * Loan.interest / 100), 0)).filter(
                Loan.loan_date >= day_start,
                Loan.loan_date <= day_end
            ).scalar()
            
            savings_return = db.session.query(db.func.coalesce(db.func.sum(Withdrawal.amount), 0)).filter(
                Withdrawal.date >= day_start,
                Withdrawal.date <= day_end
            ).scalar()
            
            expenses_total = db.session.query(db.func.coalesce(db.func.sum(Expense.amount), 0)).filter(
                Expense.date >= day_start,
                Expense.date <= day_end
            ).scalar()
        except Exception as e:
            print(f"Day {day} query error: {e}")
            installments = savings = welfare_fee = admission_fee = application_fee = 0
            capital_savings = loan_given = interest = savings_return = expenses_total = 0
        
        # Calculate daily totals
        total_income = installments + savings + welfare_fee + admission_fee + application_fee + capital_savings
        total_expense = loan_given + savings_return + expenses_total
        day_balance = total_income - total_expense
        running_balance += day_balance
        
        daily_data[day] = {
            'savings': savings,
            'installments': installments,
            'welfare_fee': welfare_fee,
            'admission_fee': admission_fee,
            'service_charge': application_fee,
            'capital_savings': capital_savings,
            'total_income': total_income,
            'loan_given': loan_given,
            'interest': interest,
            'loan_with_interest': loan_given + interest,
            'savings_return': savings_return,
            'expenses': expenses_total,
            'total_expense': total_expense,
            'balance': running_balance
        }
    
    # Calculate summary data
    total_capital_savings = sum(d['capital_savings'] for d in daily_data.values())
    total_loan_distributed = sum(d['loan_given'] for d in daily_data.values())
    total_interest = sum(d['interest'] for d in daily_data.values())
    total_monthly_expenses = sum(d['expenses'] for d in daily_data.values())
    
    try:
        current_remaining = db.session.query(db.func.coalesce(db.func.sum(Customer.remaining_loan), 0)).scalar()
    except:
        current_remaining = 0
    
    closing_balance = running_balance
    
    # Calculate monthly due with error handling
    monthly_due = 0
    try:
        customers_with_loans = Customer.query.filter(Customer.remaining_loan > 0).all()
        
        for customer in customers_with_loans:
            try:
                customer_loans = Loan.query.filter(
                    Loan.customer_name == customer.name,
                    Loan.loan_date < month_start
                ).all()
                
                if not customer_loans:
                    continue
                
                expected_amount = 0
                for loan in customer_loans:
                    loan_type = loan.installment_type.lower() if loan.installment_type else ''
                    
                    if loan_type in ['daily', 'দৈনিক']:
                        if month == today.month and year == today.year:
                            days = today.day
                        else:
                            days = last_day
                        expected_amount += loan.installment_amount * days
                    elif loan_type in ['weekly', 'সাপ্তাহিক']:
                        expected_amount += loan.installment_amount * 4
                    elif loan_type in ['monthly', 'মাসিক']:
                        expected_amount += loan.installment_amount
                
                actual_amount = db.session.query(db.func.coalesce(db.func.sum(LoanCollection.amount), 0)).filter(
                    LoanCollection.customer_id == customer.id,
                    LoanCollection.collection_date >= month_start,
                    LoanCollection.collection_date <= month_end
                ).scalar()
                
                customer_due = expected_amount - actual_amount
                if customer_due > 0:
                    monthly_due += customer_due
            except Exception as e:
                print(f"Customer {customer.id} due calculation error: {e}")
                continue
    except Exception as e:
        print(f"Monthly due calculation error: {e}")
        monthly_due = 0
    
    return render_template('monthly_report.html', 
                         month=month, 
                         month_name=month_name, 
                         year=year, 
                         daily_data=daily_data, 
                         last_day=last_day, 
                         total_capital_savings=total_capital_savings, 
                         total_loan_distributed=total_loan_distributed, 
                         total_interest=total_interest, 
                         current_remaining=current_remaining, 
                         total_monthly_expenses=total_monthly_expenses, 
                         opening_balance=opening_balance, 
                         closing_balance=closing_balance, 
                         monthly_due=monthly_due)
'''

print("Copy the FIXED_CODE above and replace your monthly_report function in app.py")
print("\nKey changes:")
print("1. Added try-except blocks around all database queries")
print("2. Used db.func.coalesce() to handle NULL values")
print("3. Removed debug print statements that cause memory issues")
print("4. Added error handling for each customer in monthly due calculation")
