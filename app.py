from flask import Flask, render_template, redirect, url_for, flash, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models.user_model import db, User
import config
from models.staff_model import Staff
from models.loan_model import Loan
from models.saving_model import Saving
from models.customer_model import Customer
from models.collection_model import Collection
from models.loan_collection_model import LoanCollection
from models.saving_collection_model import SavingCollection
from models.cash_balance_model import CashBalance
from models.investor_model import Investor
from models.investment_model import Investment
from models.withdrawal_model import Withdrawal
from models.fee_model import FeeCollection
from models.expense_model import Expense
from models.message_model import Message
from models.note_model import Note
from datetime import datetime, timedelta
import csv
import io


app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ----------- Routes -----------

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not email or not password:
            flash('ইমেইল এবং পাসওয়ার্ড আবশ্যক!', 'danger')
            return render_template('login.html')

        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Login Successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        staff_count = User.query.filter_by(role='staff').count()
        total_loans = db.session.query(db.func.sum(Customer.total_loan)).scalar() or 0
        pending_loans = db.session.query(db.func.sum(Customer.remaining_loan)).scalar() or 0
        total_savings = db.session.query(db.func.sum(Customer.savings_balance)).scalar() or 0
        total_customers = Customer.query.count()
        due_customers = Customer.query.filter(Customer.remaining_loan > 0).count()
        
        cash_balance_record = CashBalance.query.first()
        cash_balance = cash_balance_record.balance if cash_balance_record else 0
        
        period = request.args.get('period', 'all')
        
        admission_fee_total = db.session.query(db.func.sum(FeeCollection.amount)).filter_by(fee_type='admission').scalar() or 0
        welfare_fee_total = db.session.query(db.func.sum(FeeCollection.amount)).filter_by(fee_type='welfare').scalar() or 0
        application_fee_total = db.session.query(db.func.sum(FeeCollection.amount)).filter_by(fee_type='application').scalar() or 0
        notes_count = Note.query.count()
        
        return render_template('admin_dashboard.html', name=current_user.name, staff_count=staff_count, total_loans=total_loans, pending_loans=pending_loans, total_savings=total_savings, total_customers=total_customers, cash_balance=cash_balance, period=period, admission_fee_total=admission_fee_total, welfare_fee_total=welfare_fee_total, application_fee_total=application_fee_total, due_customers=due_customers, notes_count=notes_count)
    elif current_user.role == 'staff':
        my_customers = Customer.query.filter_by(staff_id=current_user.id).count()
        total_remaining = db.session.query(db.func.sum(Customer.remaining_loan)).filter_by(staff_id=current_user.id).scalar() or 0
        due_customers = Customer.query.filter_by(staff_id=current_user.id).filter(Customer.remaining_loan > 0).count()
        today = datetime.now().replace(hour=0, minute=0, second=0)
        today_loan_collections = LoanCollection.query.filter_by(staff_id=current_user.id).filter(LoanCollection.collection_date >= today).count()
        today_saving_collections = SavingCollection.query.filter_by(staff_id=current_user.id).filter(SavingCollection.collection_date >= today).count()
        today_collections = today_loan_collections + today_saving_collections
        unread_messages = Message.query.filter_by(staff_id=current_user.id, is_read=False).count()
        return render_template('staff_dashboard.html', name=current_user.name, my_customers=my_customers, total_remaining=total_remaining, today_collections=today_collections, unread_messages=unread_messages, due_customers=due_customers)
    else:
        flash('Invalid role!', 'danger')
        return redirect(url_for('logout'))

@app.route('/admin/staffs')
@login_required
def manage_staff():
    if current_user.role != 'admin':
        flash('Access denied! Only admin can view this page.', 'danger')
        return redirect(url_for('dashboard'))

    staffs = User.query.filter_by(role='staff').all()
    staff_data = []
    total_all_collections = db.session.query(db.func.sum(LoanCollection.amount)).scalar() or 0
    total_all_collections += db.session.query(db.func.sum(SavingCollection.amount)).scalar() or 0
    
    for staff in staffs:
        loan_collection = db.session.query(db.func.sum(LoanCollection.amount)).filter_by(staff_id=staff.id).scalar() or 0
        saving_collection = db.session.query(db.func.sum(SavingCollection.amount)).filter_by(staff_id=staff.id).scalar() or 0
        total_collection = loan_collection + saving_collection
        percentage = (total_collection / total_all_collections * 100) if total_all_collections > 0 else 0
        
        staff_data.append({
            'staff': staff,
            'total_collection': total_collection,
            'percentage': percentage
        })
    
    return render_template('manage_staff.html', staff_data=staff_data)

