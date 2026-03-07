# OPTIMIZED MONTHLY REPORT - Replace in app.py around line 2299

@app.route('/monthly_report')
@login_required
def monthly_report():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    import calendar
    from sqlalchemy import func, extract
    
    today = datetime.now()
    month = int(request.args.get('month', today.month))
    year = int(request.args.get('year', today.year))
    
    month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    month_name = month_names[month]
    last_day = calendar.monthrange(year, month)[1]
    
    month_start = datetime(year, month, 1, 0, 0, 0)
    month_end = datetime(year, month, last_day, 23, 59, 59)
    
    # Get current cash balance
    cash_balance_record = CashBalance.query.first()
    current_cash = cash_balance_record.balance if cash_balance_record else 0
    
    # Calculate opening balance
    is_current_month = (month == today.month and year == today.year)
    
    if is_current_month:
        month_income = (
            (db.session.query(func.coalesce(func.sum(LoanCollection.amount), 0)).filter(
                LoanCollection.collection_date >= month_start
            ).scalar() or 0) +
            (db.session.query(func.coalesce(func.sum(SavingCollection.amount), 0)).filter(
                SavingCollection.collection_date >= month_start
            ).scalar() or 0) +
            (db.session.query(func.coalesce(func.sum(FeeCollection.amount), 0)).filter(
                FeeCollection.collection_date >= month_start
            ).scalar() or 0) +
            (db.session.query(func.coalesce(func.sum(Investment.amount), 0)).filter(
                Investment.date >= month_start
            ).scalar() or 0)
        )
        
        month_expense = (
            (db.session.query(func.coalesce(func.sum(Loan.amount), 0)).filter(
                Loan.loan_date >= month_start
            ).scalar() or 0) +
            (db.session.query(func.coalesce(func.sum(Withdrawal.amount), 0)).filter(
                Withdrawal.date >= month_start
            ).scalar() or 0) +
            (db.session.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
                Expense.date >= month_start
            ).scalar() or 0)
        )
        
        opening_balance = current_cash - (month_income - month_expense)
    else:
        future_income = (
            (db.session.query(func.coalesce(func.sum(LoanCollection.amount), 0)).filter(
                LoanCollection.collection_date > month_end
            ).scalar() or 0) +
            (db.session.query(func.coalesce(func.sum(SavingCollection.amount), 0)).filter(
                SavingCollection.collection_date > month_end
            ).scalar() or 0) +
            (db.session.query(func.coalesce(func.sum(FeeCollection.amount), 0)).filter(
                FeeCollection.collection_date > month_end
            ).scalar() or 0) +
            (db.session.query(func.coalesce(func.sum(Investment.amount), 0)).filter(
                Investment.date > month_end
            ).scalar() or 0)
        )
        
        future_expense = (
            (db.session.query(func.coalesce(func.sum(Loan.amount), 0)).filter(
                Loan.loan_date > month_end
            ).scalar() or 0) +
            (db.session.query(func.coalesce(func.sum(Withdrawal.amount), 0)).filter(
                Withdrawal.date > month_end
            ).scalar() or 0) +
            (db.session.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
                Expense.date > month_end
            ).scalar() or 0)
        )
        
        opening_balance = current_cash - future_income + future_expense
    
    # OPTIMIZED: Get all data for the month in single queries using GROUP BY
    running_balance = opening_balance
    daily_data = {}
    
    # Initialize all days with zero values
    for day in range(1, last_day + 1):
        daily_data[day] = {
            'savings': 0,
            'installments': 0,
            'welfare_fee': 0,
            'admission_fee': 0,
            'service_charge': 0,
            'capital_savings': 0,
            'total_income': 0,
            'loan_given': 0,
            'interest': 0,
            'loan_with_interest': 0,
            'savings_return': 0,
            'expenses': 0,
            'total_expense': 0,
            'balance': running_balance
        }
    
    # Fetch all collections grouped by day
    loan_collections_by_day = db.session.query(
        extract('day', LoanCollection.collection_date).label('day'),
        func.sum(LoanCollection.amount).label('total')
    ).filter(
        LoanCollection.collection_date >= month_start,
        LoanCollection.collection_date <= month_end
    ).group_by(extract('day', LoanCollection.collection_date)).all()
    
    saving_collections_by_day = db.session.query(
        extract('day', SavingCollection.collection_date).label('day'),
        func.sum(SavingCollection.amount).label('total')
    ).filter(
        SavingCollection.collection_date >= month_start,
        SavingCollection.collection_date <= month_end
    ).group_by(extract('day', SavingCollection.collection_date)).all()
    
    welfare_fees_by_day = db.session.query(
        extract('day', FeeCollection.collection_date).label('day'),
        func.sum(FeeCollection.amount).label('total')
    ).filter(
        FeeCollection.fee_type == 'welfare',
        FeeCollection.collection_date >= month_start,
        FeeCollection.collection_date <= month_end
    ).group_by(extract('day', FeeCollection.collection_date)).all()
    
    admission_fees_by_day = db.session.query(
        extract('day', FeeCollection.collection_date).label('day'),
        func.sum(FeeCollection.amount).label('total')
    ).filter(
        FeeCollection.fee_type == 'admission',
        FeeCollection.collection_date >= month_start,
        FeeCollection.collection_date <= month_end
    ).group_by(extract('day', FeeCollection.collection_date)).all()
    
    application_fees_by_day = db.session.query(
        extract('day', FeeCollection.collection_date).label('day'),
        func.sum(FeeCollection.amount).label('total')
    ).filter(
        FeeCollection.fee_type == 'application',
        FeeCollection.collection_date >= month_start,
        FeeCollection.collection_date <= month_end
    ).group_by(extract('day', FeeCollection.collection_date)).all()
    
    investments_by_day = db.session.query(
        extract('day', Investment.date).label('day'),
        func.sum(Investment.amount).label('total')
    ).filter(
        Investment.date >= month_start,
        Investment.date <= month_end
    ).group_by(extract('day', Investment.date)).all()
    
    loans_by_day = db.session.query(
        extract('day', Loan.loan_date).label('day'),
        func.sum(Loan.amount).label('total'),
        func.sum(Loan.amount * Loan.interest / 100).label('interest')
    ).filter(
        Loan.loan_date >= month_start,
        Loan.loan_date <= month_end
    ).group_by(extract('day', Loan.loan_date)).all()
    
    withdrawals_by_day = db.session.query(
        extract('day', Withdrawal.date).label('day'),
        func.sum(Withdrawal.amount).label('total')
    ).filter(
        Withdrawal.date >= month_start,
        Withdrawal.date <= month_end
    ).group_by(extract('day', Withdrawal.date)).all()
    
    expenses_by_day = db.session.query(
        extract('day', Expense.date).label('day'),
        func.sum(Expense.amount).label('total')
    ).filter(
        Expense.date >= month_start,
        Expense.date <= month_end
    ).group_by(extract('day', Expense.date)).all()
    
    # Populate daily data
    for day, total in loan_collections_by_day:
        daily_data[int(day)]['installments'] = float(total or 0)
    
    for day, total in saving_collections_by_day:
        daily_data[int(day)]['savings'] = float(total or 0)
    
    for day, total in welfare_fees_by_day:
        daily_data[int(day)]['welfare_fee'] = float(total or 0)
    
    for day, total in admission_fees_by_day:
        daily_data[int(day)]['admission_fee'] = float(total or 0)
    
    for day, total in application_fees_by_day:
        daily_data[int(day)]['service_charge'] = float(total or 0)
    
    for day, total in investments_by_day:
        daily_data[int(day)]['capital_savings'] = float(total or 0)
    
    for day, total, interest in loans_by_day:
        daily_data[int(day)]['loan_given'] = float(total or 0)
        daily_data[int(day)]['interest'] = float(interest or 0)
    
    for day, total in withdrawals_by_day:
        daily_data[int(day)]['savings_return'] = float(total or 0)
    
    for day, total in expenses_by_day:
        daily_data[int(day)]['expenses'] = float(total or 0)
    
    # Calculate totals and running balance
    for day in range(1, last_day + 1):
        d = daily_data[day]
        d['total_income'] = d['installments'] + d['savings'] + d['welfare_fee'] + d['admission_fee'] + d['service_charge'] + d['capital_savings']
        d['loan_with_interest'] = d['loan_given'] + d['interest']
        d['total_expense'] = d['loan_given'] + d['savings_return'] + d['expenses']
        running_balance += d['total_income'] - d['total_expense']
        d['balance'] = running_balance
    
    # Calculate summary
    total_capital_savings = sum(d['capital_savings'] for d in daily_data.values())
    total_loan_distributed = sum(d['loan_given'] for d in daily_data.values())
    total_interest = sum(d['interest'] for d in daily_data.values())
    total_monthly_expenses = sum(d['expenses'] for d in daily_data.values())
    current_remaining = db.session.query(func.coalesce(func.sum(Customer.remaining_loan), 0)).scalar() or 0
    closing_balance = running_balance
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