@app.route('/admin/staff/add', methods=['GET', 'POST'])
@login_required
def add_staff():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        is_office_staff = request.form.get('is_office_staff') == 'on'
        
        if not name or not email or not password:
            flash('সব তথ্য পূরণ করুন!', 'danger')
            return redirect(url_for('add_staff'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('add_staff'))
        
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_staff = User(name=name, email=email, password=hashed_pw, role='staff', is_office_staff=is_office_staff)
        db.session.add(new_staff)
        db.session.commit()
        flash('Staff added successfully!', 'success')
        return redirect(url_for('manage_staff'))
    
    return render_template('add_staff.html')

@app.route('/admin/staff/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_staff(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    staff = User.query.get_or_404(id)
    if staff.role != 'staff':
        flash('Invalid staff!', 'danger')
        return redirect(url_for('manage_staff'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        
        if not name or not email:
            flash('নাম এবং ইমেইল আবশ্যক!', 'danger')
            return redirect(url_for('edit_staff', id=id))
        
        staff.name = name
        staff.email = email
        
        if request.form.get('password'):
            staff.password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        
        db.session.commit()
        flash('Staff updated successfully!', 'success')
        return redirect(url_for('manage_staff'))
    
    return render_template('edit_staff.html', staff=staff)

@app.route('/staff/collection_report/<int:id>')
@login_required
def staff_collection_report(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    staff = User.query.get_or_404(id)
    if staff.role != 'staff':
        flash('Invalid staff!', 'danger')
        return redirect(url_for('manage_staff'))
    
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    
    query_loan = LoanCollection.query.filter_by(staff_id=id)
    query_saving = SavingCollection.query.filter_by(staff_id=id)
    
    if from_date:
        try:
            from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
            query_loan = query_loan.filter(LoanCollection.collection_date >= from_datetime)
            query_saving = query_saving.filter(SavingCollection.collection_date >= from_datetime)
        except ValueError:
            flash('Invalid from date format!', 'danger')
    
    if to_date:
        try:
            to_datetime = datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_loan = query_loan.filter(LoanCollection.collection_date <= to_datetime)
            query_saving = query_saving.filter(SavingCollection.collection_date <= to_datetime)
        except ValueError:
            flash('Invalid to date format!', 'danger')
    
    loan_collections = query_loan.all()
    saving_collections = query_saving.all()
    
    daily_collections = {}
    for lc in loan_collections:
        date_key = lc.collection_date.strftime('%Y-%m-%d')
        if date_key not in daily_collections:
            daily_collections[date_key] = {'loan': 0, 'saving': 0}
        daily_collections[date_key]['loan'] += lc.amount
    
    for sc in saving_collections:
        date_key = sc.collection_date.strftime('%Y-%m-%d')
        if date_key not in daily_collections:
            daily_collections[date_key] = {'loan': 0, 'saving': 0}
        daily_collections[date_key]['saving'] += sc.amount
    
    daily_collections = dict(sorted(daily_collections.items(), reverse=True))
    total_loan = sum(lc.amount for lc in loan_collections)
    total_saving = sum(sc.amount for sc in saving_collections)
    
    return render_template('staff_collection_report.html', staff=staff, daily_collections=daily_collections, total_loan=total_loan, total_saving=total_saving, from_date=from_date, to_date=to_date)

@app.route('/all_staff_report_print')
@login_required
def all_staff_report_print():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    staffs = User.query.filter_by(role='staff').all()
    staff_data = []
    
    for staff in staffs:
        customers = Customer.query.filter_by(staff_id=staff.id).count()
        total_loan = db.session.query(db.func.sum(LoanCollection.amount)).filter_by(staff_id=staff.id).scalar() or 0
        total_saving = db.session.query(db.func.sum(SavingCollection.amount)).filter_by(staff_id=staff.id).scalar() or 0
        remaining_loan = db.session.query(db.func.sum(Customer.remaining_loan)).filter_by(staff_id=staff.id).scalar() or 0
        
        staff_data.append({
            'staff': staff,
            'customers': customers,
            'total_loan': total_loan,
            'total_saving': total_saving,
            'remaining_loan': remaining_loan,
            'total_collection': total_loan + total_saving
        })
    
    return render_template('all_staff_report_print.html', staff_data=staff_data)

@app.route('/admin/staff/delete/<int:id>')
@login_required
def delete_staff(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    staff = User.query.get_or_404(id)
    if staff.role != 'staff':
        flash('Invalid staff!', 'danger')
        return redirect(url_for('manage_staff'))
    
    db.session.delete(staff)
    db.session.commit()
    flash('Staff deleted successfully!', 'success')
    return redirect(url_for('manage_staff'))




@app.route('/loans')
@login_required
def manage_loans():
    staff_filter = request.args.get('staff_id', type=int)
    customer_filter = request.args.get('customer', '')
    
    query = Loan.query
    if staff_filter:
        query = query.filter_by(staff_id=staff_filter)
    if customer_filter:
        query = query.filter(Loan.customer_name.contains(customer_filter))
    
    loans = query.all()
    staffs = User.query.filter_by(role='staff').all()
    return render_template('manage_loans.html', loans=loans, staffs=staffs)

@app.route('/loan_collections_history')
@login_required
def loan_collections_history():
    staff_filter = request.args.get('staff_id', type=int)
    customer_filter = request.args.get('customer', '')
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    
    if current_user.role == 'staff':
        query = LoanCollection.query.filter_by(staff_id=current_user.id)
    else:
        query = LoanCollection.query
        if staff_filter:
            query = query.filter_by(staff_id=staff_filter)
    
    if customer_filter:
        query = query.join(Customer).filter(Customer.name.contains(customer_filter))
    
    if from_date:
        try:
            from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(LoanCollection.collection_date >= from_datetime)
        except ValueError:
            flash('Invalid from date format!', 'danger')
    
    if to_date:
        try:
            to_datetime = datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(LoanCollection.collection_date <= to_datetime)
        except ValueError:
            flash('Invalid to date format!', 'danger')
    
    loan_collections = query.order_by(LoanCollection.collection_date.desc()).all()
    total = sum(lc.amount for lc in loan_collections)
    staffs = User.query.filter_by(role='staff').all()
    return render_template('loan_collections_history.html', loan_collections=loan_collections, staffs=staffs, total=total, from_date=from_date, to_date=to_date)

@app.route('/loan/add', methods=['GET', 'POST'])
@login_required
def add_loan():
    if current_user.role != 'admin':
        flash('শুধুমাত্র Admin লোন দিতে পারবে!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            customer_id = request.form.get('customer_id', type=int)
            amount = request.form.get('amount', type=float, default=0)
            interest_rate = request.form.get('interest', type=float, default=0)
            
            if not customer_id or amount <= 0:
                flash('সব তথ্য সঠিকভাবে পূরণ করুন!', 'danger')
                return redirect(url_for('add_loan'))
            customer = Customer.query.get_or_404(customer_id)
            
            cash_balance_record = CashBalance.query.first()
            if not cash_balance_record:
                cash_balance_record = CashBalance(balance=0)
                db.session.add(cash_balance_record)
            
            if cash_balance_record.balance < amount:
                flash(f'পর্যাপ্ত টাকা নেই! বর্তমান ব্যালেন্স: ৳{cash_balance_record.balance}', 'danger')
                return redirect(url_for('add_loan'))
            
            interest_amount = (amount * interest_rate) / 100
            
            # Safe float conversion for fees
            service_charge_str = request.form.get('service_charge', '0').strip()
            service_charge = float(service_charge_str) if service_charge_str else 0.0
            
            welfare_fee_str = request.form.get('welfare_fee', '0').strip()
            welfare_fee = float(welfare_fee_str) if welfare_fee_str else 0.0
            
            application_fee_str = request.form.get('application_fee', '0').strip()
            application_fee = float(application_fee_str) if application_fee_str else 0.0
            
            total_with_interest = amount + interest_amount + service_charge
            
            loan_date_str = request.form.get('loan_date')
            loan_date = datetime.strptime(loan_date_str, '%Y-%m-%d') if loan_date_str else datetime.now()
            
            loan = Loan(
                customer_name=customer.name,
                amount=amount,
                interest=interest_rate,
                loan_date=loan_date,
                due_date=datetime.strptime(request.form['due_date'], '%Y-%m-%d'),
                installment_count=int(request.form.get('installment_count', 0)),
                installment_amount=float(request.form.get('installment_amount', '0') or 0),
                service_charge=service_charge,
                installment_type=request.form.get('installment_type', ''),
                staff_id=customer.staff_id
            )
            
            customer.total_loan += total_with_interest
            customer.remaining_loan += total_with_interest
            cash_balance_record.balance -= amount
            cash_balance_record.balance += service_charge + welfare_fee + application_fee
            
            # Add fee collections
            if welfare_fee > 0:
                fee_col = FeeCollection(customer_id=customer.id, fee_type='welfare', amount=welfare_fee, collected_by=current_user.id)
                db.session.add(fee_col)
            if application_fee > 0:
                fee_col = FeeCollection(customer_id=customer.id, fee_type='application', amount=application_fee, collected_by=current_user.id)
                db.session.add(fee_col)
            
            db.session.add(loan)
            db.session.commit()
            flash(f'ঋণ যোগ সফল! পরিমাণ: ৳{amount}, সুদ: ৳{interest_amount}, সার্ভিস চার্জ: ৳{service_charge}, কল্যাণ ফি: ৳{welfare_fee}, আবেদন ফি: ৳{application_fee}, মোট: ৳{total_with_interest}', 'success')
            return redirect(url_for('manage_loans'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('add_loan'))
    
    cash_balance_record = CashBalance.query.first()
    cash_balance = cash_balance_record.balance if cash_balance_record else 0
    customers = Customer.query.all()
    return render_template('add_loan.html', customers=customers, cash_balance=cash_balance)

@app.route('/loan/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_loan(id):
    loan = Loan.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            customer_name = request.form.get('customer_name', '').strip()
            amount = request.form.get('amount', type=float, default=0)
            interest = request.form.get('interest', type=float, default=0)
            due_date_str = request.form.get('due_date', '')
            status = request.form.get('status', '')
            
            if not customer_name or amount <= 0 or not due_date_str:
                flash('সব তথ্য সঠিকভাবে পূরণ করুন!', 'danger')
                return redirect(url_for('edit_loan', id=id))
            
            loan.customer_name = customer_name
            loan.amount = amount
            loan.interest = interest
            loan.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            loan.status = status
            db.session.commit()
            flash('Loan updated successfully!', 'success')
            return redirect(url_for('manage_loans'))
        except ValueError:
            flash('Invalid date format!', 'danger')
            return redirect(url_for('edit_loan', id=id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('edit_loan', id=id))
    
    return render_template('edit_loan.html', loan=loan)

@app.route('/loan/mark_paid/<int:id>')
@login_required
def mark_paid(id):
    loan = Loan.query.get_or_404(id)
    loan.status = 'Paid'
    db.session.commit()
    flash('Loan marked as paid!', 'success')
    return redirect(url_for('manage_loans'))

@app.route('/savings')
@login_required
def manage_savings():
    staff_filter = request.args.get('staff_id', type=int)
    customer_filter = request.args.get('customer', '')
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    
    query = SavingCollection.query
    if staff_filter:
        query = query.filter_by(staff_id=staff_filter)
    if customer_filter:
        query = query.join(Customer).filter(Customer.name.contains(customer_filter))
    
    if from_date:
        try:
            from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(SavingCollection.collection_date >= from_datetime)
        except ValueError:
            flash('Invalid from date format!', 'danger')
    
    if to_date:
        try:
            to_datetime = datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(SavingCollection.collection_date <= to_datetime)
        except ValueError:
            flash('Invalid to date format!', 'danger')
    
    savings = query.all()
    total = sum(s.amount for s in savings)
    staffs = User.query.filter_by(role='staff').all()
    return render_template('manage_savings.html', savings=savings, staffs=staffs, total=total, from_date=from_date, to_date=to_date)

@app.route('/saving/add', methods=['GET', 'POST'])
@login_required
def add_saving():
    if request.method == 'POST':
        customer_id = request.form.get('customer_id', type=int)
        amount = request.form.get('amount', type=float, default=0)
        
        if not customer_id or amount <= 0:
            flash('সব তথ্য সঠিকভাবে পূরণ করুন!', 'danger')
            return redirect(url_for('add_saving'))
        
        customer = Customer.query.get_or_404(customer_id)
        
        saving = Saving(
            customer_name=customer.name,
            amount=amount,
            staff_id=current_user.id
        )
        
        customer.savings_balance += amount
        
        db.session.add(saving)
        db.session.commit()
        flash('Saving added successfully!', 'success')
        return redirect(url_for('manage_savings'))
    
    if current_user.role == 'staff':
        customers = Customer.query.filter_by(staff_id=current_user.id).all()
    else:
        customers = Customer.query.all()
    return render_template('add_saving.html', customers=customers)

@app.route('/reports')
@login_required
def reports():
    period = request.args.get('period', 'daily')
    staff_id = request.args.get('staff_id', type=int)
    
    today = datetime.now()
    if period == 'daily':
        start_date = today.replace(hour=0, minute=0, second=0)
    elif period == 'weekly':
        start_date = today - timedelta(days=7)
    else:  # monthly
        start_date = today - timedelta(days=30)
    
    loan_collection_query = LoanCollection.query.filter(LoanCollection.collection_date >= start_date)
    saving_collection_query = SavingCollection.query.filter(SavingCollection.collection_date >= start_date)
    
    if staff_id:
        loan_collection_query = loan_collection_query.filter_by(staff_id=staff_id)
        saving_collection_query = saving_collection_query.filter_by(staff_id=staff_id)
    
    loan_collections = loan_collection_query.all()
    saving_collections = saving_collection_query.all()
    
    total_loans = sum(l.amount for l in loan_collections)
    total_savings = sum(s.amount for s in saving_collections)
    total_payments = total_loans
    
    staffs = User.query.filter_by(role='staff').all()
    
    return render_template('reports.html', 
                         loan_collections=loan_collections, saving_collections=saving_collections,
                         total_loans=total_loans, total_savings=total_savings, 
                         total_payments=total_payments, staffs=staffs, period=period)

@app.route('/reports/export/csv')
@login_required
def export_csv():
    period = request.args.get('period', 'daily')
    staff_id = request.args.get('staff_id', type=int)
    
    today = datetime.now()
    if period == 'daily':
        start_date = today.replace(hour=0, minute=0, second=0)
    elif period == 'weekly':
        start_date = today - timedelta(days=7)
    else:
        start_date = today - timedelta(days=30)
    
    loan_collection_query = LoanCollection.query.filter(LoanCollection.collection_date >= start_date)
    saving_collection_query = SavingCollection.query.filter(SavingCollection.collection_date >= start_date)
    
    if staff_id:
        loan_collection_query = loan_collection_query.filter_by(staff_id=staff_id)
        saving_collection_query = saving_collection_query.filter_by(staff_id=staff_id)
    
    loan_collections = loan_collection_query.all()
    saving_collections = saving_collection_query.all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(['LOAN COLLECTIONS REPORT'])
    writer.writerow(['Customer', 'Amount', 'Date', 'Staff'])
    for lc in loan_collections:
        writer.writerow([lc.customer.name, lc.amount, 
                        lc.collection_date.strftime('%Y-%m-%d %H:%M'), 
                        lc.staff.name if lc.staff else 'N/A'])
    
    writer.writerow([])
    writer.writerow(['SAVINGS COLLECTIONS REPORT'])
    writer.writerow(['Customer', 'Amount', 'Date', 'Staff'])
    for sc in saving_collections:
        writer.writerow([sc.customer.name, sc.amount, 
                        sc.collection_date.strftime('%Y-%m-%d %H:%M'), 
                        sc.staff.name if sc.staff else 'N/A'])
    
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=report_{period}.csv'
    response.headers['Content-Type'] = 'text/csv'
    return response

@app.route('/customers')
@login_required
def manage_customers():
    if current_user.role == 'staff' and not current_user.is_office_staff:
        customers = Customer.query.filter_by(staff_id=current_user.id).all()
    else:
        customers = Customer.query.all()
    return render_template('manage_customers.html', customers=customers)

@app.route('/all_customers_print')
@login_required
def all_customers_print():
    if current_user.role == 'staff' and not current_user.is_office_staff:
        customers = Customer.query.filter_by(staff_id=current_user.id).order_by(Customer.member_no).all()
    else:
        customers = Customer.query.order_by(Customer.member_no).all()
    return render_template('all_customers_print.html', customers=customers)

@app.route('/loan_customers')
@login_required
def loan_customers():
    if current_user.role == 'staff' and not current_user.is_office_staff:
        customers = Customer.query.filter_by(staff_id=current_user.id).filter(Customer.total_loan > 0).all()
    else:
        customers = Customer.query.filter(Customer.total_loan > 0).all()
    return render_template('loan_customers.html', customers=customers)

@app.route('/customer_details/<int:id>')
@login_required
def customer_details(id):
    customer = Customer.query.get_or_404(id)
    
    if current_user.role == 'staff' and customer.staff_id != current_user.id:
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    loan_collections = LoanCollection.query.filter_by(customer_id=id).all()
    saving_collections = SavingCollection.query.filter_by(customer_id=id).all()
    withdrawals = Withdrawal.query.filter_by(customer_id=id).order_by(Withdrawal.date.desc()).all() if hasattr(Withdrawal, 'customer_id') else []
    
    collections_dict = {}
    for lc in loan_collections:
        key = (lc.collection_date, lc.staff.name)
        if key not in collections_dict:
            collections_dict[key] = {'loan': 0, 'saving': 0, 'date': lc.collection_date, 'staff': lc.staff.name}
        collections_dict[key]['loan'] += lc.amount
    
    for sc in saving_collections:
        key = (sc.collection_date, sc.staff.name)
        if key not in collections_dict:
            collections_dict[key] = {'loan': 0, 'saving': 0, 'date': sc.collection_date, 'staff': sc.staff.name}
        collections_dict[key]['saving'] += sc.amount
    
    all_collections = sorted(collections_dict.values(), key=lambda x: x['date'], reverse=True)
    total_collected = sum(lc.amount for lc in loan_collections)
    total_withdrawn = sum(w.amount for w in withdrawals)
    
    return render_template('customer_details.html', customer=customer, all_collections=all_collections, total_collected=total_collected, withdrawals=withdrawals, total_withdrawn=total_withdrawn)

@app.route('/customer_details_print/<int:id>')
@login_required
def customer_details_print(id):
    customer = Customer.query.get_or_404(id)
    loan_collections = LoanCollection.query.filter_by(customer_id=id).all()
    saving_collections = SavingCollection.query.filter_by(customer_id=id).all()
    withdrawals = Withdrawal.query.filter_by(customer_id=id).order_by(Withdrawal.date.desc()).all() if hasattr(Withdrawal, 'customer_id') else []
    
    collections_dict = {}
    for lc in loan_collections:
        key = (lc.collection_date, lc.staff.name)
        if key not in collections_dict:
            collections_dict[key] = {'loan': 0, 'saving': 0, 'date': lc.collection_date, 'staff': lc.staff.name}
        collections_dict[key]['loan'] += lc.amount
    
    for sc in saving_collections:
        key = (sc.collection_date, sc.staff.name)
        if key not in collections_dict:
            collections_dict[key] = {'loan': 0, 'saving': 0, 'date': sc.collection_date, 'staff': sc.staff.name}
        collections_dict[key]['saving'] += sc.amount
    
    all_collections = sorted(collections_dict.values(), key=lambda x: x['date'], reverse=True)
    total_loan_collected = sum(lc.amount for lc in loan_collections)
    total_saving_collected = sum(sc.amount for sc in saving_collections)
    total_withdrawn = sum(w.amount for w in withdrawals)
    return render_template('customer_details_print.html', customer=customer, all_collections=all_collections, withdrawals=withdrawals, total_loan_collected=total_loan_collected, total_saving_collected=total_saving_collected, total_withdrawn=total_withdrawn)

@app.route('/customer/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    
    if current_user.role == 'staff' and customer.staff_id != current_user.id:
        flash('Access denied!', 'danger')
        return redirect(url_for('manage_customers'))
    
    if request.method == 'POST':
        customer.name = request.form.get('name', '').strip()
        customer.member_no = request.form.get('member_no', '')
        customer.phone = request.form.get('phone', '').strip()
        customer.father_husband = request.form.get('father_husband', '')
        customer.village = request.form.get('village', '')
        customer.post = request.form.get('post', '')
        customer.thana = request.form.get('thana', '')
        customer.district = request.form.get('district', '')
        customer.granter = request.form.get('granter', '')
        customer.profession = request.form.get('profession', '')
        customer.nid_no = request.form.get('nid_no', '')
        customer.address = request.form.get('address', '')
        
        if not customer.name or not customer.phone:
            flash('নাম এবং ফোন নম্বর আবশ্যক!', 'danger')
            return redirect(url_for('edit_customer', id=id))
        
        db.session.commit()
        flash('কাস্টমার আপডেট সফল হয়েছে!', 'success')
        return redirect(url_for('manage_customers'))
    
    return render_template('edit_customer.html', customer=customer)

@app.route('/customer/delete/<int:id>')
@login_required
def delete_customer(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('manage_customers'))
    
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    flash('Customer deleted successfully!', 'success')
    return redirect(url_for('manage_customers'))

@app.route('/customer/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            phone = request.form.get('phone', '').strip()
            
            if not name or not phone:
                flash('নাম এবং ফোন নম্বর আবশ্যক!', 'danger')
                return redirect(url_for('add_customer'))
            
            # Safe float conversion with default 0
            admission_fee_str = request.form.get('admission_fee', '0').strip()
            admission_fee = float(admission_fee_str) if admission_fee_str else 0.0
            
            cash_balance_record = CashBalance.query.first()
            if not cash_balance_record:
                cash_balance_record = CashBalance(balance=0)
                db.session.add(cash_balance_record)
            
            cash_balance_record.balance += admission_fee
            
            customer = Customer(
                name=name,
                member_no=request.form.get('member_no', ''),
                phone=phone,
                father_husband=request.form.get('father_husband', ''),
                village=request.form.get('village', ''),
                post=request.form.get('post', ''),
                thana=request.form.get('thana', ''),
                district=request.form.get('district', ''),
                granter=request.form.get('granter', ''),
                profession=request.form.get('profession', ''),
                nid_no=request.form.get('nid_no', ''),
                admission_fee=admission_fee,
                welfare_fee=0.0,
                application_fee=0.0,
                address=request.form.get('address', ''),
                staff_id=current_user.id
            )
            db.session.add(customer)
            db.session.flush()
            
            if admission_fee > 0:
                fee_col = FeeCollection(customer_id=customer.id, fee_type='admission', amount=admission_fee, collected_by=current_user.id)
                db.session.add(fee_col)
            
            db.session.commit()
            flash(f'সদস্য সফলভাবে যোগ হয়েছে! ভর্তি ফি: ৳{admission_fee}', 'success')
            return redirect(url_for('manage_customers'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('add_customer'))
    return render_template('add_customer.html')

@app.route('/collections')
@login_required
def manage_collections():
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    
    if current_user.role == 'staff' and not current_user.is_office_staff:
        query_loan = LoanCollection.query.filter_by(staff_id=current_user.id)
        query_saving = SavingCollection.query.filter_by(staff_id=current_user.id)
    else:
        query_loan = LoanCollection.query
        query_saving = SavingCollection.query
    
    if from_date:
        try:
            from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
            query_loan = query_loan.filter(LoanCollection.collection_date >= from_datetime)
            query_saving = query_saving.filter(SavingCollection.collection_date >= from_datetime)
        except ValueError:
            flash('Invalid from date format!', 'danger')
    
    if to_date:
        try:
            to_datetime = datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_loan = query_loan.filter(LoanCollection.collection_date <= to_datetime)
            query_saving = query_saving.filter(SavingCollection.collection_date <= to_datetime)
        except ValueError:
            flash('Invalid to date format!', 'danger')
    
    loan_collections = query_loan.order_by(LoanCollection.collection_date.desc()).all()
    saving_collections = query_saving.order_by(SavingCollection.collection_date.desc()).all()
    
    all_collections = []
    for lc in loan_collections:
        all_collections.append({
            'type': 'Loan',
            'customer': lc.customer,
            'amount': lc.amount,
            'date': lc.collection_date,
            'staff': lc.staff
        })
    
    for sc in saving_collections:
        all_collections.append({
            'type': 'Saving',
            'customer': sc.customer,
            'amount': sc.amount,
            'date': sc.collection_date,
            'staff': sc.staff
        })
    
    all_collections.sort(key=lambda x: x['date'], reverse=True)
    total_loan = sum(lc.amount for lc in loan_collections)
    total_saving = sum(sc.amount for sc in saving_collections)
    
    return render_template('manage_collections.html', all_collections=all_collections, total_loan=total_loan, total_saving=total_saving, from_date=from_date, to_date=to_date)

@app.route('/collection/add', methods=['GET', 'POST'])
@login_required
def add_collection():
    if request.method == 'POST':
        loan_id = request.form.get('loan_id', type=int)
        amount = request.form.get('amount', type=float, default=0)
        
        if not loan_id or amount <= 0:
            flash('সব তথ্য সঠিকভাবে পূরণ করুন!', 'danger')
            return redirect(url_for('add_collection'))
        
        collection = Collection(
            loan_id=loan_id,
            amount=amount,
            staff_id=current_user.id
        )
        db.session.add(collection)
        db.session.commit()
        flash('Collection recorded successfully!', 'success')
        return redirect(url_for('manage_collections'))
    
    if current_user.role == 'staff':
        loans = Loan.query.filter_by(staff_id=current_user.id, status='Pending').all()
    else:
        loans = Loan.query.filter_by(status='Pending').all()
    return render_template('add_collection.html', loans=loans)

@app.route('/collection', methods=['GET', 'POST'])
@login_required
def collection():
    if request.method == 'POST':
        customer_id = request.form.get('customer_id', type=int)
        loan_amount = request.form.get('loan_amount', type=float, default=0)
        saving_amount = request.form.get('saving_amount', type=float, default=0)
        
        if not customer_id:
            flash('গ্রাহক নির্বাচন করুন!', 'danger')
            return redirect(url_for('collection'))
        
        if loan_amount <= 0 and saving_amount <= 0:
            flash('অন্তত একটি কালেকশন পরিমাণ দিন!', 'danger')
            return redirect(url_for('collection'))
        
        customer = Customer.query.get_or_404(customer_id)
        
        cash_balance_record = CashBalance.query.first()
        if not cash_balance_record:
            cash_balance_record = CashBalance(balance=0)
            db.session.add(cash_balance_record)
        
        # Process loan collection
        if loan_amount > 0:
            if loan_amount > customer.remaining_loan:
                flash(f'লোন টাকা বাকি লোন (৳{customer.remaining_loan}) থেকে বেশি হতে পারবে না!', 'danger')
                return redirect(url_for('collection'))
            
            loan_collection = LoanCollection(
                customer_id=customer_id,
                amount=loan_amount,
                staff_id=current_user.id
            )
            customer.remaining_loan -= loan_amount
            cash_balance_record.balance += loan_amount
            db.session.add(loan_collection)
        
        # Process saving collection
        if saving_amount > 0:
            saving_collection = SavingCollection(
                customer_id=customer_id,
                amount=saving_amount,
                staff_id=current_user.id
            )
            customer.savings_balance += saving_amount
            cash_balance_record.balance += saving_amount
            db.session.add(saving_collection)
        
        db.session.commit()
        
        msg = []
        if loan_amount > 0:
            msg.append(f'লোন: ৳{loan_amount}')
        if saving_amount > 0:
            msg.append(f'সেভিংস: ৳{saving_amount}')
        flash(f'সফলভাবে কালেকশন সম্পন্ন হয়েছে! {" | ".join(msg)}', 'success')
        return redirect(url_for('collection'))
    
    if current_user.role == 'staff' and not current_user.is_office_staff:
        customers = Customer.query.filter_by(staff_id=current_user.id).all()
    else:
        customers = Customer.query.all()
    return render_template('collection.html', customers=customers)

@app.route('/loan_collection', methods=['GET'])
@login_required
def loan_collection():
    if current_user.role == 'staff' and not current_user.is_office_staff:
        customers = Customer.query.filter_by(staff_id=current_user.id).filter(Customer.remaining_loan > 0).all()
    else:
        customers = Customer.query.filter(Customer.remaining_loan > 0).all()
    return render_template('loan_collection.html', customers=customers)

@app.route('/saving_collection', methods=['GET'])
@login_required
def saving_collection():
    if current_user.role == 'staff' and not current_user.is_office_staff:
        customers = Customer.query.filter_by(staff_id=current_user.id).all()
    else:
        customers = Customer.query.all()
    return render_template('saving_collection.html', customers=customers)

@app.route('/loan_collection/collect', methods=['POST'])
@login_required
def collect_loan():
    try:
        customer_id = request.form.get('customer_id', type=int)
        amount = request.form.get('amount', type=float, default=0)
        
        if not customer_id or amount <= 0:
            flash('সব তথ্য সঠিকভাবে পূরণ করুন!', 'danger')
            return redirect(url_for('loan_collection'))
        
        customer = Customer.query.get_or_404(customer_id)
        
        if amount <= 0:
            flash('টাকার পরিমাণ ০ এর বেশি হতে হবে!', 'danger')
            return redirect(url_for('loan_collection'))
        
        if amount > customer.remaining_loan:
            flash(f'টাকা বাকি লোন (৳{customer.remaining_loan}) থেকে বেশি হতে পারবে না!', 'danger')
            return redirect(url_for('loan_collection'))
        
        collection = LoanCollection(
            customer_id=customer_id,
            amount=amount,
            staff_id=current_user.id
        )
        
        customer.remaining_loan -= amount
        
        cash_balance_record = CashBalance.query.first()
        if not cash_balance_record:
            cash_balance_record = CashBalance(balance=0)
            db.session.add(cash_balance_record)
        cash_balance_record.balance += amount
        
        db.session.add(collection)
        db.session.commit()
        
        flash(f'সফলভাবে ৳{amount} কালেকশন সম্পন্ন হয়েছে! বাকি: ৳{customer.remaining_loan}', 'success')
        return redirect(url_for('loan_collection'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('loan_collection'))

@app.route('/saving_collection/collect', methods=['POST'])
@login_required
def collect_saving():
    try:
        customer_id = request.form.get('customer_id', type=int)
        amount = request.form.get('amount', type=float, default=0)
        
        if not customer_id or amount <= 0:
            flash('সব তথ্য সঠিকভাবে পূরণ করুন!', 'danger')
            return redirect(url_for('saving_collection'))
        
        customer = Customer.query.get_or_404(customer_id)
        
        collection = SavingCollection(
            customer_id=customer_id,
            amount=amount,
            staff_id=current_user.id
        )
        
        customer.savings_balance += amount
        
        cash_balance_record = CashBalance.query.first()
        if not cash_balance_record:
            cash_balance_record = CashBalance(balance=0)
            db.session.add(cash_balance_record)
        cash_balance_record.balance += amount
        
        db.session.add(collection)
        db.session.commit()
        
        flash(f'সফলভাবে ৳{amount} সেভিংস জমা হয়েছে!', 'success')
        return redirect(url_for('saving_collection'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('saving_collection'))

@app.route('/daily_collections')
@login_required
def daily_collections():
    from datetime import date
    today_date = date.today()
    
    if current_user.role == 'staff' and not current_user.is_office_staff:
        # Get all collections for this staff (for testing)
        all_loan = LoanCollection.query.filter_by(staff_id=current_user.id).all()
        all_saving = SavingCollection.query.filter_by(staff_id=current_user.id).all()
        
        # Get today's collections
        loan_collections = [lc for lc in all_loan if lc.collection_date.date() == today_date]
        saving_collections = [sc for sc in all_saving if sc.collection_date.date() == today_date]
    else:
        all_loan = LoanCollection.query.all()
        all_saving = SavingCollection.query.all()
        
        loan_collections = [lc for lc in all_loan if lc.collection_date.date() == today_date]
        saving_collections = [sc for sc in all_saving if sc.collection_date.date() == today_date]
    
    total_loan = sum(lc.amount for lc in loan_collections)
    total_saving = sum(sc.amount for sc in saving_collections)
    
    return render_template('daily_collections.html', loan_collections=loan_collections, saving_collections=saving_collections, total_loan=total_loan, total_saving=total_saving)

@app.route('/cash_balance', methods=['GET', 'POST'])
@login_required
def manage_cash_balance():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            action = request.form.get('action', '')
            amount = request.form.get('amount', type=float, default=0)
            
            if not action or amount <= 0:
                flash('সব তথ্য সঠিকভাবে পূরণ করুন!', 'danger')
                return redirect(url_for('manage_cash_balance'))
            
            cash_balance_record = CashBalance.query.first()
            if not cash_balance_record:
                cash_balance_record = CashBalance(balance=0)
                db.session.add(cash_balance_record)
            
            if action == 'add':
                investor_name = request.form.get('investor_name', '').strip()
                note = request.form.get('note', '')
                
                if not investor_name:
                    flash('Investor নাম আবশ্যক!', 'danger')
                    return redirect(url_for('manage_cash_balance'))
                
                # Find or create investor
                investor = Investor.query.filter_by(name=investor_name).first()
                if not investor:
                    last_investor = Investor.query.order_by(Investor.id.desc()).first()
                    if last_investor:
                        last_num = int(last_investor.investor_id.split('-')[1])
                        investor_id = f'INV-{last_num + 1:04d}'
                    else:
                        investor_id = 'INV-0001'
                    
                    investor = Investor(
                        investor_id=investor_id,
                        name=investor_name
                    )
                    db.session.add(investor)
                    db.session.flush()
                
                investment = Investment(
                    investor_id=investor.id,
                    investor_name=investor_name,
                    amount=amount,
                    note=note
                )
                investor.total_investment += amount
                investor.current_balance += amount
                cash_balance_record.balance += amount
                db.session.add(investment)
                flash(f'Investor ID: {investor.investor_id} | ৳{amount} যোগ করা হয়েছে! Balance: ৳{investor.current_balance}', 'success')
            elif action == 'subtract':
                if cash_balance_record.balance >= amount:
                    cash_balance_record.balance -= amount
                    flash(f'৳{amount} বিয়োগ করা হয়েছে!', 'success')
                else:
                    flash('পর্যাপ্ত টাকা নেই!', 'danger')
            elif action == 'withdraw':
                investor_name = request.form.get('investor_name', '').strip()
                note = request.form.get('note', '')
                
                if not investor_name:
                    flash('Investor নাম আবশ্যক!', 'danger')
                    return redirect(url_for('manage_cash_balance'))
                
                if cash_balance_record.balance >= amount:
                    investor = Investor.query.filter_by(name=investor_name).first()
                    if not investor:
                        flash('Investor খুঁজে পাওয়া যায়নি!', 'danger')
                        return redirect(url_for('manage_cash_balance'))
                    
                    if investor.current_balance < amount:
                        flash(f'Investor এর balance (৳{investor.current_balance}) যথেষ্ট নয়!', 'danger')
                        return redirect(url_for('manage_cash_balance'))
                    
                    withdrawal = Withdrawal(
                        investor_id=investor.id,
                        investor_name=investor_name,
                        amount=amount,
                        note=note
                    )
                    investor.total_withdrawal += amount
                    investor.current_balance -= amount
                    cash_balance_record.balance -= amount
                    db.session.add(withdrawal)
                    flash(f'Investor ID: {investor.investor_id} | ৳{amount} Withdrawal সফল হয়েছে! Balance: ৳{investor.current_balance}', 'success')
                else:
                    flash('পর্যাপ্ত টাকা নেই!', 'danger')
            
            db.session.commit()
            return redirect(url_for('manage_cash_balance'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('manage_cash_balance'))
    
    cash_balance_record = CashBalance.query.first()
    cash_balance = cash_balance_record.balance if cash_balance_record else 0
    investments = Investment.query.order_by(Investment.date.desc()).all()
    withdrawals = Withdrawal.query.order_by(Withdrawal.date.desc()).all()
    investors = Investor.query.all()
    total_investment = db.session.query(db.func.sum(Investment.amount)).scalar() or 0
    total_withdrawal = db.session.query(db.func.sum(Withdrawal.amount)).scalar() or 0
    return render_template('manage_cash_balance.html', cash_balance=cash_balance, investments=investments, withdrawals=withdrawals, investors=investors, total_investment=total_investment, total_withdrawal=total_withdrawal)

@app.route('/expenses', methods=['GET', 'POST'])
@login_required
def manage_expenses():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            category = request.form.get('category', '')
            amount = request.form.get('amount', type=float, default=0)
            description = request.form.get('description', '')
            expense_date_str = request.form.get('expense_date')
            
            if not category or amount <= 0:
                flash('সব তথ্য সঠিকভাবে পূরণ করুন!', 'danger')
                return redirect(url_for('manage_expenses'))
            
            cash_balance_record = CashBalance.query.first()
            if not cash_balance_record:
                cash_balance_record = CashBalance(balance=0)
                db.session.add(cash_balance_record)
            
            if cash_balance_record.balance >= amount:
                expense_date = datetime.strptime(expense_date_str, '%Y-%m-%d') if expense_date_str else datetime.now()
                expense = Expense(
                    category=category,
                    amount=amount,
                    description=description,
                    date=expense_date
                )
                cash_balance_record.balance -= amount
                db.session.add(expense)
                db.session.commit()
                flash(f'{category} - ৳{amount} ব্যয় সফল হয়েছে!', 'success')
            else:
                flash('পর্যাপ্ত টাকা নেই!', 'danger')
            
            return redirect(url_for('manage_expenses'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('manage_expenses'))
    
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    
    query = Expense.query
    if from_date:
        try:
            from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(Expense.date >= from_datetime)
        except ValueError:
            flash('Invalid from date!', 'danger')
    if to_date:
        try:
            to_datetime = datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(Expense.date <= to_datetime)
        except ValueError:
            flash('Invalid to date!', 'danger')
    
    expenses = query.order_by(Expense.date.desc()).all()
    total_expenses = sum(e.amount for e in expenses)
    
    salary_total = sum(e.amount for e in expenses if e.category == 'Salary')
    office_total = sum(e.amount for e in expenses if e.category == 'Office')
    transport_total = sum(e.amount for e in expenses if e.category == 'Transport')
    other_total = sum(e.amount for e in expenses if e.category == 'Other')
    
    cash_balance_record = CashBalance.query.first()
    cash_balance = cash_balance_record.balance if cash_balance_record else 0
    
    return render_template('manage_expenses.html', expenses=expenses, total_expenses=total_expenses, salary_total=salary_total, office_total=office_total, transport_total=transport_total, other_total=other_total, cash_balance=cash_balance, from_date=from_date, to_date=to_date)

@app.route('/expenses_print')
@login_required
def expenses_print():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    
    query = Expense.query
    if from_date:
        try:
            from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(Expense.date >= from_datetime)
        except ValueError:
            pass
    if to_date:
        try:
            to_datetime = datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(Expense.date <= to_datetime)
        except ValueError:
            pass
    
    expenses = query.order_by(Expense.date.desc()).all()
    total_expenses = sum(e.amount for e in expenses)
    
    by_category = {
        'Salary': sum(e.amount for e in expenses if e.category == 'Salary'),
        'Office': sum(e.amount for e in expenses if e.category == 'Office'),
        'Transport': sum(e.amount for e in expenses if e.category == 'Transport'),
        'Other': sum(e.amount for e in expenses if e.category == 'Other')
    }
    
    return render_template('expenses_print.html', expenses=expenses, total_expenses=total_expenses, by_category=by_category, from_date=from_date, to_date=to_date)

@app.route('/profit_loss')
@login_required
def profit_loss():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    from datetime import datetime
    
    period = request.args.get('period', 'monthly')
    
    today = datetime.now()
    if period == 'monthly':
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:  # yearly
        start_date = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Income: Loan Collections + Savings Collections
    loan_collections = LoanCollection.query.filter(LoanCollection.collection_date >= start_date).all()
    saving_collections = SavingCollection.query.filter(SavingCollection.collection_date >= start_date).all()
    
    total_loan_collected = sum(lc.amount for lc in loan_collections)
    total_savings_collected = sum(sc.amount for sc in saving_collections)
    total_income = total_loan_collected + total_savings_collected
    
    # Expenses
    expenses = Expense.query.filter(Expense.date >= start_date).all()
    total_expenses = sum(exp.amount for exp in expenses)
    
    # Withdrawals
    withdrawals = Withdrawal.query.filter(Withdrawal.date >= start_date).all()
    total_withdrawals = sum(wd.amount for wd in withdrawals)
    
    # Loans Given (money out)
    loans_given = Loan.query.filter(Loan.loan_date >= start_date).all()
    total_loans_given = sum(loan.amount for loan in loans_given)
    
    # Net Profit/Loss = Income - (Expenses + Withdrawals + Loans Given)
    net_profit = total_income - (total_expenses + total_withdrawals + total_loans_given)
    
    # Category-wise expenses
    salary_exp = sum(exp.amount for exp in expenses if exp.category == 'Salary')
    office_exp = sum(exp.amount for exp in expenses if exp.category == 'Office')
    transport_exp = sum(exp.amount for exp in expenses if exp.category == 'Transport')
    other_exp = sum(exp.amount for exp in expenses if exp.category == 'Other')
    
    return render_template('profit_loss.html', 
                         period=period,
                         total_income=total_income,
                         total_loan_collected=total_loan_collected,
                         total_savings_collected=total_savings_collected,
                         total_expenses=total_expenses,
                         total_withdrawals=total_withdrawals,
                         total_loans_given=total_loans_given,
                         net_profit=net_profit,
                         salary_exp=salary_exp,
                         office_exp=office_exp,
                         transport_exp=transport_exp,
                         other_exp=other_exp)

@app.route('/messages')
@login_required
def view_messages():
    if current_user.role == 'staff':
        messages = Message.query.filter_by(staff_id=current_user.id).order_by(Message.created_date.desc()).all()
        return render_template('staff_messages.html', messages=messages)
    else:
        staffs = User.query.filter_by(role='staff').all()
        return render_template('admin_messages.html', staffs=staffs)

@app.route('/message/send', methods=['POST'])
@login_required
def send_message():
    if current_user.role == 'admin':
        staff_id = request.form.get('staff_id', type=int)
        content = request.form.get('content', '').strip()
        
        if not staff_id or not content:
            flash('সব তথ্য সঠিকভাবে পূরণ করুন!', 'danger')
            return redirect(url_for('view_messages'))
        message = Message(staff_id=staff_id, content=content)
        db.session.add(message)
        db.session.commit()
        flash('Message sent successfully!', 'success')
    return redirect(url_for('view_messages'))

@app.route('/message/read/<int:id>')
@login_required
def mark_message_read(id):
    message = Message.query.get_or_404(id)
    if message.staff_id == current_user.id:
        message.is_read = True
        db.session.commit()
    return redirect(url_for('view_messages'))

@app.route('/manage_investors')
@login_required
def manage_investors():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    investors = Investor.query.order_by(Investor.investor_id).all()
    return render_template('manage_investors.html', investors=investors)

@app.route('/manage_withdrawals', methods=['GET', 'POST'])
@login_required
def manage_withdrawals():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            customer_id = request.form.get('customer_id', type=int)
            amount = request.form.get('amount', type=float, default=0)
            note = request.form.get('note', '')
            
            if not customer_id or amount <= 0:
                flash('সব তথ্য সঠিকভাবে পূরণ করুন!', 'danger')
                return redirect(url_for('manage_withdrawals'))
            
            customer = Customer.query.get_or_404(customer_id)
            
            if customer.savings_balance < amount:
                flash(f'পর্যাপ্ত সেভিংস নেই! বর্তমান: ৳{customer.savings_balance}', 'danger')
                return redirect(url_for('manage_withdrawals'))
            
            cash_balance_record = CashBalance.query.first()
            if not cash_balance_record or cash_balance_record.balance < amount:
                flash('পর্যাপ্ত ক্যাশ নেই!', 'danger')
                return redirect(url_for('manage_withdrawals'))
            
            withdrawal = Withdrawal(
                customer_id=customer_id,
                amount=amount,
                note=note,
                withdrawal_type='savings'
            )
            customer.savings_balance -= amount
            cash_balance_record.balance -= amount
            db.session.add(withdrawal)
            db.session.commit()
            flash(f'৳{amount} উত্তোলন সফল হয়েছে!', 'success')
            return redirect(url_for('manage_withdrawals'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('manage_withdrawals'))
    
    withdrawals = Withdrawal.query.order_by(Withdrawal.date.desc()).all()
    customers = Customer.query.all()
    cash_balance_record = CashBalance.query.first()
    cash_balance = cash_balance_record.balance if cash_balance_record else 0
    total_withdrawal = sum(w.amount for w in withdrawals)
    savings_withdrawal = sum(w.amount for w in withdrawals if hasattr(w, 'withdrawal_type') and w.withdrawal_type == 'savings')
    investment_withdrawal = total_withdrawal - savings_withdrawal
    return render_template('manage_withdrawals.html', withdrawals=withdrawals, customers=customers, cash_balance=cash_balance, total_withdrawal=total_withdrawal, savings_withdrawal=savings_withdrawal, investment_withdrawal=investment_withdrawal)

@app.route('/daily_report')
@login_required
def daily_report():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    from datetime import date
    report_date_str = request.args.get('date', '')
    if report_date_str:
        try:
            today = datetime.strptime(report_date_str, '%Y-%m-%d').date()
        except:
            today = date.today()
    else:
        today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    
    loan_collections = LoanCollection.query.filter(LoanCollection.collection_date >= today_start).all()
    saving_collections = SavingCollection.query.filter(SavingCollection.collection_date >= today_start).all()
    loans_given = Loan.query.filter(Loan.loan_date >= today_start).all()
    withdrawals = Withdrawal.query.filter(Withdrawal.date >= today_start).all()
    expenses = Expense.query.filter(Expense.date >= today_start).all()
    customers_added_today = Customer.query.filter(Customer.created_date >= today_start).all()
    
    total_installment = sum(lc.amount for lc in loan_collections)
    total_saving = sum(sc.amount for sc in saving_collections)
    total_loan_distributed = sum(l.amount for l in loans_given)
    total_withdrawal = sum(w.amount for w in withdrawals)
    total_expense = sum(e.amount for e in expenses)
    total_application_fee = sum(l.service_charge for l in loans_given)
    total_welfare_fee = 0
    total_admission_fee = sum(c.admission_fee for c in customers_added_today)
    total_outflow = total_loan_distributed + total_withdrawal + total_expense
    
    customers = Customer.query.order_by(Customer.member_no).all()
    collections = []
    for customer in customers:
        loan_amount = sum(lc.amount for lc in loan_collections if lc.customer_id == customer.id)
        saving_amount = sum(sc.amount for sc in saving_collections if sc.customer_id == customer.id)
        collections.append({'customer': customer, 'loan_amount': loan_amount, 'saving_amount': saving_amount})
    
    return render_template('daily_report.html', report_date=today.strftime('%d-%m-%Y'), selected_date=today.strftime('%Y-%m-%d'), total_installment=total_installment, total_saving=total_saving, total_welfare_fee=total_welfare_fee, total_admission_fee=total_admission_fee, total_application_fee=total_application_fee, total_expense=total_expense, collections=collections, total_loan_distributed=total_loan_distributed, total_withdrawal=total_withdrawal, total_outflow=total_outflow)

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
    
    month_names = ['', 'জানুয়ারি', 'ফেব্রুয়ারি', 'মার্চ', 'এপ্রিল', 'মে', 'জুন', 'জুলাই', 'আগস্ট', 'সেপ্টেম্বর', 'অক্টোবর', 'নভেম্বর', 'ডিসেম্বর']
    month_name = month_names[month]
    last_day = calendar.monthrange(year, month)[1]
    
    month_start = datetime(year, month, 1)
    month_end = datetime(year, month, last_day, 23, 59, 59)
    
    daily_data = {}
    running_balance = 0
    
    for day in range(1, last_day + 1):
        day_start = datetime(year, month, day)
        day_end = datetime(year, month, day, 23, 59, 59)
        
        loan_collections = LoanCollection.query.filter(LoanCollection.collection_date >= day_start, LoanCollection.collection_date <= day_end).all()
        saving_collections = SavingCollection.query.filter(SavingCollection.collection_date >= day_start, SavingCollection.collection_date <= day_end).all()
        loans_given = Loan.query.filter(Loan.loan_date >= day_start, Loan.loan_date <= day_end).all()
        withdrawals = Withdrawal.query.filter(Withdrawal.date >= day_start, Withdrawal.date <= day_end).all()
        expenses = Expense.query.filter(Expense.date >= day_start, Expense.date <= day_end).all()
        customers_added = Customer.query.filter(Customer.created_date >= day_start, Customer.created_date <= day_end).all()
        investments = Investment.query.filter(Investment.date >= day_start, Investment.date <= day_end).all()
        
        installments = sum(lc.amount for lc in loan_collections)
        savings = sum(sc.amount for sc in saving_collections)
        loan_given = sum(l.amount for l in loans_given)
        interest = sum((l.amount * l.interest / 100) for l in loans_given)
        service_charge = sum(l.service_charge for l in loans_given)
        admission_fee = sum(c.admission_fee for c in customers_added)
        welfare_fee = 0
        loan_with_interest = loan_given + interest
        savings_return = sum(w.amount for w in withdrawals)
        expenses_total = sum(e.amount for e in expenses)
        investment_amount = sum(inv.amount for inv in investments)
        
        total_income = installments + savings + service_charge + admission_fee + welfare_fee
        total_expense = loan_given + savings_return + expenses_total
        day_balance = total_income - total_expense
        running_balance += day_balance
        
        daily_data[day] = {
            'savings': savings,
            'installments': installments,
            'welfare_fee': welfare_fee,
            'admission_fee': admission_fee,
            'service_charge': service_charge,
            'capital_savings': investment_amount,
            'loan_given': loan_given,
            'interest': interest,
            'loan_with_interest': loan_with_interest,
            'savings_return': savings_return,
            'expenses': expenses_total,
            'total_expense': total_expense,
            'balance': running_balance
        }
    
    total_capital_savings = sum(d['capital_savings'] for d in daily_data.values())
    total_loan_distributed = sum(d['loan_given'] for d in daily_data.values())
    total_interest = sum(d['interest'] for d in daily_data.values())
    current_remaining = db.session.query(db.func.sum(Customer.remaining_loan)).scalar() or 0
    prev_remaining = current_remaining + total_capital_savings - total_loan_distributed
    total_monthly_expenses = sum(d['expenses'] for d in daily_data.values())
    
    return render_template('monthly_report.html', month=month, month_name=month_name, year=year, daily_data=daily_data, last_day=last_day, total_capital_savings=total_capital_savings, total_loan_distributed=total_loan_distributed, total_interest=total_interest, prev_remaining=prev_remaining, current_remaining=current_remaining, total_monthly_expenses=total_monthly_expenses)

@app.route('/withdrawal_report')
@login_required
def withdrawal_report():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    withdrawals = Withdrawal.query.order_by(Withdrawal.date.desc()).all()
    total = sum(w.amount for w in withdrawals)
    savings_total = sum(w.amount for w in withdrawals if hasattr(w, 'withdrawal_type') and w.withdrawal_type == 'savings')
    investment_total = total - savings_total
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    return render_template('withdrawal_report.html', withdrawals=withdrawals, total=total, savings_total=savings_total, investment_total=investment_total, from_date=from_date, to_date=to_date)

@app.route('/fee_history/<fee_type>')
@login_required
def fee_history(fee_type):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    fee_types = {'admission': 'ভর্তি ফি', 'welfare': 'কল্যাণ ফি', 'application': 'আবেদন ফি'}
    if fee_type not in fee_types:
        flash('Invalid fee type!', 'danger')
        return redirect(url_for('dashboard'))
    
    fees = FeeCollection.query.filter_by(fee_type=fee_type).order_by(FeeCollection.collection_date.desc()).all()
    total = sum(f.amount for f in fees)
    return render_template('fee_history.html', fees=fees, total=total, fee_type=fee_type, fee_name=fee_types[fee_type])

@app.route('/all_fees_history')
@login_required
def all_fees_history():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    fees = FeeCollection.query.order_by(FeeCollection.collection_date.desc()).all()
    admission_total = sum(f.amount for f in fees if f.fee_type == 'admission')
    welfare_total = sum(f.amount for f in fees if f.fee_type == 'welfare')
    application_total = sum(f.amount for f in fees if f.fee_type == 'application')
    total = admission_total + welfare_total + application_total
    return render_template('all_fees_history.html', fees=fees, total=total, admission_total=admission_total, welfare_total=welfare_total, application_total=application_total)

@app.route('/due_report')
@login_required
def due_report():
    if current_user.role == 'staff' and not current_user.is_office_staff:
        customers = Customer.query.filter_by(staff_id=current_user.id).filter(Customer.remaining_loan > 0).all()
    else:
        customers = Customer.query.filter(Customer.remaining_loan > 0).all()
    
    due_data = []
    for customer in customers:
        loans = Loan.query.filter_by(customer_name=customer.name).all()
        total_installments = sum(loan.installment_count for loan in loans)
        total_collected = LoanCollection.query.filter_by(customer_id=customer.id).count()
        due_installments = max(0, total_installments - total_collected)
        
        due_data.append({
            'customer': customer,
            'due_amount': customer.remaining_loan,
            'total_installments': total_installments,
            'paid_installments': total_collected,
            'due_installments': due_installments
        })
    
    due_data.sort(key=lambda x: x['due_amount'], reverse=True)
    total_due = sum(d['due_amount'] for d in due_data)
    return render_template('due_report.html', due_data=due_data, total_due=total_due)

@app.route('/due_report_print')
@login_required
def due_report_print():
    if current_user.role == 'staff' and not current_user.is_office_staff:
        customers = Customer.query.filter_by(staff_id=current_user.id).filter(Customer.remaining_loan > 0).all()
    else:
        customers = Customer.query.filter(Customer.remaining_loan > 0).all()
    
    due_data = []
    for customer in customers:
        loans = Loan.query.filter_by(customer_name=customer.name).all()
        total_installments = sum(loan.installment_count for loan in loans)
        total_collected = LoanCollection.query.filter_by(customer_id=customer.id).count()
        due_installments = max(0, total_installments - total_collected)
        
        due_data.append({
            'customer': customer,
            'due_amount': customer.remaining_loan,
            'total_installments': total_installments,
            'paid_installments': total_collected,
            'due_installments': due_installments
        })
    
    due_data.sort(key=lambda x: x['due_amount'], reverse=True)
    total_due = sum(d['due_amount'] for d in due_data)
    return render_template('due_report_print.html', due_data=due_data, total_due=total_due)

@app.route('/notes', methods=['GET', 'POST'])
@login_required
def manage_notes():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        priority = request.form.get('priority', 'normal')
        
        if not title or not content:
            flash('শিরোনাম এবং বিষয়বস্তু আবশ্যক!', 'danger')
            return redirect(url_for('manage_notes'))
        
        note = Note(title=title, content=content, priority=priority, created_by=current_user.id)
        db.session.add(note)
        db.session.commit()
        flash('নোট সফলভাবে যোগ হয়েছে!', 'success')
        return redirect(url_for('manage_notes'))
    
    notes = Note.query.order_by(Note.created_date.desc()).all()
    return render_template('manage_notes.html', notes=notes)

@app.route('/note/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_note(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    note = Note.query.get_or_404(id)
    
    if request.method == 'POST':
        note.title = request.form.get('title', '').strip()
        note.content = request.form.get('content', '').strip()
        note.priority = request.form.get('priority', 'normal')
        
        if not note.title or not note.content:
            flash('শিরোনাম এবং বিষয়বস্তু আবশ্যক!', 'danger')
            return redirect(url_for('edit_note', id=id))
        
        db.session.commit()
        flash('নোট আপডেট সফল!', 'success')
        return redirect(url_for('manage_notes'))
    
    return render_template('edit_note.html', note=note)

@app.route('/note/delete/<int:id>')
@login_required
def delete_note(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    note = Note.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    flash('নোট ডিলিট সফল!', 'success')
    return redirect(url_for('manage_notes'))

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'change_email':
            new_email = request.form.get('new_email', '').strip()
            password = request.form.get('password', '').strip()
            
            if not new_email or not password:
                flash('সব তথ্য পূরণ করুন!', 'danger')
                return redirect(url_for('admin_settings'))
            
            if not bcrypt.check_password_hash(current_user.password, password):
                flash('পাসওয়ার্ড ভুল!', 'danger')
                return redirect(url_for('admin_settings'))
            
            if User.query.filter(User.email == new_email, User.id != current_user.id).first():
                flash('এই ইমেইল ইতিমধ্যে ব্যবহৃত হচ্ছে!', 'danger')
                return redirect(url_for('admin_settings'))
            
            current_user.email = new_email
            db.session.commit()
            flash('ইমেইল সফলভাবে পরিবর্তন হয়েছে!', 'success')
            return redirect(url_for('admin_settings'))
        
        elif action == 'change_password':
            current_password = request.form.get('current_password', '').strip()
            new_password = request.form.get('new_password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            if not current_password or not new_password or not confirm_password:
                flash('সব তথ্য পূরণ করুন!', 'danger')
                return redirect(url_for('admin_settings'))
            
            if not bcrypt.check_password_hash(current_user.password, current_password):
                flash('বর্তমান পাসওয়ার্ড ভুল!', 'danger')
                return redirect(url_for('admin_settings'))
            
            if new_password != confirm_password:
                flash('নতুন পাসওয়ার্ড মিলছে না!', 'danger')
                return redirect(url_for('admin_settings'))
            
            if len(new_password) < 6:
                flash('পাসওয়ার্ড কমপক্ষে ৬ অক্ষরের হতে হবে!', 'danger')
                return redirect(url_for('admin_settings'))
            
            current_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            db.session.commit()
            flash('পাসওয়ার্ড সফলভাবে পরিবর্তন হয়েছে!', 'success')
            return redirect(url_for('admin_settings'))
    
    return render_template('admin_settings.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

# Initialize database
def init_db():
    with app.app_context():
        try:
            db.create_all()
            
            if not User.query.filter_by(email='admin@example.com').first():
                hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
                admin = User(name='Admin', email='admin@example.com', password=hashed_pw, role='admin')
                db.session.add(admin)
            
            if not User.query.filter_by(email='staff@example.com').first():
                hashed_pw = bcrypt.generate_password_hash('staff123').decode('utf-8')
                staff = User(name='Staff', email='staff@example.com', password=hashed_pw, role='staff')
                db.session.add(staff)
            
            db.session.commit()
            
            if not CashBalance.query.first():
                initial_balance = CashBalance(balance=0)
                db.session.add(initial_balance)
                db.session.commit()
        except Exception as e:
            print(f"DB init error: {e}")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
