# -*- coding: utf-8 -*-
import os
from flask import Flask, render_template, redirect, url_for, flash, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from jinja2 import Undefined, DebugUndefined
from models.user_model import db, User
import config
from models.staff_model import Staff

# Custom Undefined class to return 0 for formatting
class SilentUndefined(DebugUndefined):
    def __format__(self, format_spec):
        return format(0, format_spec)
    def __int__(self):
        return 0
    def __float__(self):
        return 0.0
    def __str__(self):
        return '0'
    def __bool__(self):
        return False
    def __iter__(self):
        return iter([])

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
from models.note_model import Note
from models.scheduled_expense_model import ScheduledExpense
from models.collection_schedule_model import CollectionSchedule
from models.otp_model import OTP
from models.email_settings_model import EmailSettings
from datetime import datetime, timedelta, date
import csv
import io
import pytz


app = Flask(__name__)
app.config.from_object(config)
app.jinja_env.undefined = SilentUndefined

# Add default values for ALL common variables to prevent undefined errors
app.jinja_env.globals.update(
    # Financial
    total_withdrawn=0,
    total_invested=0,
    admission_fee_total=0,
    welfare_fee_total=0,
    application_fee_total=0,
    cash_balance=0,
    total_loan=0,
    total_savings=0,
    pending_loans=0,
    
    # Loan related
    interest_rate=0,
    interest_amount=0,
    loan_amount=0,
    loan_principal=0,
    installment_count=0,
    installment_type='Monthly',
    installment_amount=0,
    total_with_interest=0,
    
    # Counts
    notes_count=0,
    staff_count=0,
    total_customers=0,
    
    # Collections
    today_loan=0,
    today_saving=0,
    total_collected=0,
    
    # Dates
    loan_date='',
    collection_date='',
    
    # Others
    name='',
    role='',
    customer=None,
    customers=[],
    loans=[],
    collections=[],
    staff=None,
    staffs=[]
)

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Custom Jinja2 filter to handle undefined variables
@app.template_filter('default_zero')
def default_zero(value):
    try:
        return value if value is not None else 0
    except:
        return 0

app.jinja_env.globals.update(default_zero=default_zero)

# Auto-initialize database on startup
with app.app_context():
    try:
        db.create_all()
        
        # Create default admin if not exists
        if not User.query.filter_by(email='admin@example.com').first():
            hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
            admin = User(name='Admin', email='admin@example.com', password=hashed_pw, role='admin')
            db.session.add(admin)
        
        # Create default staff if not exists
        if not User.query.filter_by(email='staff@example.com').first():
            hashed_pw = bcrypt.generate_password_hash('staff123').decode('utf-8')
            staff = User(name='Staff', email='staff@example.com', password=hashed_pw, role='staff')
            db.session.add(staff)
        
        db.session.commit()
        
        # Initialize cash balance
        if not CashBalance.query.first():
            initial_balance = CashBalance(balance=0)
            db.session.add(initial_balance)
            db.session.commit()
    except Exception as e:
        print(f"Database initialization: {e}")

# Bangladesh timezone
BD_TZ = pytz.timezone('Asia/Dhaka')

@app.context_processor
def inject_now():
    def get_bd_time():
        return datetime.now(BD_TZ)
    return {'now': datetime.now(), 'bd_time': get_bd_time}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ----------- Routes -----------

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not email or not password:
            flash('Email and password are required!', 'danger')
            return render_template('login.html')
        
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!', 'danger')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Disable caching for dashboard
    from flask import make_response
    try:
        total_customers = Customer.query.filter_by(is_active=True).count()
        total_loan = db.session.query(db.func.coalesce(db.func.sum(Customer.remaining_loan), 0)).scalar() or 0
        total_savings = db.session.query(db.func.coalesce(db.func.sum(Customer.savings_balance), 0)).scalar() or 0
        cash_balance_record = CashBalance.query.first()
        cash_balance = cash_balance_record.balance if cash_balance_record else 0
        
        from datetime import date
        today = date.today()
        today_start = datetime.combine(today, datetime.min.time())
        today_loan = db.session.query(db.func.coalesce(db.func.sum(LoanCollection.amount), 0)).filter(LoanCollection.collection_date >= today_start).scalar() or 0
        today_saving = db.session.query(db.func.coalesce(db.func.sum(SavingCollection.amount), 0)).filter(SavingCollection.collection_date >= today_start).scalar() or 0
        
        if current_user.role == 'admin':
            staff_count = User.query.filter(User.role != 'admin').count() or 0
            try:
                notes_count = Note.query.count() or 0
            except:
                notes_count = 0
            
            admission_fee_total = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter_by(fee_type='admission').scalar() or 0
            welfare_fee_total = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter_by(fee_type='welfare').scalar() or 0
            application_fee_total = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter_by(fee_type='application').scalar() or 0
            
            resp = make_response(render_template('admin_dashboard.html',
                                 name=current_user.name or 'Admin',
                                 total_customers=total_customers or 0,
                                 pending_loans=total_loan or 0,
                                 total_savings=total_savings or 0,
                                 cash_balance=cash_balance or 0,
                                 staff_count=staff_count or 0,
                                 notes_count=notes_count or 0,
                                 admission_fee_total=admission_fee_total or 0,
                                 welfare_fee_total=welfare_fee_total or 0,
                                 application_fee_total=application_fee_total or 0))
            resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            resp.headers['Pragma'] = 'no-cache'
            resp.headers['Expires'] = '0'
            return resp
        else:
            # Get unread messages count for staff
            try:
                admin = User.query.filter_by(role='admin').first()
                unread_messages = Message.query.filter_by(
                    sender_id=admin.id if admin else 0,
                    receiver_id=current_user.id,
                    is_read=False
                ).count() if admin else 0
            except:
                unread_messages = 0
            
            # Check if monitor staff
            is_monitor = hasattr(current_user, 'is_monitor') and current_user.is_monitor
            
            # Get staff-specific data
            if is_monitor:
                # Monitor can see all customers but read-only
                my_customers = Customer.query.filter_by(is_active=True).count()
                total_remaining = db.session.query(db.func.coalesce(db.func.sum(Customer.remaining_loan), 0)).scalar() or 0
                due_customers = Customer.query.filter(Customer.remaining_loan > 0).count()
            else:
                my_customers = Customer.query.filter_by(staff_id=current_user.id, is_active=True).count()
                total_remaining = db.session.query(db.func.coalesce(db.func.sum(Customer.remaining_loan), 0)).filter_by(staff_id=current_user.id).scalar() or 0
                due_customers = Customer.query.filter_by(staff_id=current_user.id).filter(Customer.remaining_loan > 0).count()
            
            # Today's collections count
            today_loan_count = LoanCollection.query.filter_by(staff_id=current_user.id).filter(LoanCollection.collection_date >= today_start).count()
            today_saving_count = SavingCollection.query.filter_by(staff_id=current_user.id).filter(SavingCollection.collection_date >= today_start).count()
            today_collections = today_loan_count + today_saving_count
            
            # Check if office staff
            is_office_staff = hasattr(current_user, 'is_office_staff') and current_user.is_office_staff
            
            # Get all staff for office staff
            all_staff = User.query.filter(User.role != 'admin', User.id != current_user.id).all() if is_office_staff else []
            
            # Check logo
            import os
            logo_path = os.path.join('static', 'images', 'logo.jpg')
            logo_exists = os.path.exists(logo_path)
            
            resp = make_response(render_template('staff_dashboard.html',
                                 name=current_user.name or 'Staff',
                                 role=current_user.role or 'staff',
                                 total_customers=total_customers or 0,
                                 total_loan=total_loan or 0,
                                 total_savings=total_savings or 0,
                                 cash_balance=cash_balance or 0,
                                 today_loan=today_loan or 0,
                                 today_saving=today_saving or 0,
                                 unread_messages=unread_messages or 0,
                                 my_customers=my_customers or 0,
                                 total_remaining=total_remaining or 0,
                                 due_customers=due_customers or 0,
                                 today_collections=today_collections or 0,
                                 is_office_staff=is_office_staff,
                                 all_staff=all_staff,
                                 logo_exists=logo_exists,
                                 today=today,
                                 current_user=current_user))
            resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            resp.headers['Pragma'] = 'no-cache'
            resp.headers['Expires'] = '0'
            return resp
    except Exception as e:
        import traceback
        error_msg = traceback.format_exc()
        print(f"Dashboard error: {e}")
        print(error_msg)
        return f"<h1>Dashboard Error</h1><pre>{error_msg}</pre>", 500

@app.route('/manage_customers')
@login_required
def manage_customers():
    # Monitor staff can view all customers (read-only)
    if hasattr(current_user, 'is_monitor') and current_user.is_monitor:
        customers = Customer.query.filter_by(is_active=True).all()
    elif current_user.role == 'staff' and (not hasattr(current_user, 'is_office_staff') or not current_user.is_office_staff):
        customers = Customer.query.filter_by(is_active=True, staff_id=current_user.id).all()
    else:
        customers = Customer.query.filter_by(is_active=True).all()
    return render_template('manage_customers.html', customers=customers)

@app.route('/manage_staff')
@login_required
def manage_staff():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    period = request.args.get('period', 'all')
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    
    staffs = User.query.filter(User.role != 'admin').all()
    staff_data = []
    
    for staff in staffs:
        query_loan = LoanCollection.query.filter_by(staff_id=staff.id)
        query_saving = SavingCollection.query.filter_by(staff_id=staff.id)
        
        if from_date:
            start_date = datetime.strptime(from_date, '%Y-%m-%d')
            query_loan = query_loan.filter(LoanCollection.collection_date >= start_date)
            query_saving = query_saving.filter(SavingCollection.collection_date >= start_date)
        
        if to_date:
            end_date = datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_loan = query_loan.filter(LoanCollection.collection_date <= end_date)
            query_saving = query_saving.filter(SavingCollection.collection_date <= end_date)
        
        if period == 'daily':
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            query_loan = query_loan.filter(LoanCollection.collection_date >= today)
            query_saving = query_saving.filter(SavingCollection.collection_date >= today)
        elif period == 'monthly':
            if month and year:
                import calendar
                last_day = calendar.monthrange(year, month)[1]
                start = datetime(year, month, 1)
                end = datetime(year, month, last_day, 23, 59, 59)
            else:
                today = datetime.now()
                start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                end = today.replace(hour=23, minute=59, second=59, microsecond=999999)
            query_loan = query_loan.filter(LoanCollection.collection_date >= start, LoanCollection.collection_date <= end)
            query_saving = query_saving.filter(SavingCollection.collection_date >= start, SavingCollection.collection_date <= end)
        elif period == 'yearly':
            year_start = datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            query_loan = query_loan.filter(LoanCollection.collection_date >= year_start)
            query_saving = query_saving.filter(SavingCollection.collection_date >= year_start)
        
        loan_collections = query_loan.all()
        saving_collections = query_saving.all()
        total_loan = sum(lc.amount for lc in loan_collections)
        total_saving = sum(sc.amount for sc in saving_collections)
        
        staff_data.append({
            'staff': staff,
            'total_collection': total_loan + total_saving
        })
    
    return render_template('manage_staff.html', 
                         staff_data=staff_data, 
                         staffs=staffs, 
                         period=period, 
                         from_date=from_date, 
                         to_date=to_date, 
                         now=datetime.now())

@app.route('/staff/add', methods=['GET', 'POST'])
@login_required
def add_staff():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        staff_type = request.form.get('staff_type', 'field')
        
        if not name or not email or not password:
            flash('All fields are required!', 'danger')
            return redirect(url_for('add_staff'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('add_staff'))
        
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        staff = User(
            name=name,
            email=email,
            password=hashed_pw,
            role='staff',
            plain_password=password,
            is_office_staff=(staff_type == 'office'),
            is_monitor=(staff_type == 'monitor')
        )
        db.session.add(staff)
        db.session.commit()
        
        staff_type_name = 'Monitor Staff' if staff_type == 'monitor' else ('Office Staff' if staff_type == 'office' else 'Field Staff')
        flash(f'{staff_type_name} {name} added successfully!', 'success')
        return redirect(url_for('manage_staff'))
    
    return render_template('add_staff.html')

@app.route('/staff/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_staff(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    staff = User.query.get_or_404(id)
    
    if request.method == 'POST':
        staff.name = request.form.get('name', '').strip()
        staff.email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        staff_type = request.form.get('staff_type', 'field')
        
        if password:
            staff.password = bcrypt.generate_password_hash(password).decode('utf-8')
            staff.plain_password = password
        
        staff.is_office_staff = (staff_type == 'office')
        staff.is_monitor = (staff_type == 'monitor')
        
        db.session.commit()
        flash('Staff updated successfully!', 'success')
        return redirect(url_for('manage_staff'))
    
    return render_template('edit_staff.html', staff=staff)

@app.route('/staff/delete/<int:id>', methods=['POST'])
@login_required
def delete_staff(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    staff = User.query.get_or_404(id)
    
    # Check if staff has customers
    customer_count = Customer.query.filter_by(staff_id=id).count()
    if customer_count > 0:
        flash(f'Cannot delete staff! {customer_count} customers are assigned to this staff. Please transfer customers to another staff first.', 'danger')
        return redirect(url_for('manage_staff'))
    
    db.session.delete(staff)
    db.session.commit()
    flash('Staff deleted successfully!', 'success')
    return redirect(url_for('manage_staff'))

@app.route('/staff/dashboard/<int:id>')
@login_required
def staff_dashboard_view(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    staff = User.query.get_or_404(id)
    customers = Customer.query.filter_by(staff_id=id).all()
    
    total_loan = db.session.query(db.func.coalesce(db.func.sum(LoanCollection.amount), 0)).filter_by(staff_id=id).scalar() or 0
    total_saving = db.session.query(db.func.coalesce(db.func.sum(SavingCollection.amount), 0)).filter_by(staff_id=id).scalar() or 0
    
    return render_template('staff_dashboard_view.html', staff=staff, customers=customers, 
                         total_loan=total_loan, total_saving=total_saving)

@app.route('/loan_customers')
@login_required
def loan_customers():
    # Monitor staff can view all loan customers
    if hasattr(current_user, 'is_monitor') and current_user.is_monitor:
        customers = Customer.query.filter(Customer.remaining_loan > 0).all()
    elif current_user.role == 'staff' and (not hasattr(current_user, 'is_office_staff') or not current_user.is_office_staff):
        customers = Customer.query.filter(Customer.remaining_loan > 0, Customer.staff_id == current_user.id).all()
    else:
        customers = Customer.query.filter(Customer.remaining_loan > 0).all()
    return render_template('loan_customers.html', customers=customers)

@app.route('/manage_loans')
@login_required
def manage_loans():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    loans = Loan.query.order_by(Loan.loan_date.desc()).all()
    return render_template('manage_loans.html', loans=loans)

@app.route('/loans_print')
@login_required
def loans_print():
    filter_type = request.args.get('filter_type', 'all')
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    
    query = Loan.query
    
    if filter_type == 'month' and month and year:
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        month_start = datetime(year, month, 1)
        month_end = datetime(year, month, last_day, 23, 59, 59)
        query = query.filter(Loan.loan_date >= month_start, Loan.loan_date <= month_end)
    elif filter_type == 'year' and year:
        year_start = datetime(year, 1, 1)
        year_end = datetime(year, 12, 31, 23, 59, 59)
        query = query.filter(Loan.loan_date >= year_start, Loan.loan_date <= year_end)
    
    loans = query.order_by(Loan.loan_date.desc()).all()
    total_amount = sum(l.amount for l in loans)
    total_interest = sum((l.amount * l.interest / 100) for l in loans)
    total_with_interest = total_amount + total_interest
    return render_template('loans_print.html', loans=loans, filter_type=filter_type, month=month, year=year, total_amount=total_amount, total_interest=total_interest, total_with_interest=total_with_interest)

@app.route('/loan/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_loan(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    loan = Loan.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            loan.customer_name = request.form.get('customer_name', '').strip()
            loan.amount = float(request.form.get('amount', 0))
            loan.interest = float(request.form.get('interest', 0))
            due_date_str = request.form.get('due_date', '')
            
            if due_date_str:
                loan.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            
            db.session.commit()
            flash('Loan updated successfully!', 'success')
            return redirect(url_for('manage_loans'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('edit_loan', id=id))
    
    return render_template('edit_loan.html', loan=loan)

@app.route('/loan_collections_history')
@login_required
def loan_collections_history():
    # Get filter parameters
    customer_filter = request.args.get('customer', '').strip()
    staff_id = request.args.get('staff_id', type=int)
    from_date = request.args.get('from_date', '').strip()
    to_date = request.args.get('to_date', '').strip()
    
    # Build query
    query = LoanCollection.query
    
    # Apply customer filter
    if customer_filter:
        query = query.join(Customer).filter(Customer.name.like(f'%{customer_filter}%'))
    
    # Apply staff filter
    if staff_id:
        query = query.filter(LoanCollection.staff_id == staff_id)
    
    # Apply date filters
    if from_date:
        try:
            start_date = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(LoanCollection.collection_date >= start_date)
        except ValueError:
            pass
    
    if to_date:
        try:
            end_date = datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(LoanCollection.collection_date <= end_date)
        except ValueError:
            pass
    
    # Get collections
    loan_collections = query.order_by(LoanCollection.collection_date.desc()).all()
    
    # Calculate total
    total = sum(lc.amount for lc in loan_collections)
    
    # Get all staff for filter dropdown
    staffs = User.query.filter(User.role != 'admin').all()
    
    return render_template('loan_collections_history.html', 
                         loan_collections=loan_collections,
                         collections=loan_collections,  # For backward compatibility
                         total=total,
                         staffs=staffs,
                         from_date=from_date,
                         to_date=to_date)

@app.route('/manage_savings')
@login_required
def manage_savings():
    # Get filter parameters
    customer_filter = request.args.get('customer', '').strip()
    staff_id = request.args.get('staff_id', type=int)
    from_date = request.args.get('from_date', '').strip()
    to_date = request.args.get('to_date', '').strip()
    
    # Build query
    query = SavingCollection.query
    
    # Apply customer filter
    if customer_filter:
        query = query.join(Customer).filter(Customer.name.like(f'%{customer_filter}%'))
    
    # Apply staff filter
    if staff_id:
        query = query.filter(SavingCollection.staff_id == staff_id)
    
    # Apply date filters
    if from_date:
        try:
            start_date = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(SavingCollection.collection_date >= start_date)
        except ValueError:
            pass
    
    if to_date:
        try:
            end_date = datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(SavingCollection.collection_date <= end_date)
        except ValueError:
            pass
    
    # Get collections
    savings = query.order_by(SavingCollection.collection_date.desc()).all()
    
    # Calculate total
    total = sum(sc.amount for sc in savings)
    
    # Get all staff for filter dropdown
    staffs = User.query.filter(User.role != 'admin').all()
    
    return render_template('manage_savings.html', 
                         savings=savings,
                         collections=savings,  # For backward compatibility
                         total=total,
                         staffs=staffs,
                         from_date=from_date,
                         to_date=to_date)

@app.route('/all_customers_print')
@login_required
def all_customers_print():
    customers = Customer.query.filter_by(is_active=True).order_by(Customer.member_no).all()
    return render_template('all_customers_print.html', customers=customers)

@app.route('/individual_loan_sheet/<int:customer_id>')
@login_required
def individual_loan_sheet(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    loans = Loan.query.filter_by(customer_name=customer.name).order_by(Loan.loan_date).all()
    collections = LoanCollection.query.filter_by(customer_id=customer_id).order_by(LoanCollection.collection_date).all()
    return render_template('individual_loan_sheet.html', customer=customer, loans=loans, collections=collections)

@app.route('/customer_loan_sheet/<int:id>')
@login_required
def customer_loan_sheet(id):
    try:
        customer = Customer.query.get_or_404(id)
        loans = Loan.query.filter_by(customer_name=customer.name).order_by(Loan.loan_date).all()
    except Exception as e:
        if 'loan_id does not exist' in str(e):
            flash('Database migration needed. Please contact admin to run: python migrate_add_loan_id_universal.py', 'danger')
            return redirect(url_for('customer_details', id=id))
        raise
    
    # Calculate financial data
    total_loan_disbursed = sum(loan.amount for loan in loans)
    total_interest = sum(loan.amount * loan.interest / 100 for loan in loans)
    total_loan_collected = db.session.query(db.func.coalesce(db.func.sum(LoanCollection.amount), 0)).filter_by(customer_id=id).scalar() or 0
    total_savings = db.session.query(db.func.coalesce(db.func.sum(SavingCollection.amount), 0)).filter_by(customer_id=id).scalar() or 0
    total_withdrawn = db.session.query(db.func.coalesce(db.func.sum(Withdrawal.amount), 0)).filter_by(customer_id=id).scalar() or 0
    
    actual_remaining = total_loan_disbursed + total_interest - total_loan_collected
    actual_savings_balance = total_savings - total_withdrawn
    
    # Get latest loan info
    latest_loan = loans[-1] if loans else None
    loan_date = latest_loan.loan_date.strftime('%d-%m-%Y') if latest_loan else ''
    loan_end_date = latest_loan.due_date.strftime('%d-%m-%Y') if latest_loan and latest_loan.due_date else ''
    loan_principal = latest_loan.amount if latest_loan else 0
    interest_rate = latest_loan.interest if latest_loan else 0
    interest_amount = loan_principal * interest_rate / 100 if latest_loan else 0
    installment_count = latest_loan.installment_count if latest_loan else 0
    weekly_installment = latest_loan.installment_amount if latest_loan else 0
    
    # Get fees
    admission_fee = customer.admission_fee or 0
    welfare_fee = customer.welfare_fee or 0
    application_fee = customer.application_fee or 0
    
    # Get collections for history
    loan_collections = LoanCollection.query.filter_by(customer_id=id).order_by(LoanCollection.collection_date).all()
    saving_collections = SavingCollection.query.filter_by(customer_id=id).order_by(SavingCollection.collection_date).all()
    
    # Create combined collections data for template - Fixed to properly combine same-date collections
    collections_data = []
    
    # Create a dictionary to group collections by date
    collections_by_date = {}
    
    # Add loan collections
    for lc in loan_collections:
        date_key = lc.collection_date.date()
        if date_key not in collections_by_date:
            collections_by_date[date_key] = {
                'collection': lc,  # Use loan collection as primary
                'loan_amount': 0,
                'saving_amount': 0
            }
        collections_by_date[date_key]['loan_amount'] += lc.amount
    
    # Add saving collections
    for sc in saving_collections:
        date_key = sc.collection_date.date()
        if date_key not in collections_by_date:
            collections_by_date[date_key] = {
                'collection': sc,  # Use saving collection as primary if no loan collection
                'loan_amount': 0,
                'saving_amount': 0
            }
        collections_by_date[date_key]['saving_amount'] += sc.amount
    
    # Convert to list and sort by date
    collections_data = list(collections_by_date.values())
    collections_data.sort(key=lambda x: x['collection'].collection_date)
    
    # Create loans_with_collections structure for template compatibility
    loans_with_collections = []
    if loans:
        loans_with_collections.append({
            'loan': latest_loan,
            'collections': collections_data
        })
    
    return render_template('customer_loan_sheet.html', 
                         customer=customer, 
                         loans=loans,
                         total_loan_disbursed=total_loan_disbursed,
                         total_interest=total_interest,
                         total_loan_collected=total_loan_collected,
                         total_savings=total_savings,
                         total_withdrawn=total_withdrawn,
                         actual_remaining=actual_remaining,
                         actual_savings_balance=actual_savings_balance,
                         loan_date=loan_date,
                         loan_end_date=loan_end_date,
                         loan_principal=loan_principal,
                         interest_rate=interest_rate,
                         interest_amount=interest_amount,
                         installment_count=installment_count,
                         weekly_installment=weekly_installment,
                         admission_fee=admission_fee,
                         welfare_fee=welfare_fee,
                         application_fee=application_fee,
                         staff=customer.staff,
                         loans_with_collections=loans_with_collections,
                         now=datetime.now())

@app.route('/staff_collection_report')
@login_required
def staff_collection_report():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get parameters
    staff_id = request.args.get('id', type=int)
    period = request.args.get('period', 'all')
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    
    if not staff_id:
        flash('Staff ID required!', 'danger')
        return redirect(url_for('manage_staff'))
    
    staff = User.query.get_or_404(staff_id)
    
    query_loan = LoanCollection.query.filter_by(staff_id=staff_id)
    query_saving = SavingCollection.query.filter_by(staff_id=staff_id)
    
    # Apply date filters
    if from_date:
        start_date = datetime.strptime(from_date, '%Y-%m-%d')
        query_loan = query_loan.filter(LoanCollection.collection_date >= start_date)
        query_saving = query_saving.filter(SavingCollection.collection_date >= start_date)
    
    if to_date:
        end_date = datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        query_loan = query_loan.filter(LoanCollection.collection_date <= end_date)
        query_saving = query_saving.filter(SavingCollection.collection_date <= end_date)
    
    # Apply period filters
    period_display = '???'
    if period == 'daily':
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        query_loan = query_loan.filter(LoanCollection.collection_date >= today)
        query_saving = query_saving.filter(SavingCollection.collection_date >= today)
        period_display = f'????? - {today.strftime("%d-%m-%Y")}'
    elif period == 'monthly':
        if month and year:
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            start = datetime(year, month, 1)
            end = datetime(year, month, last_day, 23, 59, 59)
        else:
            today = datetime.now()
            month = today.month
            year = today.year
            start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        query_loan = query_loan.filter(LoanCollection.collection_date >= start, LoanCollection.collection_date <= end)
        query_saving = query_saving.filter(SavingCollection.collection_date >= start, SavingCollection.collection_date <= end)
        month_names = ['?????????', '???????????', '?????', '??????', '??', '???', '?????', '?????', '??????????', '???????', '???????', '????????']
        period_display = f'????? - {month_names[month-1]} {year}'
    elif period == 'yearly':
        year_start = datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        query_loan = query_loan.filter(LoanCollection.collection_date >= year_start)
        query_saving = query_saving.filter(SavingCollection.collection_date >= year_start)
        period_display = f'??????? - {datetime.now().year}'
    
    if from_date and to_date:
        period_display = f'{from_date} ???? {to_date}'
    
    loan_collections = query_loan.all()
    saving_collections = query_saving.all()
    
    # Calculate totals
    total_loan = sum(lc.amount for lc in loan_collections)
    total_saving = sum(sc.amount for sc in saving_collections)
    
    # Group collections by date
    daily_collections = {}
    for lc in loan_collections:
        date_key = lc.collection_date.strftime('%d-%m-%Y')
        if date_key not in daily_collections:
            daily_collections[date_key] = {'loan': 0, 'saving': 0}
        daily_collections[date_key]['loan'] += lc.amount
    
    for sc in saving_collections:
        date_key = sc.collection_date.strftime('%d-%m-%Y')
        if date_key not in daily_collections:
            daily_collections[date_key] = {'loan': 0, 'saving': 0}
        daily_collections[date_key]['saving'] += sc.amount
    
    return render_template('staff_collection_report.html', 
                         staff=staff,
                         period=period,
                         period_display=period_display,
                         month=month,
                         year=year,
                         total_loan=total_loan, 
                         total_saving=total_saving,
                         daily_collections=daily_collections,
                         from_date=from_date,
                         to_date=to_date,
                         now=datetime.now())

@app.route('/all_staff_report_print')
@login_required
def all_staff_report_print():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    period = request.args.get('period', 'all')
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    
    staffs = User.query.filter(User.role != 'admin').all()
    staff_data = []
    
    for staff in staffs:
        query_loan = LoanCollection.query.filter_by(staff_id=staff.id)
        query_saving = SavingCollection.query.filter_by(staff_id=staff.id)
        
        if from_date:
            start_date = datetime.strptime(from_date, '%Y-%m-%d')
            query_loan = query_loan.filter(LoanCollection.collection_date >= start_date)
            query_saving = query_saving.filter(SavingCollection.collection_date >= start_date)
        
        if to_date:
            end_date = datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query_loan = query_loan.filter(LoanCollection.collection_date <= end_date)
            query_saving = query_saving.filter(SavingCollection.collection_date <= end_date)
        
        if period == 'daily':
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            query_loan = query_loan.filter(LoanCollection.collection_date >= today)
            query_saving = query_saving.filter(SavingCollection.collection_date >= today)
        elif period == 'monthly':
            if month and year:
                import calendar
                last_day = calendar.monthrange(year, month)[1]
                start = datetime(year, month, 1)
                end = datetime(year, month, last_day, 23, 59, 59)
            else:
                today = datetime.now()
                start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                end = today.replace(hour=23, minute=59, second=59, microsecond=999999)
            query_loan = query_loan.filter(LoanCollection.collection_date >= start, LoanCollection.collection_date <= end)
            query_saving = query_saving.filter(SavingCollection.collection_date >= start, SavingCollection.collection_date <= end)
        elif period == 'yearly':
            year_start = datetime.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            query_loan = query_loan.filter(LoanCollection.collection_date >= year_start)
            query_saving = query_saving.filter(SavingCollection.collection_date >= year_start)
        
        loan_collections = query_loan.all()
        saving_collections = query_saving.all()
        total_loan = sum(lc.amount for lc in loan_collections)
        total_saving = sum(sc.amount for sc in saving_collections)
        
        customers = Customer.query.filter_by(staff_id=staff.id).count()
        remaining_loan = db.session.query(db.func.coalesce(db.func.sum(Customer.remaining_loan), 0)).filter_by(staff_id=staff.id).scalar() or 0
        
        staff_data.append({
            'staff': staff,
            'customers': customers,
            'total_loan': total_loan,
            'total_saving': total_saving,
            'total_collection': total_loan + total_saving,
            'remaining_loan': remaining_loan
        })
    
    return render_template('all_staff_report_print.html', 
                         staff_data=staff_data, 
                         period=period, 
                         from_date=from_date, 
                         to_date=to_date,
                         month=month,
                         year=year,
                         now=datetime.now())

@app.route('/customer/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    if request.method == 'POST':
        customer.name = request.form.get('name', '').strip()
        customer.phone = request.form.get('phone', '').strip()
        customer.member_no = request.form.get('member_no', '').strip()
        customer.village = request.form.get('village', '').strip()
        customer.address = request.form.get('address', '').strip()
        db.session.commit()
        flash('Customer updated successfully!', 'success')
        return redirect(url_for('customer_details', id=id))
    return render_template('edit_customer.html', customer=customer)

@app.route('/loan/add', methods=['GET', 'POST'])
@login_required
def add_loan():
    if hasattr(current_user, 'is_monitor') and current_user.is_monitor:
        flash('Monitor staff ????????? ????? ?????, ??? ???? ????? ??!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        customer_id = int(request.form.get('customer_id', 0))
        amount = float(request.form.get('amount', 0))
        interest = float(request.form.get('interest', 0))
        installment_count = int(request.form.get('installment_count', 0))
        installment_type = request.form.get('installment_type', 'Monthly')
        loan_date_str = request.form.get('loan_date', '')
        due_date_str = request.form.get('due_date', '')
        
        customer = Customer.query.get_or_404(customer_id)
        total_with_interest = amount + (amount * interest / 100)
        installment_amount = total_with_interest / installment_count if installment_count > 0 else 0
        
        loan_date = datetime.strptime(loan_date_str, '%Y-%m-%d') if loan_date_str else datetime.now()
        
        # New: Process welfare and application fees
        welfare_fee = float(request.form.get('welfare_fee', 0))
        application_fee = float(request.form.get('application_fee', 0))
        
        if due_date_str:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
        else:
            if installment_type in ['Daily', '?????']:
                due_date = loan_date + timedelta(days=installment_count)
            elif installment_type in ['Weekly', '?????????']:
                due_date = loan_date + timedelta(weeks=installment_count)
            else:
                due_date = loan_date + timedelta(days=installment_count * 30)
        
        loan = Loan(
            customer_name=customer.name,
            amount=amount,
            interest=interest,
            loan_date=loan_date,
            due_date=due_date,
            installment_count=installment_count,
            installment_type=installment_type,
            installment_amount=installment_amount
        )
        
        customer.total_loan += total_with_interest
        customer.remaining_loan += total_with_interest
        
        # Update customer fee fields
        if welfare_fee > 0:
            customer.welfare_fee = (customer.welfare_fee or 0) + welfare_fee
            fee_col = FeeCollection(customer_id=customer.id, fee_type='welfare', amount=welfare_fee, collected_by=current_user.id, note="Collected during loan disbursement")
            db.session.add(fee_col)
            
        if application_fee > 0:
            customer.application_fee = (customer.application_fee or 0) + application_fee
            fee_col = FeeCollection(customer_id=customer.id, fee_type='application', amount=application_fee, collected_by=current_user.id, note="Collected during loan disbursement")
            db.session.add(fee_col)
        
        cash_balance_record = CashBalance.query.first()
        if cash_balance_record:
            # Fees are income (+), Loan amount is expense (-)
            cash_balance_record.balance -= amount
            cash_balance_record.balance += (welfare_fee + application_fee)
        
        db.session.add(loan)
        db.session.commit()
        
        flash(f'Loan of ?{amount} added successfully!', 'success')
        return redirect(url_for('manage_loans'))
    
    if current_user.role == 'staff' and (not hasattr(current_user, 'is_office_staff') or not current_user.is_office_staff):
        customers = Customer.query.filter_by(is_active=True, staff_id=current_user.id).all()
    else:
        customers = Customer.query.filter_by(is_active=True).all()
    
    cash_balance_record = CashBalance.query.first()
    cash_balance = cash_balance_record.balance if cash_balance_record else 0
    
    return render_template('add_loan.html', customers=customers, cash_balance=cash_balance)

@app.route('/customer/<int:id>')
@login_required
def customer_details(id):
    customer = Customer.query.get_or_404(id)
    loans = Loan.query.filter_by(customer_name=customer.name).all()
    
    # Handle loan_collections with proper error handling and transaction management
    try:
        loan_collections = LoanCollection.query.filter_by(customer_id=id).order_by(LoanCollection.collection_date.desc()).all()
    except Exception as e:
        # Rollback the failed transaction
        db.session.rollback()
        # Use raw SQL to get collections without loan_id column
        from sqlalchemy import text
        try:
            result = db.session.execute(
                text("SELECT id, customer_id, amount, collection_date, staff_id FROM loan_collections WHERE customer_id = :customer_id ORDER BY collection_date DESC"),
                {'customer_id': id}
            )
            loan_collections = []
            for row in result:
                # Create a simple object for template compatibility
                collection = type('LoanCollection', (), {
                    'id': row[0],
                    'customer_id': row[1], 
                    'amount': row[2],
                    'collection_date': row[3],
                    'staff_id': row[4],
                    'staff': User.query.get(row[4]) if row[4] else None
                })()
                loan_collections.append(collection)
        except Exception as e2:
            # If even raw SQL fails, return empty list
            loan_collections = []
    
    saving_collections = SavingCollection.query.filter_by(customer_id=id).order_by(SavingCollection.collection_date.desc()).all()
    withdrawals = Withdrawal.query.filter_by(customer_id=id).order_by(Withdrawal.date.desc()).all()
    fees = FeeCollection.query.filter_by(customer_id=id).order_by(FeeCollection.collection_date.desc()).all()
    
    collections_dict = {}
    for lc in loan_collections:
        key = lc.collection_date
        if key not in collections_dict:
            collections_dict[key] = {'loan': 0, 'saving': 0, 'date': lc.collection_date, 'staff': lc.staff.name if lc.staff else 'N/A'}
        collections_dict[key]['loan'] += lc.amount
    
    for sc in saving_collections:
        key = sc.collection_date
        if key not in collections_dict:
            collections_dict[key] = {'loan': 0, 'saving': 0, 'date': sc.collection_date, 'staff': sc.staff.name if sc.staff else 'N/A'}
        collections_dict[key]['saving'] += sc.amount
    
    all_collections = sorted(collections_dict.values(), key=lambda x: x['date'], reverse=True)
    total_collected = sum(lc.amount for lc in loan_collections)
    total_withdrawn = sum(w.amount for w in withdrawals)
    
    # Calculate total fees
    admission_fee = sum(f.amount for f in fees if f.fee_type == 'admission')
    welfare_fee = sum(f.amount for f in fees if f.fee_type == 'welfare')
    application_fee = sum(f.amount for f in fees if f.fee_type == 'application')
    
    return render_template('customer_details.html', customer=customer, loans=loans, 
                         loan_collections=loan_collections, saving_collections=saving_collections,
                         withdrawals=withdrawals, all_collections=all_collections,
                         total_collected=total_collected, total_withdrawn=total_withdrawn,
                         fees=fees, admission_fee=admission_fee, welfare_fee=welfare_fee,
                         application_fee=application_fee)

@app.route('/customer/print/<int:id>')
@login_required
def customer_details_print(id):
    customer = Customer.query.get_or_404(id)
    loans = Loan.query.filter_by(customer_name=customer.name).all()
    loan_collections = LoanCollection.query.filter_by(customer_id=id).order_by(LoanCollection.collection_date).all()
    saving_collections = SavingCollection.query.filter_by(customer_id=id).order_by(SavingCollection.collection_date).all()
    withdrawals = Withdrawal.query.filter_by(customer_id=id).order_by(Withdrawal.date).all()
    return render_template('customer_details_print.html', customer=customer, loans=loans,
                         loan_collections=loan_collections, saving_collections=saving_collections,
                         withdrawals=withdrawals)

@app.route('/customer/deactivate/<int:id>', methods=['POST'])
@login_required
def deactivate_customer(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('manage_customers'))
    
    customer = Customer.query.get_or_404(id)
    customer.is_active = False
    db.session.commit()
    flash('Customer successfully deactivated!', 'success')
    return redirect(url_for('manage_customers'))

@app.route('/customer/activate/<int:id>', methods=['POST'])
@login_required
def activate_customer(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('inactive_customers'))
    
    customer = Customer.query.get_or_404(id)
    customer.is_active = True
    db.session.commit()
    flash('Customer activated successfully!', 'success')
    return redirect(url_for('inactive_customers'))

@app.route('/customer/permanent_delete/<int:id>', methods=['POST'])
@login_required
def permanent_delete_customer(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('inactive_customers'))
    
    try:
        password = request.form.get('password', '').strip()
        if not password:
            flash('Password required!', 'danger')
            return redirect(url_for('inactive_customers'))
        
        if not bcrypt.check_password_hash(current_user.password, password):
            flash('Wrong password!', 'danger')
            return redirect(url_for('inactive_customers'))
        
        customer = Customer.query.get_or_404(id)
        
        # Check if customer is inactive
        if customer.is_active:
            flash('Can only delete deactivated customers!', 'danger')
            return redirect(url_for('inactive_customers'))
        
        # Store customer name for history
        customer_name = customer.name
        
        # Delete all related records (PostgreSQL doesn't allow NULL in customer_id)
        LoanCollection.query.filter_by(customer_id=id).delete(synchronize_session=False)
        SavingCollection.query.filter_by(customer_id=id).delete(synchronize_session=False)
        FeeCollection.query.filter_by(customer_id=id).delete(synchronize_session=False)
        Withdrawal.query.filter_by(customer_id=id).delete(synchronize_session=False)
        CollectionSchedule.query.filter_by(customer_id=id).delete(synchronize_session=False)
        
        # Mark loans as deleted but keep for history
        Loan.query.filter_by(customer_name=customer.name).update(
            {'customer_name': f'[DELETED] {customer.name}'}, 
            synchronize_session=False
        )
        
        # Delete customer
        db.session.delete(customer)
        db.session.commit()
        
        flash(f'Customer "{customer_name}" permanently deleted! All related data has been removed.', 'success')
        return redirect(url_for('inactive_customers'))
    
    except Exception as e:
        db.session.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f"Delete error: {error_details}")
        flash(f'Error deleting customer: {str(e)}', 'danger')
        return redirect(url_for('inactive_customers'))

@app.route('/customer/download_report/<int:id>')
@login_required
def download_customer_report(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('inactive_customers'))
    
    customer = Customer.query.get_or_404(id)
    
    # Get all customer data
    loan_collections = LoanCollection.query.filter_by(customer_id=id).order_by(LoanCollection.collection_date).all()
    saving_collections = SavingCollection.query.filter_by(customer_id=id).order_by(SavingCollection.collection_date).all()
    loans = Loan.query.filter_by(customer_name=customer.name).order_by(Loan.loan_date).all()
    withdrawals = Withdrawal.query.filter_by(customer_id=id).order_by(Withdrawal.date).all()
    fees = FeeCollection.query.filter_by(customer_id=id).order_by(FeeCollection.collection_date).all()
    
    return render_template('customer_report_print.html',
                         customer=customer,
                         loans=loans,
                         loan_collections=loan_collections,
                         saving_collections=saving_collections,
                         withdrawals=withdrawals,
                         fees=fees,
                         now=datetime.now())

@app.route('/inactive_customers')
@login_required
def inactive_customers():
    if current_user.role not in ['admin', 'office', 'staff']:
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    customers = Customer.query.filter_by(is_active=False).all()
    return render_template('inactive_customers.html', customers=customers)

@app.route('/customer/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    if hasattr(current_user, 'is_monitor') and current_user.is_monitor:
        flash('Monitor staff ????????? ????? ?????, ???? ???????? ??? ???? ????? ??!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            phone = request.form.get('phone', '').strip()
            member_no = request.form.get('member_no', '').strip()
            
            if not name or not phone:
                flash('Name and phone are required!', 'danger')
                return redirect(url_for('add_customer'))
            
            # Check if member_no already exists
            if member_no and Customer.query.filter_by(member_no=member_no).first():
                flash(f'Member No "{member_no}" already exists!', 'danger')
                return redirect(url_for('add_customer'))
            
            admission_fee_str = request.form.get('admission_fee', '0').strip()
            admission_fee = float(admission_fee_str) if admission_fee_str else 0.0
            
            photo_filename = None
            if 'photo' in request.files:
                photo = request.files['photo']
                if photo and photo.filename:
                    import os
                    from werkzeug.utils import secure_filename
                    filename = secure_filename(photo.filename)
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    photo_filename = f"{timestamp}_{filename}"
                    photo_path = os.path.join('static', 'uploads', photo_filename)
                    photo.save(photo_path)
            
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
                photo=photo_filename,
                staff_id=current_user.id
            )
            db.session.add(customer)
            db.session.flush()
            
            if admission_fee > 0:
                fee_col = FeeCollection(customer_id=customer.id, fee_type='admission', amount=admission_fee, collected_by=current_user.id)
                db.session.add(fee_col)
            
            db.session.commit()
            flash(f'Customer added successfully! Admission Fee: ?{admission_fee}', 'success')
            return redirect(url_for('manage_customers'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('add_customer'))
    return render_template('add_customer.html')

@app.route('/collections')
@login_required
def manage_collections():
    staff_id = (lambda x: int(x) if x and x != '' else 0)(request.args.get('staff_id', ''))
    period = request.args.get('period', 'all')
    selected_date = request.args.get('date')
    month = (lambda x: int(x) if x and x != '' else 0)(request.args.get('month', ''))
    year = (lambda x: int(x) if x and x != '' else 0)(request.args.get('year', ''))
    
    # Monitor staff can view all collections
    if hasattr(current_user, 'is_monitor') and current_user.is_monitor:
        query_loan = LoanCollection.query
        query_saving = SavingCollection.query
        
        if staff_id:
            query_loan = query_loan.filter_by(staff_id=staff_id)
            query_saving = query_saving.filter_by(staff_id=staff_id)
    elif current_user.role == 'staff' and (not hasattr(current_user, 'is_office_staff') or not current_user.is_office_staff):
        query_loan = LoanCollection.query.filter_by(staff_id=current_user.id)
        query_saving = SavingCollection.query.filter_by(staff_id=current_user.id)
    else:
        query_loan = LoanCollection.query
        query_saving = SavingCollection.query
        
        if staff_id:
            query_loan = query_loan.filter_by(staff_id=staff_id)
            query_saving = query_saving.filter_by(staff_id=staff_id)
    
    from datetime import date
    import calendar
    today = datetime.now()
    period_info = {'type': period}
    
    if selected_date:
        filter_date = datetime.strptime(selected_date, '%Y-%m-%d')
        start_date = filter_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = filter_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        query_loan = query_loan.filter(LoanCollection.collection_date >= start_date, LoanCollection.collection_date <= end_date)
        query_saving = query_saving.filter(SavingCollection.collection_date >= start_date, SavingCollection.collection_date <= end_date)
        period_info['date'] = filter_date.strftime('%d-%m-%Y')
        period_info['type'] = 'daily'
    elif period == 'daily':
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        query_loan = query_loan.filter(LoanCollection.collection_date >= start_date)
        query_saving = query_saving.filter(SavingCollection.collection_date >= start_date)
        period_info['date'] = today.strftime('%d-%m-%Y')
    elif period == 'monthly':
        if month and year:
            last_day = calendar.monthrange(year, month)[1]
            start_date = datetime(year, month, 1, 0, 0, 0)
            end_date = datetime(year, month, last_day, 23, 59, 59)
        else:
            month = today.month
            year = today.year
            start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        query_loan = query_loan.filter(LoanCollection.collection_date >= start_date, LoanCollection.collection_date <= end_date)
        query_saving = query_saving.filter(SavingCollection.collection_date >= start_date, SavingCollection.collection_date <= end_date)
        month_names = ['?????????', '???????????', '?????', '??????', '??', '???', '?????', '?????', '??????????', '???????', '???????', '????????']
        period_info['month'] = month_names[month - 1]
        period_info['year'] = year
    elif period == 'yearly':
        start_date = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        query_loan = query_loan.filter(LoanCollection.collection_date >= start_date)
        query_saving = query_saving.filter(SavingCollection.collection_date >= start_date)
        period_info['year'] = today.year
    
    loan_collections = query_loan.order_by(LoanCollection.collection_date.desc()).all()
    saving_collections = query_saving.order_by(SavingCollection.collection_date.desc()).all()
    
    collections_dict = {}
    for lc in loan_collections:
        key = (lc.customer_id, lc.collection_date.date())
        if key not in collections_dict:
            collections_dict[key] = {
                'customer': lc.customer,
                'loan_amount': 0,
                'saving_amount': 0,
                'date': lc.collection_date,
                'staff': lc.staff
            }
        collections_dict[key]['loan_amount'] += lc.amount
    
    for sc in saving_collections:
        key = (sc.customer_id, sc.collection_date.date())
        if key not in collections_dict:
            collections_dict[key] = {
                'customer': sc.customer,
                'loan_amount': 0,
                'saving_amount': 0,
                'date': sc.collection_date,
                'staff': sc.staff
            }
        collections_dict[key]['saving_amount'] += sc.amount
    
    all_collections = list(collections_dict.values())
    all_collections.sort(key=lambda x: x['date'], reverse=True)
    total_loan = sum(lc.amount for lc in loan_collections)
    total_saving = sum(sc.amount for sc in saving_collections)
    
    staffs = User.query.filter_by(role='staff').all()
    
    return render_template('manage_collections.html', all_collections=all_collections, total_loan=total_loan, total_saving=total_saving, staffs=staffs, selected_staff=staff_id, period=period, period_info=period_info, selected_date=selected_date)

@app.route('/collection/add', methods=['GET', 'POST'])
@login_required
def add_collection():
    if request.method == 'POST':
        loan_id = (lambda x: int(x) if x and x != '' else 0)(request.form.get('loan_id', ''))
        amount = (lambda x: float(x) if x and x != '' else 0.0)(request.form.get('amount', ''))
        
        if not loan_id or amount <= 0:
            flash('Please fill all required fields!', 'danger')
            return redirect(url_for('add_collection'))
        
        collection = Collection(
            
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
    if hasattr(current_user, 'is_monitor') and current_user.is_monitor:
        flash('Monitor staff ????????? ????? ?????, ??????? ???? ????? ??!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        customer_id = (lambda x: int(x) if x and x != '' else 0)(request.form.get('customer_id', ''))
        loan_amount = (lambda x: float(x) if x and x != '' else 0.0)(request.form.get('loan_amount', ''))
        saving_amount = (lambda x: float(x) if x and x != '' else 0.0)(request.form.get('saving_amount', ''))
        
        if not customer_id:
            flash('Please select a customer!', 'danger')
            return redirect(url_for('collection'))
        
        if loan_amount <= 0 and saving_amount <= 0:
            flash('Please enter loan or saving amount!', 'danger')
            return redirect(url_for('collection'))
        
        customer = Customer.query.get_or_404(customer_id)
        
        cash_balance_record = CashBalance.query.first()
        if not cash_balance_record:
            cash_balance_record = CashBalance(balance=0)
            db.session.add(cash_balance_record)
        
        # Process loan collection
        if loan_amount > 0:
            if loan_amount > customer.remaining_loan:
                flash(f'Amount exceeds remaining loan (?{customer.remaining_loan})!', 'danger')
                return redirect(url_for('collection'))
            
            loan_collection = LoanCollection(customer_id=customer_id, amount=loan_amount, staff_id=current_user.id)
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
            msg.append(f'ঋণ: ৳{loan_amount}')
        if saving_amount > 0:
            msg.append(f'সঞ্চয়: ৳{saving_amount}')
        flash(f'Collection successful! {" | ".join(msg)}', 'success')
        return redirect(url_for('collection'))
    
    if current_user.role == 'staff' and (not hasattr(current_user, 'is_office_staff') or not current_user.is_office_staff):
        customers = Customer.query.filter_by(staff_id=current_user.id).all()
    else:
        customers = Customer.query.all()
    return render_template('collection.html', customers=customers)





@app.route('/daily_collections')
@login_required
def daily_collections():
    from datetime import date, datetime as dt
    
    selected_date = request.args.get('date', '')
    if selected_date:
        try:
            today_date = dt.strptime(selected_date, '%Y-%m-%d').date()
        except:
            today_date = date.today()
    else:
        today_date = date.today()
    
    # Monitor staff can view all collections
    if hasattr(current_user, 'is_monitor') and current_user.is_monitor:
        all_loan = LoanCollection.query.all()
        all_saving = SavingCollection.query.all()
        loan_collections = [lc for lc in all_loan if lc.collection_date.date() == today_date]
        saving_collections = [sc for sc in all_saving if sc.collection_date.date() == today_date]
    elif current_user.role == 'staff' and (not hasattr(current_user, 'is_office_staff') or not current_user.is_office_staff):
        all_loan = LoanCollection.query.filter_by(staff_id=current_user.id).all()
        all_saving = SavingCollection.query.filter_by(staff_id=current_user.id).all()
        loan_collections = [lc for lc in all_loan if lc.collection_date.date() == today_date]
        saving_collections = [sc for sc in all_saving if sc.collection_date.date() == today_date]
    else:
        all_loan = LoanCollection.query.all()
        all_saving = SavingCollection.query.all()
        loan_collections = [lc for lc in all_loan if lc.collection_date.date() == today_date]
        saving_collections = [sc for sc in all_saving if sc.collection_date.date() == today_date]
    
    collections_dict = {}
    for lc in loan_collections:
        key = (lc.customer_id, lc.collection_date.date())
        if key not in collections_dict:
            collections_dict[key] = {
                'customer': lc.customer,
                'loan_amount': 0,
                'saving_amount': 0,
                'date': lc.collection_date,
                'staff': lc.staff
            }
        collections_dict[key]['loan_amount'] += lc.amount
    
    for sc in saving_collections:
        key = (sc.customer_id, sc.collection_date.date())
        if key not in collections_dict:
            collections_dict[key] = {
                'customer': sc.customer,
                'loan_amount': 0,
                'saving_amount': 0,
                'date': sc.collection_date,
                'staff': sc.staff
            }
        collections_dict[key]['saving_amount'] += sc.amount
    
    all_collections = list(collections_dict.values())
    all_collections.sort(key=lambda x: x['date'], reverse=True)
    
    total_loan = sum(lc.amount for lc in loan_collections)
    total_saving = sum(sc.amount for sc in saving_collections)
    
    import os
    logo_path = os.path.join('static', 'images', 'logo.jpg')
    logo_exists = os.path.exists(logo_path)
    
    return render_template('daily_collections.html', 
                         all_collections=all_collections, 
                         total_loan=total_loan, 
                         total_saving=total_saving, 
                         logo_exists=logo_exists, 
                         today=datetime.now(), 
                         selected_date=today_date)

@app.route('/cash_balance', methods=['GET', 'POST'])
@login_required
def manage_cash_balance():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            action = request.form.get('action', '')
            amount = (lambda x: float(x) if x and x != '' else 0.0)(request.form.get('amount', ''))
            
            if not action or amount <= 0:
                flash('Please fill all required fields!', 'danger')
                return redirect(url_for('manage_cash_balance'))
            
            cash_balance_record = CashBalance.query.first()
            if not cash_balance_record:
                cash_balance_record = CashBalance(balance=0)
                db.session.add(cash_balance_record)
            
            if action == 'add':
                investor_name = request.form.get('investor_name', '').strip()
                note = request.form.get('note', '')
                
                if not investor_name:
                    flash('Investor name required!', 'danger')
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
                flash(f'Investor ID: {investor.investor_id} | ?{amount} invested successfully! Balance: ?{investor.current_balance}', 'success')
            elif action == 'subtract':
                if cash_balance_record.balance >= amount:
                    cash_balance_record.balance -= amount
                    flash(f'?{amount} deducted successfully!', 'success')
                else:
                    flash('Insufficient cash balance!', 'danger')
            elif action == 'withdraw':
                investor_name = request.form.get('investor_name', '').strip()
                note = request.form.get('note', '')
                
                if not investor_name:
                    flash('Investor name required!', 'danger')
                    return redirect(url_for('manage_cash_balance'))
                
                if cash_balance_record.balance >= amount:
                    investor = Investor.query.filter_by(name=investor_name).first()
                    if not investor:
                        flash('Investor not found! Please add investment first!', 'danger')
                        return redirect(url_for('manage_cash_balance'))
                    
                    if investor.current_balance < amount:
                        flash(f'Investor balance (?{investor.current_balance}) is insufficient!', 'danger')
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
                    flash(f'Investor ID: {investor.investor_id} | ?{amount} withdrawn successfully! Balance: ?{investor.current_balance}', 'success')
                else:
                    flash('Insufficient cash balance!', 'danger')
            
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
    total_investment = db.session.query(db.func.coalesce(db.func.sum(Investment.amount), 0)).scalar() or 0
    total_withdrawal = db.session.query(db.func.coalesce(db.func.sum(Withdrawal.amount), 0)).scalar() or 0
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
            amount = (lambda x: float(x) if x and x != '' else 0.0)(request.form.get('amount', ''))
            description = request.form.get('description', '')
            expense_date_str = request.form.get('expense_date')
            
            if not category or amount <= 0:
                flash('Please fill all required fields!', 'danger')
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
                flash(f'{category} - ?{amount} expense added successfully!', 'success')
            else:
                flash('???????? ???? ???!', 'danger')
            
            return redirect(url_for('manage_expenses'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('manage_expenses'))
    
    filter_type = request.args.get('filter_type', 'all')
    month = (lambda x: int(x) if x and x != '' else 0)(request.args.get('month', ''))
    year = (lambda x: int(x) if x and x != '' else 0)(request.args.get('year', ''))
    
    query = Expense.query
    
    if filter_type == 'month' and month and year:
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        month_start = datetime(year, month, 1)
        month_end = datetime(year, month, last_day, 23, 59, 59)
        query = query.filter(Expense.date >= month_start, Expense.date <= month_end)
    elif filter_type == 'year' and year:
        year_start = datetime(year, 1, 1)
        year_end = datetime(year, 12, 31, 23, 59, 59)
        query = query.filter(Expense.date >= year_start, Expense.date <= year_end)
    
    expenses = query.order_by(Expense.date.desc()).all()
    total_expenses = sum(e.amount for e in expenses)
    
    salary_total = sum(e.amount for e in expenses if e.category == 'Salary')
    office_total = sum(e.amount for e in expenses if e.category == 'Office')
    transport_total = sum(e.amount for e in expenses if e.category == 'Transport')
    other_total = sum(e.amount for e in expenses if e.category == 'Other')
    
    cash_balance_record = CashBalance.query.first()
    cash_balance = cash_balance_record.balance if cash_balance_record else 0
    
    return render_template('manage_expenses.html', expenses=expenses, total_expenses=total_expenses, salary_total=salary_total, office_total=office_total, transport_total=transport_total, other_total=other_total, cash_balance=cash_balance, filter_type=filter_type, month=month, year=year)

@app.route('/expenses_print')
@login_required
def expenses_print():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    filter_type = request.args.get('filter_type', 'all')
    month = (lambda x: int(x) if x and x != '' else 0)(request.args.get('month', ''))
    year = (lambda x: int(x) if x and x != '' else 0)(request.args.get('year', ''))
    
    query = Expense.query
    
    if filter_type == 'month' and month and year:
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        month_start = datetime(year, month, 1)
        month_end = datetime(year, month, last_day, 23, 59, 59)
        query = query.filter(Expense.date >= month_start, Expense.date <= month_end)
    elif filter_type == 'year' and year:
        year_start = datetime(year, 1, 1)
        year_end = datetime(year, 12, 31, 23, 59, 59)
        query = query.filter(Expense.date >= year_start, Expense.date <= year_end)
    
    expenses = query.order_by(Expense.date.desc()).all()
    total_expenses = sum(e.amount for e in expenses)
    
    by_category = {
        'Salary': sum(e.amount for e in expenses if e.category == 'Salary'),
        'Office': sum(e.amount for e in expenses if e.category == 'Office'),
        'Transport': sum(e.amount for e in expenses if e.category == 'Transport'),
        'Other': sum(e.amount for e in expenses if e.category == 'Other')
    }
    
    return render_template('expenses_print.html', expenses=expenses, total_expenses=total_expenses, by_category=by_category, filter_type=filter_type, month=month, year=year)

@app.route('/expense_receipt/<int:id>')
@login_required
def expense_receipt(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    expense = Expense.query.get_or_404(id)
    return render_template('expense_receipt.html', expense=expense)

@app.route('/profit_loss')
@login_required
def profit_loss():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    from datetime import datetime
    import calendar
    
    period = request.args.get('period', 'monthly')
    month = (lambda x: int(x) if x and x != '' else 0)(request.args.get('month', ''))
    year = (lambda x: int(x) if x and x != '' else 0)(request.args.get('year', ''))
    
    today = datetime.now()
    if period == 'monthly':
        if month and year:
            last_day = calendar.monthrange(year, month)[1]
            start_date = datetime(year, month, 1, 0, 0, 0)
        else:
            start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:  # yearly
        start_date = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Income: Loan Collections + Savings Collections + Fee Collections
    loan_collections = LoanCollection.query.filter(LoanCollection.collection_date >= start_date).all()
    saving_collections = SavingCollection.query.filter(SavingCollection.collection_date >= start_date).all()
    
    total_loan_collected = sum(lc.amount for lc in loan_collections)
    total_savings_collected = sum(sc.amount for sc in saving_collections)
    
    # Get fee collections
    admission_fee_total = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
        FeeCollection.fee_type == 'admission',
        FeeCollection.collection_date >= start_date
    ).scalar() or 0
    
    welfare_fee_total = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
        FeeCollection.fee_type == 'welfare',
        FeeCollection.collection_date >= start_date
    ).scalar() or 0
    
    application_fee_total = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
        FeeCollection.fee_type == 'application',
        FeeCollection.collection_date >= start_date
    ).scalar() or 0
    
    total_income = total_loan_collected + total_savings_collected + admission_fee_total + welfare_fee_total + application_fee_total
    
    # Expenses
    expenses = Expense.query.filter(Expense.date >= start_date).all()
    total_expenses = sum(exp.amount for exp in expenses)
    
    # Withdrawals
    withdrawals = Withdrawal.query.filter(Withdrawal.date >= start_date).all()
    total_withdrawals = sum(wd.amount for wd in withdrawals)
    
    # Net Profit/Loss = Income - (Expenses + Withdrawals)
    net_profit = total_income - (total_expenses + total_withdrawals)
    
    # Category-wise expenses
    salary_exp = sum(exp.amount for exp in expenses if exp.category == 'Salary')
    office_exp = sum(exp.amount for exp in expenses if exp.category == 'Office')
    transport_exp = sum(exp.amount for exp in expenses if exp.category == 'Transport')
    other_exp = sum(exp.amount for exp in expenses if exp.category == 'Other')
    
    # Get month name and year for display
    month_name = None
    display_year = today.year
    if period == 'monthly':
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        if month and year:
            month_name = month_names[month]
            display_year = year
        else:
            month_name = month_names[today.month]
            display_year = today.year
    elif period == 'yearly':
        display_year = today.year
    
    from markupsafe import escape
    return render_template('profit_loss.html', 
                         period=escape(period),
                         total_income=total_income,
                         total_loan_collected=total_loan_collected,
                         total_savings_collected=total_savings_collected,
                         admission_fee_total=admission_fee_total,
                         welfare_fee_total=welfare_fee_total,
                         application_fee_total=application_fee_total,
                         total_expenses=total_expenses,
                         total_withdrawals=total_withdrawals,
                         net_profit=net_profit,
                         salary_exp=salary_exp,
                         office_exp=office_exp,
                         transport_exp=transport_exp,
                         other_exp=other_exp,
                         now=datetime.now(),
                         month_name=month_name,
                         year=display_year)

@app.route('/profit_loss_print')
@login_required
def profit_loss_print():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    from datetime import datetime
    import calendar
    
    period = request.args.get('period', 'monthly')
    month = (lambda x: int(x) if x and x != '' else 0)(request.args.get('month', ''))
    year = (lambda x: int(x) if x and x != '' else 0)(request.args.get('year', ''))
    
    today = datetime.now()
    if period == 'monthly':
        if month and year:
            last_day = calendar.monthrange(year, month)[1]
            start_date = datetime(year, month, 1, 0, 0, 0)
        else:
            start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start_date = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    loan_collections = LoanCollection.query.filter(LoanCollection.collection_date >= start_date).all()
    saving_collections = SavingCollection.query.filter(SavingCollection.collection_date >= start_date).all()
    
    total_loan_collected = sum(lc.amount for lc in loan_collections)
    total_savings_collected = sum(sc.amount for sc in saving_collections)
    
    # Get fee collections
    admission_fee_total = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
        FeeCollection.fee_type == 'admission',
        FeeCollection.collection_date >= start_date
    ).scalar() or 0
    
    welfare_fee_total = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
        FeeCollection.fee_type == 'welfare',
        FeeCollection.collection_date >= start_date
    ).scalar() or 0
    
    application_fee_total = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
        FeeCollection.fee_type == 'application',
        FeeCollection.collection_date >= start_date
    ).scalar() or 0
    
    total_income = total_loan_collected + total_savings_collected + admission_fee_total + welfare_fee_total + application_fee_total
    
    expenses = Expense.query.filter(Expense.date >= start_date).all()
    total_expenses = sum(exp.amount for exp in expenses)
    
    withdrawals = Withdrawal.query.filter(Withdrawal.date >= start_date).all()
    total_withdrawals = sum(wd.amount for wd in withdrawals)
    
    net_profit = total_income - (total_expenses + total_withdrawals)
    
    salary_exp = sum(exp.amount for exp in expenses if exp.category == 'Salary')
    office_exp = sum(exp.amount for exp in expenses if exp.category == 'Office')
    transport_exp = sum(exp.amount for exp in expenses if exp.category == 'Transport')
    other_exp = sum(exp.amount for exp in expenses if exp.category == 'Other')
    
    month_name = None
    display_year = today.year
    if period == 'monthly':
        month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        if month and year:
            month_name = month_names[month]
            display_year = year
        else:
            month_name = month_names[today.month]
            display_year = today.year
    elif period == 'yearly':
        display_year = today.year
    
    return render_template('profit_loss_print.html', 
                         period=period,
                         total_income=total_income,
                         total_loan_collected=total_loan_collected,
                         total_savings_collected=total_savings_collected,
                         admission_fee_total=admission_fee_total,
                         welfare_fee_total=welfare_fee_total,
                         application_fee_total=application_fee_total,
                         total_expenses=total_expenses,
                         total_withdrawals=total_withdrawals,
                         net_profit=net_profit,
                         salary_exp=salary_exp,
                         office_exp=office_exp,
                         transport_exp=transport_exp,
                         other_exp=other_exp,
                         now=datetime.now(),
                         month_name=month_name,
                         year=display_year)

@app.route('/messages')
@login_required
def view_messages():
    # Get conversation partner ID from query params
    partner_id = (lambda x: int(x) if x and x != '' else 0)(request.args.get('user_id', ''))
    
    if current_user.role == 'admin':
        # Admin can see all staff
        staffs = User.query.filter_by(role='staff').all()
        
        # Get unread count for each staff
        staff_data = []
        for staff in staffs:
            unread = Message.query.filter_by(sender_id=staff.id, receiver_id=current_user.id, is_read=False).count()
            last_msg = Message.query.filter(
                ((Message.sender_id == current_user.id) & (Message.receiver_id == staff.id)) |
                ((Message.sender_id == staff.id) & (Message.receiver_id == current_user.id))
            ).order_by(Message.created_date.desc()).first()
            
            staff_data.append({
                'user': staff,
                'unread': unread,
                'last_message': last_msg.content[:30] + '...' if last_msg and len(last_msg.content) > 30 else (last_msg.content if last_msg else ''),
                'last_time': last_msg.created_date if last_msg else None
            })
        
        # Sort by last message time
        staff_data.sort(key=lambda x: x['last_time'] if x['last_time'] else datetime.min, reverse=True)
        
        # Get messages with selected staff
        messages = []
        selected_user = None
        if partner_id:
            selected_user = User.query.get(partner_id)
            messages = Message.query.filter(
                ((Message.sender_id == current_user.id) & (Message.receiver_id == partner_id)) |
                ((Message.sender_id == partner_id) & (Message.receiver_id == current_user.id))
            ).order_by(Message.created_date.asc()).all()
            
            # Mark messages as read
            Message.query.filter_by(sender_id=partner_id, receiver_id=current_user.id, is_read=False).update({'is_read': True})
            db.session.commit()
        
        return render_template('admin_messages.html', staff_data=staff_data, messages=messages, selected_user=selected_user)
    else:
        # Staff can only message admin
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            flash('Admin not found!', 'danger')
            return redirect(url_for('dashboard'))
        
        messages = Message.query.filter(
            ((Message.sender_id == current_user.id) & (Message.receiver_id == admin.id)) |
            ((Message.sender_id == admin.id) & (Message.receiver_id == current_user.id))
        ).order_by(Message.created_date.asc()).all()
        
        # Mark admin messages as read
        Message.query.filter_by(sender_id=admin.id, receiver_id=current_user.id, is_read=False).update({'is_read': True})
        db.session.commit()
        
        unread = Message.query.filter_by(sender_id=admin.id, receiver_id=current_user.id, is_read=False).count()
        
        return render_template('staff_messages.html', messages=messages, admin=admin, unread=unread)

@app.route('/message/send', methods=['POST'])
@login_required
def send_message():
    receiver_id = (lambda x: int(x) if x and x != '' else 0)(request.form.get('receiver_id', ''))
    content = request.form.get('content', '').strip()
    
    if not receiver_id:
        return {'success': False, 'error': 'Invalid receiver'}, 400
    
    # Handle file upload
    file_path = None
    file_type = None
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename:
            from werkzeug.utils import secure_filename
            import os
            
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            file_path = f"messages/{timestamp}_{filename}"
            full_path = os.path.join('static', 'uploads', file_path)
            
            # Create directory if not exists
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            file.save(full_path)
            
            # Determine file type
            ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                file_type = 'image'
            elif ext in ['pdf']:
                file_type = 'pdf'
            elif ext in ['doc', 'docx']:
                file_type = 'document'
            elif ext in ['xls', 'xlsx']:
                file_type = 'excel'
            else:
                file_type = 'file'
            
            if not content:
                content = f"?? {filename}"
    
    if not content and not file_path:
        return {'success': False, 'error': 'Empty message'}, 400
    
    message = Message(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        content=content,
        file_path=file_path,
        file_type=file_type
    )
    db.session.add(message)
    db.session.commit()
    
    # Return JSON for AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return {
            'success': True,
            'message': {
                'id': message.id,
                'content': message.content,
                'sender_name': current_user.name,
                'created_date': message.created_date.strftime('%H:%M'),
                'file_path': message.file_path,
                'file_type': message.file_type
            }
        }
    
    flash('Message sent!', 'success')
    return redirect(url_for('view_messages', user_id=receiver_id))

@app.route('/message/get_new/<int:partner_id>')
@login_required
def get_new_messages(partner_id):
    """Get new messages from partner (for AJAX polling)"""
    last_id = request.args.get('last_id', type=int, default=0)
    
    messages = Message.query.filter(
        Message.sender_id == partner_id,
        Message.receiver_id == current_user.id,
        Message.id > last_id
    ).order_by(Message.created_date.asc()).all()
    
    # Mark as read
    for msg in messages:
        msg.is_read = True
    db.session.commit()
    
    return {
        'messages': [{
            'id': m.id,
            'content': m.content,
            'sender_name': m.sender.name,
            'created_date': m.created_date.strftime('%H:%M'),
            'file_path': m.file_path,
            'file_type': m.file_type
        } for m in messages]
    }



@app.route('/manage_investors')
@login_required
def manage_investors():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    investors = Investor.query.order_by(Investor.investor_id).all()
    total_withdrawn = db.session.query(db.func.coalesce(db.func.sum(Withdrawal.amount), 0)).filter(Withdrawal.investor_id.isnot(None)).scalar() or 0
    return render_template('manage_investors.html', investors=investors, total_withdrawn=total_withdrawn)

@app.route('/manage_withdrawals', methods=['GET', 'POST'])
@login_required
def manage_withdrawals():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            customer_id = (lambda x: int(x) if x and x != '' else 0)(request.form.get('customer_id', ''))
            amount = (lambda x: float(x) if x and x != '' else 0.0)(request.form.get('amount', ''))
            note = request.form.get('note', '')
            
            if not customer_id or amount <= 0:
                flash('Please fill all required fields!', 'danger')
                return redirect(url_for('manage_withdrawals'))
            
            customer = Customer.query.get_or_404(customer_id)
            
            if customer.savings_balance < amount:
                flash(f'Insufficient savings! Available: ?{customer.savings_balance}', 'danger')
                return redirect(url_for('manage_withdrawals'))
            
            cash_balance_record = CashBalance.query.first()
            if not cash_balance_record or cash_balance_record.balance < amount:
                flash('Insufficient cash balance!', 'danger')
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
            flash(f'?{amount} withdrawn successfully!', 'success')
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
    # Monitor staff can view daily reports
    if current_user.role not in ['admin', 'office', 'staff']:
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
    today_end = datetime.combine(today, datetime.max.time())
    
    loan_collections = LoanCollection.query.filter(LoanCollection.collection_date >= today_start, LoanCollection.collection_date <= today_end).all()
    saving_collections = SavingCollection.query.filter(SavingCollection.collection_date >= today_start, SavingCollection.collection_date <= today_end).all()
    loans_given = Loan.query.filter(Loan.loan_date >= today_start, Loan.loan_date <= today_end).all()
    withdrawals = Withdrawal.query.filter(Withdrawal.date >= today_start, Withdrawal.date <= today_end).all()
    expenses = Expense.query.filter(Expense.date >= today_start, Expense.date <= today_end).all()
    customers_added_today = Customer.query.filter(Customer.created_date >= today_start, Customer.created_date <= today_end).all()
    
    total_installment = sum(lc.amount for lc in loan_collections)
    total_saving = sum(sc.amount for sc in saving_collections)
    total_loan_distributed = sum(l.amount for l in loans_given)
    total_withdrawal = sum(w.amount for w in withdrawals)
    total_expense = sum(e.amount for e in expenses)
    
    # Get fees from FeeCollection table
    total_welfare_fee = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
        FeeCollection.fee_type == 'welfare',
        FeeCollection.collection_date >= today_start,
        FeeCollection.collection_date <= today_end
    ).scalar() or 0
    
    total_admission_fee = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
        FeeCollection.fee_type == 'admission',
        FeeCollection.collection_date >= today_start,
        FeeCollection.collection_date <= today_end
    ).scalar() or 0
    
    total_application_fee = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
        FeeCollection.fee_type == 'application',
        FeeCollection.collection_date >= today_start,
        FeeCollection.collection_date <= today_end
    ).scalar() or 0
    
    total_outflow = total_loan_distributed + total_withdrawal + total_expense
    
    # Only show customers who have collections on this date
    collections = []
    for customer in Customer.query.order_by(Customer.member_no).all():
        loan_amount = sum(lc.amount for lc in loan_collections if lc.customer_id == customer.id)
        saving_amount = sum(sc.amount for sc in saving_collections if sc.customer_id == customer.id)
        if loan_amount > 0 or saving_amount > 0:
            collections.append({'customer': customer, 'loan_amount': loan_amount, 'saving_amount': saving_amount})
    
    return render_template('daily_report.html', report_date=today.strftime('%d-%m-%Y'), selected_date=today.strftime('%Y-%m-%d'), total_installment=total_installment, total_saving=total_saving, total_welfare_fee=total_welfare_fee, total_admission_fee=total_admission_fee, total_application_fee=total_application_fee, total_expense=total_expense, collections=collections, total_loan_distributed=total_loan_distributed, total_withdrawal=total_withdrawal, total_outflow=total_outflow)

@app.route('/daily_income_expense_print')
@login_required
def daily_income_expense_print():
    if current_user.role not in ['admin', 'office', 'staff']:
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
    today_end = datetime.combine(today, datetime.max.time())
    
    # Calculate income
    total_installment = db.session.query(db.func.coalesce(db.func.sum(LoanCollection.amount), 0)).filter(
        LoanCollection.collection_date >= today_start,
        LoanCollection.collection_date <= today_end
    ).scalar() or 0
    
    total_saving = db.session.query(db.func.coalesce(db.func.sum(SavingCollection.amount), 0)).filter(
        SavingCollection.collection_date >= today_start,
        SavingCollection.collection_date <= today_end
    ).scalar() or 0
    
    total_welfare_fee = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
        FeeCollection.fee_type == 'welfare',
        FeeCollection.collection_date >= today_start,
        FeeCollection.collection_date <= today_end
    ).scalar() or 0
    
    total_admission_fee = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
        FeeCollection.fee_type == 'admission',
        FeeCollection.collection_date >= today_start,
        FeeCollection.collection_date <= today_end
    ).scalar() or 0
    
    total_application_fee = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
        FeeCollection.fee_type == 'application',
        FeeCollection.collection_date >= today_start,
        FeeCollection.collection_date <= today_end
    ).scalar() or 0
    
    total_income = total_installment + total_saving + total_welfare_fee + total_admission_fee + total_application_fee
    
    # Calculate expenses
    total_loan_distributed = db.session.query(db.func.coalesce(db.func.sum(Loan.amount), 0)).filter(
        Loan.loan_date >= today_start,
        Loan.loan_date <= today_end
    ).scalar() or 0
    
    total_withdrawal = db.session.query(db.func.coalesce(db.func.sum(Withdrawal.amount), 0)).filter(
        Withdrawal.date >= today_start,
        Withdrawal.date <= today_end
    ).scalar() or 0
    
    total_expense = db.session.query(db.func.coalesce(db.func.sum(Expense.amount), 0)).filter(
        Expense.date >= today_start,
        Expense.date <= today_end
    ).scalar() or 0
    
    total_outflow = total_loan_distributed + total_withdrawal + total_expense
    
    return render_template('daily_income_expense_print.html',
                         report_date=today.strftime('%d-%m-%Y'),
                         total_installment=total_installment,
                         total_saving=total_saving,
                         total_welfare_fee=total_welfare_fee,
                         total_admission_fee=total_admission_fee,
                         total_application_fee=total_application_fee,
                         total_income=total_income,
                         total_loan_distributed=total_loan_distributed,
                         total_withdrawal=total_withdrawal,
                         total_expense=total_expense,
                         total_outflow=total_outflow,
                         now=datetime.now())
@login_required
def daily_report():
    if current_user.role not in ['admin', 'office', 'staff']:
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
    today_end = datetime.combine(today, datetime.max.time())
    
    loan_collections = LoanCollection.query.filter(LoanCollection.collection_date >= today_start, LoanCollection.collection_date <= today_end).all()
    saving_collections = SavingCollection.query.filter(SavingCollection.collection_date >= today_start, SavingCollection.collection_date <= today_end).all()
    loans_given = Loan.query.filter(Loan.loan_date >= today_start, Loan.loan_date <= today_end).all()
    withdrawals = Withdrawal.query.filter(Withdrawal.date >= today_start, Withdrawal.date <= today_end).all()
    expenses = Expense.query.filter(Expense.date >= today_start, Expense.date <= today_end).all()
    customers_added_today = Customer.query.filter(Customer.created_date >= today_start, Customer.created_date <= today_end).all()
    
    total_installment = sum(lc.amount for lc in loan_collections)
    total_saving = sum(sc.amount for sc in saving_collections)
    total_loan_distributed = sum(l.amount for l in loans_given)
    total_withdrawal = sum(w.amount for w in withdrawals)
    total_expense = sum(e.amount for e in expenses)
    
    # Get fees from FeeCollection table
    total_welfare_fee = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
        FeeCollection.fee_type == 'welfare',
        FeeCollection.collection_date >= today_start,
        FeeCollection.collection_date <= today_end
    ).scalar() or 0
    
    total_admission_fee = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
        FeeCollection.fee_type == 'admission',
        FeeCollection.collection_date >= today_start,
        FeeCollection.collection_date <= today_end
    ).scalar() or 0
    
    total_application_fee = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
        FeeCollection.fee_type == 'application',
        FeeCollection.collection_date >= today_start,
        FeeCollection.collection_date <= today_end
    ).scalar() or 0
    
    total_outflow = total_loan_distributed + total_withdrawal + total_expense
    
    # Only show customers who have collections on this date
    collections = []
    for customer in Customer.query.order_by(Customer.member_no).all():
        loan_amount = sum(lc.amount for lc in loan_collections if lc.customer_id == customer.id)
        saving_amount = sum(sc.amount for sc in saving_collections if sc.customer_id == customer.id)
        if loan_amount > 0 or saving_amount > 0:
            collections.append({'customer': customer, 'loan_amount': loan_amount, 'saving_amount': saving_amount})
    
    return render_template('daily_report.html', report_date=today.strftime('%d-%m-%Y'), selected_date=today.strftime('%Y-%m-%d'), total_installment=total_installment, total_saving=total_saving, total_welfare_fee=total_welfare_fee, total_admission_fee=total_admission_fee, total_application_fee=total_application_fee, total_expense=total_expense, collections=collections, total_loan_distributed=total_loan_distributed, total_withdrawal=total_withdrawal, total_outflow=total_outflow)

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
    
    # Fetch all collections grouped by day (9 queries instead of 279!)
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
        if day: daily_data[int(day)]['installments'] = float(total or 0)
    
    for day, total in saving_collections_by_day:
        if day: daily_data[int(day)]['savings'] = float(total or 0)
    
    for day, total in welfare_fees_by_day:
        if day: daily_data[int(day)]['welfare_fee'] = float(total or 0)
    
    for day, total in admission_fees_by_day:
        if day: daily_data[int(day)]['admission_fee'] = float(total or 0)
    
    for day, total in application_fees_by_day:
        if day: daily_data[int(day)]['service_charge'] = float(total or 0)
    
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

@app.route('/monthly_income_expense_print')
@login_required
def monthly_income_expense_print():
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
    
    # Calculate income
    loan_installments = db.session.query(db.func.coalesce(db.func.sum(LoanCollection.amount), 0)).filter(
        LoanCollection.collection_date >= month_start,
        LoanCollection.collection_date <= month_end
    ).scalar() or 0
    
    savings_deposits = db.session.query(db.func.coalesce(db.func.sum(SavingCollection.amount), 0)).filter(
        SavingCollection.collection_date >= month_start,
        SavingCollection.collection_date <= month_end
    ).scalar() or 0
    
    admission_fees = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
        FeeCollection.fee_type == 'admission',
        FeeCollection.collection_date >= month_start,
        FeeCollection.collection_date <= month_end
    ).scalar() or 0
    
    application_fees = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
        FeeCollection.fee_type == 'application',
        FeeCollection.collection_date >= month_start,
        FeeCollection.collection_date <= month_end
    ).scalar() or 0
    
    welfare_fees = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
        FeeCollection.fee_type == 'welfare',
        FeeCollection.collection_date >= month_start,
        FeeCollection.collection_date <= month_end
    ).scalar() or 0
    
    capital_savings = db.session.query(db.func.coalesce(db.func.sum(Investment.amount), 0)).filter(
        Investment.date >= month_start,
        Investment.date <= month_end
    ).scalar() or 0
    
    total_income = loan_installments + savings_deposits + admission_fees + application_fees + welfare_fees + capital_savings
    
    # Calculate expenses
    loan_distributed = db.session.query(db.func.coalesce(db.func.sum(Loan.amount), 0)).filter(
        Loan.loan_date >= month_start,
        Loan.loan_date <= month_end
    ).scalar() or 0
    
    total_interest = db.session.query(db.func.coalesce(db.func.sum(Loan.amount * Loan.interest / 100), 0)).filter(
        Loan.loan_date >= month_start,
        Loan.loan_date <= month_end
    ).scalar() or 0
    
    savings_return = db.session.query(db.func.coalesce(db.func.sum(Withdrawal.amount), 0)).filter(
        Withdrawal.date >= month_start,
        Withdrawal.date <= month_end
    ).scalar() or 0
    
    monthly_expenses = db.session.query(db.func.coalesce(db.func.sum(Expense.amount), 0)).filter(
        Expense.date >= month_start,
        Expense.date <= month_end
    ).scalar() or 0
    
    total_expense = loan_distributed + savings_return + monthly_expenses
    
    # Calculate balances
    cash_balance_record = CashBalance.query.first()
    current_cash = cash_balance_record.balance if cash_balance_record else 0
    
    is_current_month = (month == today.month and year == today.year)
    
    if is_current_month:
        month_income_calc = (
            (db.session.query(db.func.coalesce(db.func.sum(LoanCollection.amount), 0)).filter(
                LoanCollection.collection_date >= month_start
            ).scalar() or 0) +
            (db.session.query(db.func.coalesce(db.func.sum(SavingCollection.amount), 0)).filter(
                SavingCollection.collection_date >= month_start
            ).scalar() or 0) +
            (db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
                FeeCollection.collection_date >= month_start
            ).scalar() or 0) +
            (db.session.query(db.func.coalesce(db.func.sum(Investment.amount), 0)).filter(
                Investment.date >= month_start
            ).scalar() or 0)
        )
        
        month_expense_calc = (
            (db.session.query(db.func.coalesce(db.func.sum(Loan.amount), 0)).filter(
                Loan.loan_date >= month_start
            ).scalar() or 0) +
            (db.session.query(db.func.coalesce(db.func.sum(Withdrawal.amount), 0)).filter(
                Withdrawal.date >= month_start
            ).scalar() or 0) +
            (db.session.query(db.func.coalesce(db.func.sum(Expense.amount), 0)).filter(
                Expense.date >= month_start
            ).scalar() or 0)
        )
        
        opening_balance = current_cash - (month_income_calc - month_expense_calc)
    else:
        future_income = (
            (db.session.query(db.func.coalesce(db.func.sum(LoanCollection.amount), 0)).filter(
                LoanCollection.collection_date > month_end
            ).scalar() or 0) +
            (db.session.query(db.func.coalesce(db.func.sum(SavingCollection.amount), 0)).filter(
                SavingCollection.collection_date > month_end
            ).scalar() or 0) +
            (db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
                FeeCollection.collection_date > month_end
            ).scalar() or 0) +
            (db.session.query(db.func.coalesce(db.func.sum(Investment.amount), 0)).filter(
                Investment.date > month_end
            ).scalar() or 0)
        )
        
        future_expense = (
            (db.session.query(db.func.coalesce(db.func.sum(Loan.amount), 0)).filter(
                Loan.loan_date > month_end
            ).scalar() or 0) +
            (db.session.query(db.func.coalesce(db.func.sum(Withdrawal.amount), 0)).filter(
                Withdrawal.date > month_end
            ).scalar() or 0) +
            (db.session.query(db.func.coalesce(db.func.sum(Expense.amount), 0)).filter(
                Expense.date > month_end
            ).scalar() or 0)
        )
        
        opening_balance = current_cash - future_income + future_expense
    
    closing_balance = opening_balance + total_income - total_expense
    current_remaining = db.session.query(db.func.coalesce(db.func.sum(Customer.remaining_loan), 0)).scalar() or 0
    
    # Calculate monthly due
    monthly_due = 0
    customers_with_loans = Customer.query.filter(Customer.remaining_loan > 0).all()
    
    for customer in customers_with_loans:
        customer_loans = Loan.query.filter(
            Loan.customer_name == customer.name,
            Loan.loan_date < month_start
        ).all()
        
        if not customer_loans:
            continue
        
        expected_amount = 0
        for loan in customer_loans:
            loan_type = loan.installment_type.lower() if loan.installment_type else ''
            
            if loan_type in ['daily', '?????']:
                if month == today.month and year == today.year:
                    days = today.day
                else:
                    days = last_day
                expected_amount += loan.installment_amount * days
            elif loan_type in ['weekly', '?????????']:
                expected_amount += loan.installment_amount * 4
            elif loan_type in ['monthly', '?????']:
                expected_amount += loan.installment_amount
        
        actual_amount = db.session.query(db.func.coalesce(db.func.sum(LoanCollection.amount), 0)).filter(
            LoanCollection.customer_id == customer.id,
            LoanCollection.collection_date >= month_start,
            LoanCollection.collection_date <= month_end
        ).scalar() or 0
        
        customer_due = expected_amount - actual_amount
        if customer_due > 0:
            monthly_due += customer_due
    
    return render_template('monthly_income_expense_print.html',
                         month=month,
                         month_name=month_name,
                         year=year,
                         loan_installments=loan_installments,
                         savings_deposits=savings_deposits,
                         admission_fees=admission_fees,
                         application_fees=application_fees,
                         welfare_fees=welfare_fees,
                         capital_savings=capital_savings,
                         total_income=total_income,
                         loan_distributed=loan_distributed,
                         total_interest=total_interest,
                         savings_return=savings_return,
                         monthly_expenses=monthly_expenses,
                         total_expense=total_expense,
                         opening_balance=opening_balance,
                         closing_balance=closing_balance,
                         current_remaining=current_remaining,
                         monthly_due=monthly_due,
                         now=datetime.now())
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
    cash_balance_record = CashBalance.query.first()
    current_cash = cash_balance_record.balance if cash_balance_record else 0
    
    # For current month, calculate opening from month start transactions
    # For past months, calculate from future transactions
    is_current_month = (month == today.month and year == today.year)
    
    if is_current_month:
        # Current month - get transactions from start of month till now
        month_income = (
            (db.session.query(db.func.coalesce(db.func.sum(LoanCollection.amount), 0)).filter(
                LoanCollection.collection_date >= month_start
            ).scalar() or 0) +
            (db.session.query(db.func.coalesce(db.func.sum(SavingCollection.amount), 0)).filter(
                SavingCollection.collection_date >= month_start
            ).scalar() or 0) +
            (db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
                FeeCollection.collection_date >= month_start
            ).scalar() or 0) +
            (db.session.query(db.func.coalesce(db.func.sum(Investment.amount), 0)).filter(
                Investment.date >= month_start
            ).scalar() or 0)
        )
        
        month_expense = (
            (db.session.query(db.func.coalesce(db.func.sum(Loan.amount), 0)).filter(
                Loan.loan_date >= month_start
            ).scalar() or 0) +
            (db.session.query(db.func.coalesce(db.func.sum(Withdrawal.amount), 0)).filter(
                Withdrawal.date >= month_start
            ).scalar() or 0) +
            (db.session.query(db.func.coalesce(db.func.sum(Expense.amount), 0)).filter(
                Expense.date >= month_start
            ).scalar() or 0)
        )
        
        # Opening = Current - Net change from start of month
        opening_balance = current_cash - (month_income - month_expense)
    else:
        # Past month - calculate from future transactions
        future_income = (
            (db.session.query(db.func.coalesce(db.func.sum(LoanCollection.amount), 0)).filter(
                LoanCollection.collection_date > month_end
            ).scalar() or 0) +
            (db.session.query(db.func.coalesce(db.func.sum(SavingCollection.amount), 0)).filter(
                SavingCollection.collection_date > month_end
            ).scalar() or 0) +
            (db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
                FeeCollection.collection_date > month_end
            ).scalar() or 0) +
            (db.session.query(db.func.coalesce(db.func.sum(Investment.amount), 0)).filter(
                Investment.date > month_end
            ).scalar() or 0)
        )
        
        future_expense = (
            (db.session.query(db.func.coalesce(db.func.sum(Loan.amount), 0)).filter(
                Loan.loan_date > month_end
            ).scalar() or 0) +
            (db.session.query(db.func.coalesce(db.func.sum(Withdrawal.amount), 0)).filter(
                Withdrawal.date > month_end
            ).scalar() or 0) +
            (db.session.query(db.func.coalesce(db.func.sum(Expense.amount), 0)).filter(
                Expense.date > month_end
            ).scalar() or 0)
        )
        
        opening_balance = current_cash - future_income + future_expense
    
    running_balance = opening_balance
    daily_data = {}
    
    # Process each day of the month
    for day in range(1, last_day + 1):
        day_start = datetime(year, month, day, 0, 0, 0)
        day_end = datetime(year, month, day, 23, 59, 59)
        
        # Get daily transactions
        installments = db.session.query(db.func.coalesce(db.func.sum(LoanCollection.amount), 0)).filter(
            LoanCollection.collection_date >= day_start,
            LoanCollection.collection_date <= day_end
        ).scalar() or 0
        
        savings = db.session.query(db.func.coalesce(db.func.sum(SavingCollection.amount), 0)).filter(
            SavingCollection.collection_date >= day_start,
            SavingCollection.collection_date <= day_end
        ).scalar() or 0
        
        welfare_fee = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
            FeeCollection.fee_type == 'welfare',
            FeeCollection.collection_date >= day_start,
            FeeCollection.collection_date <= day_end
        ).scalar() or 0
        
        admission_fee = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
            FeeCollection.fee_type == 'admission',
            FeeCollection.collection_date >= day_start,
            FeeCollection.collection_date <= day_end
        ).scalar() or 0
        
        application_fee = db.session.query(db.func.coalesce(db.func.sum(FeeCollection.amount), 0)).filter(
            FeeCollection.fee_type == 'application',
            FeeCollection.collection_date >= day_start,
            FeeCollection.collection_date <= day_end
        ).scalar() or 0
        
        capital_savings = db.session.query(db.func.coalesce(db.func.sum(Investment.amount), 0)).filter(
            Investment.date >= day_start,
            Investment.date <= day_end
        ).scalar() or 0
        
        loan_given = db.session.query(db.func.coalesce(db.func.sum(Loan.amount), 0)).filter(
            Loan.loan_date >= day_start,
            Loan.loan_date <= day_end
        ).scalar() or 0
        
        interest = db.session.query(db.func.coalesce(db.func.sum(Loan.amount * Loan.interest / 100), 0)).filter(
            Loan.loan_date >= day_start,
            Loan.loan_date <= day_end
        ).scalar() or 0
        
        savings_return = db.session.query(db.func.coalesce(db.func.sum(Withdrawal.amount), 0)).filter(
            Withdrawal.date >= day_start,
            Withdrawal.date <= day_end
        ).scalar() or 0
        
        expenses_total = db.session.query(db.func.coalesce(db.func.sum(Expense.amount), 0)).filter(
            Expense.date >= day_start,
            Expense.date <= day_end
        ).scalar() or 0
        
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
    current_remaining = db.session.query(db.func.coalesce(db.func.sum(Customer.remaining_loan), 0)).scalar() or 0
    closing_balance = running_balance
    
    # Calculate monthly due - expected vs actual collections
    monthly_due = 0
    
    # Get all customers with remaining loans
    customers_with_loans = Customer.query.filter(Customer.remaining_loan > 0).all()
    
    print(f"\n=== Monthly Due Calculation for {month}/{year} ===")
    print(f"Total customers with remaining loans: {len(customers_with_loans)}")
    
    for customer in customers_with_loans:
        # Get loans given BEFORE this month starts
        customer_loans = Loan.query.filter(
            Loan.customer_name == customer.name,
            Loan.loan_date < month_start
        ).all()
        
        if not customer_loans:
            print(f"Customer {customer.name}: No loans before {month_start.date()}")
            continue
        
        print(f"\nCustomer: {customer.name} (ID: {customer.id})")
        print(f"  Loans before month: {len(customer_loans)}")
        
        # Calculate total expected for this month
        expected_amount = 0
        
        for loan in customer_loans:
            print(f"  Loan ID {loan.id}: Type='{loan.installment_type}', Amount={loan.installment_amount}, Date={loan.loan_date.date()}")
            
            loan_expected = 0
            # Support both English and Bengali installment types
            loan_type = loan.installment_type.lower() if loan.installment_type else ''
            
            if loan_type in ['daily', '?????']:
                # Count days in month (or till today for current month)
                if month == today.month and year == today.year:
                    days = today.day
                else:
                    days = last_day
                loan_expected = loan.installment_amount * days
                print(f"    Daily: {loan.installment_amount} x {days} days = {loan_expected}")
                
            elif loan_type in ['weekly', '?????????']:
                # 4 weeks per month
                loan_expected = loan.installment_amount * 4
                print(f"    Weekly: {loan.installment_amount} x 4 weeks = {loan_expected}")
                
            elif loan_type in ['monthly', '?????']:
                loan_expected = loan.installment_amount
                print(f"    Monthly: {loan.installment_amount}")
            else:
                print(f"    Unknown type: '{loan.installment_type}'")
            
            expected_amount += loan_expected
        
        # Get actual collections for this customer in this month
        actual_amount = db.session.query(db.func.coalesce(db.func.sum(LoanCollection.amount), 0)).filter(
            LoanCollection.customer_id == customer.id,
            LoanCollection.collection_date >= month_start,
            LoanCollection.collection_date <= month_end
        ).scalar() or 0
        
        print(f"  Expected: {expected_amount}, Actual: {actual_amount}")
        
        # Calculate due for this customer
        customer_due = expected_amount - actual_amount
        
        if customer_due > 0:
            print(f"  Due: {customer_due}")
            monthly_due += customer_due
        else:
            print(f"  No due (paid {actual_amount - expected_amount} extra)")
    
    print(f"\nTotal Monthly Due: {monthly_due}")
    print("=" * 50)
    
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

@app.route('/withdrawal_report')
@login_required
def withdrawal_report():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    from_date = request.args.get('from_date', '').strip()
    to_date = request.args.get('to_date', '').strip()
    
    query = Withdrawal.query
    from_date_display = ''
    to_date_display = ''
    
    if from_date or to_date:
        try:
            if from_date and to_date:
                start = datetime.strptime(from_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
                end = datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
                from_date_display = start.strftime('%d-%m-%Y')
                to_date_display = end.strftime('%d-%m-%Y')
                query = query.filter(Withdrawal.date >= start, Withdrawal.date <= end)
            elif from_date:
                start = datetime.strptime(from_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
                from_date_display = start.strftime('%d-%m-%Y')
                query = query.filter(Withdrawal.date >= start)
            elif to_date:
                end = datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
                to_date_display = end.strftime('%d-%m-%Y')
                query = query.filter(Withdrawal.date <= end)
        except Exception as e:
            print(f"Date filter error: {e}")
            flash('Date filter error! Please check dates!', 'danger')
    
    withdrawals = query.order_by(Withdrawal.date.desc()).all()
    total = sum(w.amount for w in withdrawals)
    savings_total = sum(w.amount for w in withdrawals if hasattr(w, 'withdrawal_type') and w.withdrawal_type == 'savings')
    investment_total = total - savings_total
    
    return render_template('withdrawal_report.html', withdrawals=withdrawals, total=total, savings_total=savings_total, investment_total=investment_total, from_date=from_date, to_date=to_date, from_date_display=from_date_display, to_date_display=to_date_display, now=datetime.now())

@app.route('/api/search_customers')
@login_required
def search_customers():
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return {'customers': []}
    customers = Customer.query.filter(
        Customer.is_active == True,
        (Customer.name.like(f'%{query}%')) | 
        (Customer.member_no.like(f'%{query}%')) | 
        (Customer.phone.like(f'%{query}%'))
    ).limit(20).all()
    
    result = []
    for c in customers:
        # Calculate collection stats
        total_collected = db.session.query(db.func.coalesce(db.func.sum(LoanCollection.amount), 0)).filter_by(customer_id=c.id).scalar() or 0
        last_collection = LoanCollection.query.filter_by(customer_id=c.id).order_by(LoanCollection.collection_date.desc()).first()
        
        result.append({
            'id': c.id,
            'name': c.name,
            'member_no': c.member_no or 'N/A',
            'phone': c.phone or 'N/A',
            'village': c.village or 'N/A',
            'post': c.post or 'N/A',
            'thana': c.thana or 'N/A',
            'district': c.district or 'N/A',
            'address': c.address or 'N/A',
            'father_husband': c.father_husband or 'N/A',
            'granter': c.granter or 'N/A',
            'nid_no': c.nid_no or 'N/A',
            'profession': c.profession or 'N/A',
            'admission_fee': float(c.admission_fee),
            'welfare_fee': float(c.welfare_fee),
            'application_fee': float(c.application_fee),
            'total_loan': float(c.total_loan),
            'remaining_loan': float(c.remaining_loan),
            'savings_balance': float(c.savings_balance),
            'staff_name': c.staff.name if c.staff else 'N/A',
            'created_date': c.created_date.strftime('%d-%m-%Y') if c.created_date else 'N/A',
            'total_collected': float(total_collected),
            'last_collection_date': last_collection.collection_date.strftime('%d-%m-%Y') if last_collection else 'No collection',
            'loan_status': '????????' if c.remaining_loan == 0 and c.total_loan > 0 else '?????' if c.remaining_loan > 0 else '????',
            'payment_percentage': round((total_collected / c.total_loan * 100) if c.total_loan > 0 else 0, 1)
        })
    
    return {'customers': result}

@app.route('/api/get_customer_by_nid')
@login_required
def get_customer_by_nid():
    nid = request.args.get('nid', '').strip()
    if not nid:
        return {'found': False}
    customer = Customer.query.filter_by(nid_no=nid).first()
    if customer:
        return {
            'found': True,
            'name': customer.name,
            'phone': customer.phone or '',
            'father_husband': customer.father_husband or '',
            'village': customer.village or '',
            'post': customer.post or '',
            'thana': customer.thana or '',
            'district': customer.district or '',
            'granter': customer.granter or '',
            'profession': customer.profession or '',
            'address': customer.address or ''
        }
    return {'found': False}

@app.route('/customer_search')
@login_required
def customer_search():
    return render_template('customer_search.html')

@app.route('/customer_search_advanced')
@login_required
def customer_search_advanced():
    return render_template('customer_search_advanced.html')

@app.route('/collect_fee/<int:customer_id>', methods=['POST'])
@login_required
def collect_fee(customer_id):
    if hasattr(current_user, 'is_monitor') and current_user.is_monitor:
        flash('Monitor staff ????????? ????? ?????, ?? ??????? ???? ????? ??!', 'danger')
        return redirect(url_for('customer_details', id=customer_id))
    
    customer = Customer.query.get_or_404(customer_id)
    fee_type = request.form.get('fee_type', '').strip()
    amount = float(request.form.get('amount', 0))
    note = request.form.get('note', '').strip()
    
    if not fee_type or amount <= 0:
        flash('?? ???? ??? ?????? ????????!', 'danger')
        return redirect(url_for('customer_details', id=customer_id))
    
    if fee_type not in ['admission', 'welfare', 'application']:
        flash('Invalid fee type!', 'danger')
        return redirect(url_for('customer_details', id=customer_id))
    
    # Update cash balance
    cash_balance_record = CashBalance.query.first()
    if not cash_balance_record:
        cash_balance_record = CashBalance(balance=0)
        db.session.add(cash_balance_record)
    
    cash_balance_record.balance += amount
    
    # Update customer record so fees show up on their profile
    if fee_type == 'admission':
        customer.admission_fee = (customer.admission_fee or 0) + amount
    elif fee_type == 'welfare':
        customer.welfare_fee = (customer.welfare_fee or 0) + amount
    elif fee_type == 'application':
        customer.application_fee = (customer.application_fee or 0) + amount
    
    # Create fee collection record
    fee_collection = FeeCollection(
        customer_id=customer_id,
        fee_type=fee_type,
        amount=amount,
        collected_by=current_user.id,
        note=note
    )
    db.session.add(fee_collection)
    db.session.commit()
    
    fee_names = {'admission': '????? ??', 'welfare': '?????? ??', 'application': '????? ??'}
    flash(f'{fee_names[fee_type]} ?{amount} ??????? ?????? ??? ??????!', 'success')
    return redirect(url_for('customer_details', id=customer_id))

@app.route('/fee_history/<fee_type>')
@login_required
def fee_history(fee_type):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    fee_types = {'admission': 'Admission Fee', 'welfare': 'Welfare Fee', 'application': 'Application Fee'}
    if fee_type not in fee_types:
        flash('Invalid fee type!', 'danger')
        return redirect(url_for('dashboard'))
    
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    month = (lambda x: int(x) if x and x != '' else 0)(request.args.get('month', ''))
    year = (lambda x: int(x) if x and x != '' else 0)(request.args.get('year', ''))
    
    query = FeeCollection.query.filter_by(fee_type=fee_type)
    
    if month and year:
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, last_day, 23, 59, 59)
        query = query.filter(FeeCollection.collection_date >= start_date, FeeCollection.collection_date <= end_date)
    elif from_date:
        try:
            from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(FeeCollection.collection_date >= from_datetime)
        except ValueError:
            pass
    
    if to_date:
        try:
            to_datetime = datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(FeeCollection.collection_date <= to_datetime)
        except ValueError:
            pass
    
    fees = query.order_by(FeeCollection.collection_date.desc()).all()
    total = sum(f.amount for f in fees)
    return render_template('fee_history.html', fees=fees, total=total, fee_type=fee_type, fee_name=fee_types[fee_type], from_date=from_date, to_date=to_date, month=month, year=year)

@app.route('/fee_print/<fee_type>')
@login_required
def fee_print(fee_type):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    fee_types = {'admission': 'Admission Fee', 'welfare': 'Welfare Fee', 'application': 'Application Fee'}
    if fee_type not in fee_types:
        flash('Invalid fee type!', 'danger')
        return redirect(url_for('dashboard'))
    
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    month = (lambda x: int(x) if x and x != '' else 0)(request.args.get('month', ''))
    year = (lambda x: int(x) if x and x != '' else 0)(request.args.get('year', ''))
    
    query = FeeCollection.query.filter_by(fee_type=fee_type)
    
    if month and year:
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, last_day, 23, 59, 59)
        query = query.filter(FeeCollection.collection_date >= start_date, FeeCollection.collection_date <= end_date)
    elif from_date:
        try:
            from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(FeeCollection.collection_date >= from_datetime)
        except ValueError:
            pass
    
    if to_date:
        try:
            to_datetime = datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(FeeCollection.collection_date <= to_datetime)
        except ValueError:
            pass
    
    fees = query.order_by(FeeCollection.collection_date.desc()).all()
    total = sum(f.amount for f in fees)
    return render_template('fee_print.html', fees=fees, total=total, fee_type=fee_type, fee_name=fee_types[fee_type], from_date=from_date, to_date=to_date, now=datetime.now(), month=month, year=year)

@app.route('/all_fees_history')
@login_required
def all_fees_history():
    if current_user.role not in ['admin', 'office', 'staff']:
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    month = (lambda x: int(x) if x and x != '' else 0)(request.args.get('month', ''))
    year = (lambda x: int(x) if x and x != '' else 0)(request.args.get('year', ''))
    
    query = FeeCollection.query
    
    if month and year:
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, last_day, 23, 59, 59)
        query = query.filter(FeeCollection.collection_date >= start_date, FeeCollection.collection_date <= end_date)
    elif from_date:
        try:
            from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(FeeCollection.collection_date >= from_datetime)
        except ValueError:
            pass
    
    if to_date:
        try:
            to_datetime = datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(FeeCollection.collection_date <= to_datetime)
        except ValueError:
            pass
    
    fees = query.order_by(FeeCollection.collection_date.desc()).all()
    
    # Group fees by customer
    customer_fees = {}
    for fee in fees:
        key = fee.customer_id
        if key not in customer_fees:
            customer_fees[key] = {'customer': fee.customer, 'admission': 0, 'welfare': 0, 'application': 0, 'date': fee.collection_date, 'collector': fee.collector}
        customer_fees[key][fee.fee_type] += fee.amount
    
    grouped_fees = list(customer_fees.values())
    admission_total = sum(f['admission'] for f in grouped_fees)
    welfare_total = sum(f['welfare'] for f in grouped_fees)
    application_total = sum(f['application'] for f in grouped_fees)
    total = admission_total + welfare_total + application_total
    return render_template('all_fees_history.html', fees=grouped_fees, total=total, admission_total=admission_total, welfare_total=welfare_total, application_total=application_total, from_date=from_date, to_date=to_date)

@app.route('/all_fees_print')
@login_required
def all_fees_print():
    if current_user.role not in ['admin', 'office', 'staff']:
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    month = (lambda x: int(x) if x and x != '' else 0)(request.args.get('month', ''))
    year = (lambda x: int(x) if x and x != '' else 0)(request.args.get('year', ''))
    
    query = FeeCollection.query
    
    if month and year:
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        start_date = datetime(year, month, 1)
        end_date = datetime(year, month, last_day, 23, 59, 59)
        query = query.filter(FeeCollection.collection_date >= start_date, FeeCollection.collection_date <= end_date)
    elif from_date:
        try:
            from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
            query = query.filter(FeeCollection.collection_date >= from_datetime)
        except ValueError:
            pass
    
    if to_date:
        try:
            to_datetime = datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(FeeCollection.collection_date <= to_datetime)
        except ValueError:
            pass
    
    fees = query.order_by(FeeCollection.collection_date.desc()).all()
    
    # Group fees by customer
    customer_fees = {}
    for fee in fees:
        key = fee.customer_id
        if key not in customer_fees:
            customer_fees[key] = {'customer': fee.customer, 'admission': 0, 'welfare': 0, 'application': 0, 'date': fee.collection_date, 'collector': fee.collector}
        customer_fees[key][fee.fee_type] += fee.amount
    
    grouped_fees = list(customer_fees.values())
    admission_total = sum(f['admission'] for f in grouped_fees)
    welfare_total = sum(f['welfare'] for f in grouped_fees)
    application_total = sum(f['application'] for f in grouped_fees)
    total = admission_total + welfare_total + application_total
    return render_template('all_fees_print.html', fees=grouped_fees, total=total, admission_total=admission_total, welfare_total=welfare_total, application_total=application_total, from_date=from_date, to_date=to_date, month=month, year=year, now=datetime.now())

@app.route('/due_report')
@login_required
def due_report():
    from datetime import date, timedelta
    
    staff_filter = (lambda x: int(x) if x and x != '' else 0)(request.args.get('staff_id', ''))
    min_due = request.args.get('min_due', type=float, default=0)
    max_due = request.args.get('max_due', type=float)
    min_days = request.args.get('min_days', type=int, default=0)
    risk_level = request.args.get('risk_level', '')
    village_filter = request.args.get('village', '')
    
    # Monitor staff can view all customers
    if hasattr(current_user, 'is_monitor') and current_user.is_monitor:
        query = Customer.query.filter(Customer.remaining_loan > 0)
        if staff_filter:
            query = query.filter_by(staff_id=staff_filter)
        if village_filter:
            query = query.filter(Customer.village.like(f'%{village_filter}%'))
        customers = query.all()
    elif current_user.role == 'staff' and (not hasattr(current_user, 'is_office_staff') or not current_user.is_office_staff):
        customers = Customer.query.filter_by(staff_id=current_user.id).filter(Customer.remaining_loan > 0).all()
    else:
        query = Customer.query.filter(Customer.remaining_loan > 0)
        if staff_filter:
            query = query.filter_by(staff_id=staff_filter)
        if village_filter:
            query = query.filter(Customer.village.like(f'%{village_filter}%'))
        customers = query.all()
    
    today = date.today()
    due_data = []
    daily_due_list = {}
    analytics = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'total_amount': 0}
    village_stats = {}
    staff_stats = {}
    
    for customer in customers:
        loans = Loan.query.filter_by(customer_name=customer.name).all()
        if not loans:
            continue
            
        total_installments = sum(loan.installment_count for loan in loans)
        total_collected = LoanCollection.query.filter_by(customer_id=customer.id).count()
        due_installments = max(0, total_installments - total_collected)
        
        last_collection = LoanCollection.query.filter_by(customer_id=customer.id).order_by(LoanCollection.collection_date.desc()).first()
        last_collection_date = last_collection.collection_date.date() if last_collection else None
        
        installment_type = loans[0].installment_type
        next_due_date = None
        
        if last_collection_date:
            if installment_type == 'Daily':
                next_due_date = last_collection_date + timedelta(days=1)
            elif installment_type == 'Weekly':
                next_due_date = last_collection_date + timedelta(days=7)
            elif installment_type == 'Monthly':
                next_due_date = last_collection_date + timedelta(days=30)
        else:
            next_due_date = loans[0].loan_date.date()
        
        # Calculate days: positive = overdue, negative = days remaining
        if next_due_date:
            days_overdue = (today - next_due_date).days
        else:
            days_overdue = 0
        
        # Advanced risk assessment
        risk_score = 0
        if days_overdue > 30: risk_score += 40
        elif days_overdue > 15: risk_score += 30
        elif days_overdue > 7: risk_score += 20
        elif days_overdue > 0: risk_score += 10
        
        if customer.remaining_loan > 50000: risk_score += 30
        elif customer.remaining_loan > 30000: risk_score += 20
        elif customer.remaining_loan > 10000: risk_score += 10
        
        payment_rate = (total_collected / total_installments * 100) if total_installments > 0 else 0
        if payment_rate < 50: risk_score += 20
        elif payment_rate < 70: risk_score += 10
        
        if risk_score >= 60:
            risk = 'critical'
            analytics['critical'] += 1
        elif risk_score >= 40:
            risk = 'high'
            analytics['high'] += 1
        elif risk_score >= 20:
            risk = 'medium'
            analytics['medium'] += 1
        else:
            risk = 'low'
            analytics['low'] += 1
        
        if customer.remaining_loan < min_due or (max_due and customer.remaining_loan > max_due) or days_overdue < min_days or (risk_level and risk != risk_level):
            continue
        
        # Village statistics
        village = customer.village or 'Unknown'
        if village not in village_stats:
            village_stats[village] = {'count': 0, 'amount': 0}
        village_stats[village]['count'] += 1
        village_stats[village]['amount'] += customer.remaining_loan
        
        # Staff statistics
        staff_name = customer.staff.name if customer.staff else 'Unassigned'
        if staff_name not in staff_stats:
            staff_stats[staff_name] = {'count': 0, 'amount': 0}
        staff_stats[staff_name]['count'] += 1
        staff_stats[staff_name]['amount'] += customer.remaining_loan
        
        # Payment prediction
        expected_payment_date = next_due_date + timedelta(days=7) if next_due_date else today
        
        due_data.append({
            'customer': customer,
            'due_amount': customer.remaining_loan,
            'total_installments': total_installments,
            'paid_installments': total_collected,
            'due_installments': due_installments,
            'last_collection_date': last_collection_date,
            'next_due_date': next_due_date,
            'days_overdue': days_overdue,
            'installment_type': installment_type,
            'installment_amount': loans[0].installment_amount if loans else 0,
            'risk_level': risk,
            'risk_score': risk_score,
            'payment_rate': round(payment_rate, 1),
            'expected_payment_date': expected_payment_date,
            'staff_name': staff_name
        })
        
        if next_due_date:
            date_key = next_due_date.strftime('%Y-%m-%d')
            if date_key not in daily_due_list:
                daily_due_list[date_key] = []
            daily_due_list[date_key].append({
                'customer': customer,
                'installment_amount': loans[0].installment_amount if loans else 0,
                'risk': risk
            })
    
    due_data.sort(key=lambda x: (x['risk_score'], x['days_overdue']), reverse=True)
    total_due = sum(d['due_amount'] for d in due_data)
    total_due_installment_amount = sum(d['due_installments'] * d['installment_amount'] for d in due_data)
    analytics['total_amount'] = total_due
    daily_due_list = dict(sorted(daily_due_list.items()))
    
    all_staff = User.query.filter(User.role.in_(['staff', 'admin'])).all()
    villages = sorted(set([c.village for c in Customer.query.all() if c.village]))
    
    return render_template('due_report.html', due_data=due_data, total_due=total_due, 
                         total_due_installment_amount=total_due_installment_amount, 
                         daily_due_list=daily_due_list, today=today, analytics=analytics,
                         all_staff=all_staff, villages=villages, village_stats=village_stats,
                         staff_stats=staff_stats, now=datetime.now())

@app.route('/due_report/export')
@login_required
def due_report_export():
    from datetime import date, timedelta
    import csv
    from io import StringIO
    from flask import make_response
    
    if current_user.role == 'staff' and (not hasattr(current_user, 'is_office_staff') or not current_user.is_office_staff):
        customers = Customer.query.filter_by(staff_id=current_user.id).filter(Customer.remaining_loan > 0).all()
    else:
        customers = Customer.query.filter(Customer.remaining_loan > 0).all()
    
    today = date.today()
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Serial', 'Member No', 'Name', 'Phone', 'Address', 'Remaining Loan', 'Total Installments', 
                     'Paid', 'Due Installments', 'Last Collection', 'Next Due', 'Days Overdue', 'Risk Level'])
    
    for idx, customer in enumerate(customers, 1):
        loans = Loan.query.filter_by(customer_name=customer.name).all()
        if not loans:
            continue
            
        total_installments = sum(loan.installment_count for loan in loans)
        total_collected = LoanCollection.query.filter_by(customer_id=customer.id).count()
        due_installments = max(0, total_installments - total_collected)
        
        last_collection = LoanCollection.query.filter_by(customer_id=customer.id).order_by(LoanCollection.collection_date.desc()).first()
        last_collection_date = last_collection.collection_date.date() if last_collection else None
        
        installment_type = loans[0].installment_type
        next_due_date = None
        
        if last_collection_date:
            if installment_type == 'Daily':
                next_due_date = last_collection_date + timedelta(days=1)
            elif installment_type == 'Weekly':
                next_due_date = last_collection_date + timedelta(days=7)
            elif installment_type == 'Monthly':
                next_due_date = last_collection_date + timedelta(days=30)
        else:
            next_due_date = loans[0].loan_date.date()
        
        days_overdue = (today - next_due_date).days if next_due_date and next_due_date < today else 0
        
        if days_overdue > 30:
            risk = 'Critical'
        elif days_overdue > 15:
            risk = 'High'
        elif days_overdue > 7:
            risk = 'Medium'
        else:
            risk = 'Low'
        
        writer.writerow([
            idx,
            customer.member_no or 'N/A',
            customer.name,
            customer.phone,
            f"{customer.village}, {customer.thana or ''}",
            customer.remaining_loan,
            total_installments,
            total_collected,
            due_installments,
            last_collection_date.strftime('%d-%m-%Y') if last_collection_date else 'N/A',
            next_due_date.strftime('%d-%m-%Y') if next_due_date else 'N/A',
            days_overdue,
            risk
        ])
    
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = f'attachment; filename=due_report_{today.strftime("%Y%m%d")}.csv'
    response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
    return response

@app.route('/due_report_print')
@login_required
def due_report_print():
    if current_user.role == 'staff' and (not hasattr(current_user, 'is_office_staff') or not current_user.is_office_staff):
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
            'due_installments': due_installments,
            'installment_amount': loans[0].installment_amount if loans else 0
        })
    
    due_data.sort(key=lambda x: x['due_amount'], reverse=True)
    total_due = sum(d['due_amount'] for d in due_data)
    total_due_installment_amount = sum(d['due_installments'] * d.get('installment_amount', 0) for d in due_data)
    return render_template('due_report_print.html', due_data=due_data, total_due=total_due, total_due_installment_amount=total_due_installment_amount)

@app.route('/followup/add/<int:customer_id>', methods=['POST'])
@login_required
def add_followup(customer_id):
    from models.followup_model import FollowUp
    
    customer = Customer.query.get_or_404(customer_id)
    
    method = request.form.get('method')
    notes = request.form.get('notes')
    amount_promised = (lambda x: float(x) if x and x != '' else 0.0)(request.form.get('amount_promised', ''))
    next_follow_date_str = request.form.get('next_follow_date')
    
    next_follow_date = None
    if next_follow_date_str:
        next_follow_date = datetime.strptime(next_follow_date_str, '%Y-%m-%d')
    
    followup = FollowUp(
        customer_id=customer_id,
        staff_id=current_user.id,
        method=method,
        notes=notes,
        amount_promised=amount_promised,
        next_follow_date=next_follow_date,
        status='pending'
    )
    
    db.session.add(followup)
    db.session.commit()
    
    flash('Follow-up added successfully!', 'success')
    return redirect(url_for('customer_details', id=customer_id))

@app.route('/followup/complete/<int:id>', methods=['POST'])
@login_required
def complete_followup(id):
    from models.followup_model import FollowUp
    
    followup = FollowUp.query.get_or_404(id)
    amount_collected = (lambda x: float(x) if x and x != '' else 0.0)(request.form.get('amount_collected', ''))
    
    followup.status = 'completed'
    followup.amount_collected = amount_collected
    
    db.session.commit()
    flash('Follow-up completed!', 'success')
    return redirect(url_for('customer_details', id=followup.customer_id))

@app.route('/followup/list')
@login_required
def followup_list():
    from models.followup_model import FollowUp
    from datetime import date
    
    if current_user.role == 'staff' and (not hasattr(current_user, 'is_office_staff') or not current_user.is_office_staff):
        followups = FollowUp.query.filter_by(staff_id=current_user.id).order_by(FollowUp.next_follow_date).all()
    else:
        followups = FollowUp.query.order_by(FollowUp.next_follow_date).all()
    
    today = date.today()
    pending = [f for f in followups if f.status == 'pending' and f.next_follow_date and f.next_follow_date.date() <= today]
    upcoming = [f for f in followups if f.status == 'pending' and f.next_follow_date and f.next_follow_date.date() > today]
    completed = [f for f in followups if f.status == 'completed']
    
    return render_template('followup_list.html', pending=pending, upcoming=upcoming, completed=completed)

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
        reminder_date_str = request.form.get('reminder_date', '').strip()
        
        if not title or not content:
            flash('Title and content required!', 'danger')
            return redirect(url_for('manage_notes'))
        
        reminder_date = None
        if reminder_date_str:
            reminder_date = datetime.strptime(reminder_date_str, '%Y-%m-%d')
        
        note = Note(title=title, content=content, priority=priority, reminder_date=reminder_date, created_by=current_user.id)
        db.session.add(note)
        db.session.commit()
        flash('Note added successfully!', 'success')
        return redirect(url_for('manage_notes'))
    
    # Get today's reminders
    from datetime import date
    today = date.today()
    today_reminders = Note.query.filter(
        Note.reminder_date != None,
        db.func.date(Note.reminder_date) == today,
        Note.is_notified == False
    ).all()
    
    # Mark as notified
    for note in today_reminders:
        note.is_notified = True
    db.session.commit()
    
    notes = Note.query.order_by(Note.created_date.desc()).all()
    return render_template('manage_notes.html', notes=notes, today_reminders=today_reminders)

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
            flash('Title and content required!', 'danger')
            return redirect(url_for('edit_note', id=id))
        
        db.session.commit()
        flash('Note updated successfully!', 'success')
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
    flash('Note deleted successfully!', 'success')
    return redirect(url_for('manage_notes'))

@app.route('/admin/settings/request_otp', methods=['GET'])
@login_required
def request_admin_otp():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    otp = OTP.create_otp(current_user.id, purpose='admin_settings', validity_minutes=5)
    
    # Try to send OTP via email
    email_sent = False
    email_settings = EmailSettings.get_settings()
    
    if email_settings and email_settings.email and email_settings.password:
        try:
            import smtplib
            from email.mime.text import MIMEText
            
            msg = MIMEText(f'Your OTP code is: {otp.code}\n\nThis code will expire in 5 minutes.')
            msg['Subject'] = 'Admin Settings OTP'
            msg['From'] = email_settings.email
            msg['To'] = current_user.email
            
            with smtplib.SMTP(email_settings.smtp_server, email_settings.smtp_port) as server:
                server.starttls()
                server.login(email_settings.email, email_settings.password)
                server.send_message(msg)
            
            email_sent = True
            flash('OTP sent to your email!', 'success')
        except Exception as e:
            flash(f'Email failed: {str(e)}', 'warning')
    
    return render_template('admin_settings_otp.html', otp_code=otp.code, email_sent=email_sent)

@app.route('/admin/settings/verify_otp', methods=['POST'])
@login_required
def verify_admin_otp():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    otp_code = request.form.get('otp_code', '').strip()
    
    if not otp_code:
        flash('OTP code required!', 'danger')
        return redirect(url_for('request_admin_otp'))
    
    otp = OTP.query.filter_by(
        user_id=current_user.id,
        code=otp_code,
        purpose='admin_settings',
        is_used=False
    ).first()
    
    if not otp:
        flash('Invalid OTP code!', 'danger')
        return redirect(url_for('request_admin_otp'))
    
    if not otp.is_valid():
        flash('OTP expired! Please request a new one.', 'danger')
        return redirect(url_for('request_admin_otp'))
    
    otp.mark_used()
    return redirect(url_for('admin_settings', verified='true'))

@app.route('/admin/settings', methods=['GET', 'POST'])
@login_required
def admin_settings():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'GET':
        verified = request.args.get('verified', '')
        if not verified:
            return redirect(url_for('request_admin_otp'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'change_email':
            new_email = request.form.get('new_email', '').strip()
            password = request.form.get('password', '').strip()
            
            if not new_email or not password:
                flash('All fields required!', 'danger')
                return redirect(url_for('admin_settings'))
            
            if not bcrypt.check_password_hash(current_user.password, password):
                flash('Wrong password!', 'danger')
                return redirect(url_for('admin_settings'))
            
            if User.query.filter(User.email == new_email, User.id != current_user.id).first():
                flash('Email already exists!', 'danger')
                return redirect(url_for('admin_settings'))
            
            current_user.email = new_email
            db.session.commit()
            flash('Email updated successfully!', 'success')
            return redirect(url_for('admin_settings'))
        
        elif action == 'change_password':
            current_password = request.form.get('current_password', '').strip()
            new_password = request.form.get('new_password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            if not current_password or not new_password or not confirm_password:
                flash('All fields required!', 'danger')
                return redirect(url_for('admin_settings'))
            
            if not bcrypt.check_password_hash(current_user.password, current_password):
                flash('Wrong current password!', 'danger')
                return redirect(url_for('admin_settings'))
            
            if new_password != confirm_password:
                flash('New passwords do not match!', 'danger')
                return redirect(url_for('admin_settings'))
            
            if len(new_password) < 6:
                flash('Password must be at least 6 characters!', 'danger')
                return redirect(url_for('admin_settings'))
            
            current_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            current_user.plain_password = new_password
            db.session.commit()
            flash('Password updated successfully!', 'success')
            return redirect(url_for('admin_settings'))
        
        elif action == 'save_email_settings':
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            smtp_server = request.form.get('smtp_server', 'smtp.gmail.com').strip()
            smtp_port = int(request.form.get('smtp_port', 587))
            
            if not email or not password:
                flash('Email and password required!', 'danger')
                return redirect(url_for('admin_settings'))
            
            EmailSettings.query.update({'is_active': False})
            settings = EmailSettings(
                smtp_server=smtp_server,
                smtp_port=smtp_port,
                email=email,
                password=password,
                is_active=True
            )
            db.session.add(settings)
            db.session.commit()
            flash('Email settings saved successfully!', 'success')
            return redirect(url_for('admin_settings'))
    
    return render_template('admin_settings.html')

@app.route('/scheduled_expenses', methods=['GET', 'POST'])
@login_required
def manage_scheduled_expenses():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            category = request.form.get('category', '')
            amount = (lambda x: float(x) if x and x != '' else 0.0)(request.form.get('amount', ''))
            description = request.form.get('description', '')
            frequency = request.form.get('frequency', '')
            start_date_str = request.form.get('start_date')
            
            if not category or amount <= 0 or not frequency:
                flash('Please fill all required fields!', 'danger')
                return redirect(url_for('manage_scheduled_expenses'))
            
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str else datetime.now()
            
            # Calculate next_date based on frequency
            if frequency == 'daily':
                next_date = start_date + timedelta(days=1)
            elif frequency == 'weekly':
                next_date = start_date + timedelta(days=7)
            elif frequency == 'monthly':
                next_date = start_date + timedelta(days=30)
            else:  # yearly
                next_date = start_date + timedelta(days=365)
            
            scheduled_expense = ScheduledExpense(
                category=category,
                amount=amount,
                description=description,
                frequency=frequency,
                start_date=start_date,
                next_date=next_date
            )
            db.session.add(scheduled_expense)
            db.session.commit()
            flash(f'Scheduled expense added successfully! {frequency} - ?{amount}', 'success')
            return redirect(url_for('manage_scheduled_expenses'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('manage_scheduled_expenses'))
    
    scheduled_expenses = ScheduledExpense.query.filter_by(is_active=True).all()
    return render_template('manage_scheduled_expenses.html', scheduled_expenses=scheduled_expenses)

@app.route('/scheduled_expense/toggle/<int:id>')
@login_required
def toggle_scheduled_expense(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    scheduled_expense = ScheduledExpense.query.get_or_404(id)
    scheduled_expense.is_active = not scheduled_expense.is_active
    db.session.commit()
    status = '???????' if scheduled_expense.is_active else '??????????'
    flash(f'Scheduled expense {status} successfully!', 'success')
    return redirect(url_for('manage_scheduled_expenses'))

@app.route('/scheduled_expense/delete/<int:id>', methods=['POST'])
@login_required
def delete_scheduled_expense(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    scheduled_expense = ScheduledExpense.query.get_or_404(id)
    db.session.delete(scheduled_expense)
    db.session.commit()
    flash('Scheduled expense deleted successfully!', 'success')
    return redirect(url_for('manage_scheduled_expenses'))

@app.route('/investor_details/<int:id>')
@login_required
def investor_details(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    investor = Investor.query.get_or_404(id)
    investments = Investment.query.filter_by(investor_id=id).order_by(Investment.date.desc()).all()
    withdrawals = Withdrawal.query.filter_by(investor_id=id).order_by(Withdrawal.date.desc()).all()
    
    total_invested = sum(inv.amount for inv in investments)
    total_withdrawn = sum(wd.amount for wd in withdrawals)
    
    return render_template('investor_details.html', investor=investor, investments=investments, 
                         withdrawals=withdrawals, total_invested=total_invested, 
                         total_withdrawn=total_withdrawn)

@app.route('/investor_details_print/<int:id>')
@login_required
def investor_details_print(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    investor = Investor.query.get_or_404(id)
    investments = Investment.query.filter_by(investor_id=id).order_by(Investment.date.desc()).all()
    withdrawals = Withdrawal.query.filter_by(investor_id=id).order_by(Withdrawal.date.desc()).all()
    
    total_invested = sum(inv.amount for inv in investments)
    total_withdrawn = sum(wd.amount for wd in withdrawals)
    
    return render_template('investor_details_print.html', investor=investor, investments=investments, 
                         withdrawals=withdrawals, total_invested=total_invested, 
                         total_withdrawn=total_withdrawn)

@app.route('/monthly_sheet')
@login_required
def monthly_sheet():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    import calendar
    today = datetime.now()
    month = int(request.args.get('month', today.month))
    year = int(request.args.get('year', today.year))
    
    month_names = ['', 'january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
    month_name = month_names[month]
    last_day = calendar.monthrange(year, month)[1]
    
    customers = Customer.query.filter_by(is_active=True).order_by(Customer.member_no).all()
    customer_data = {}
    
    for customer in customers:
        customer_data[customer.id] = {}
        for day in range(1, last_day + 1):
            day_start = datetime(year, month, day)
            day_end = datetime(year, month, day, 23, 59, 59)
            
            loan_amount = db.session.query(db.func.coalesce(db.func.sum(LoanCollection.amount), 0)).filter(
                LoanCollection.customer_id == customer.id,
                LoanCollection.collection_date >= day_start,
                LoanCollection.collection_date <= day_end
            ).scalar() or 0
            
            saving_amount = db.session.query(db.func.coalesce(db.func.sum(SavingCollection.amount), 0)).filter(
                SavingCollection.customer_id == customer.id,
                SavingCollection.collection_date >= day_start,
                SavingCollection.collection_date <= day_end
            ).scalar() or 0
            
            customer_data[customer.id][day] = {'loan': loan_amount, 'saving': saving_amount}
    
    return render_template('monthly_sheet.html', month=month, month_name=month_name, year=year, customers=customers, customer_data=customer_data, last_day=last_day)

@app.route('/withdrawal_invoice/<int:id>')
@login_required
def withdrawal_invoice(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    withdrawal = Withdrawal.query.get_or_404(id)
    customer = Customer.query.get_or_404(withdrawal.customer_id)
    return render_template('withdrawal_invoice.html', withdrawal=withdrawal, customer=customer)

# Collection Schedule Routes
@app.route('/collection_schedule')
@login_required
def collection_schedule():
    date_filter = request.args.get('date_filter', 'today')
    status_filter = request.args.get('status_filter', 'all')
    staff_filter = (lambda x: int(x) if x and x != '' else 0)(request.args.get('staff_filter', ''))
    
    today = date.today()
    query = CollectionSchedule.query
    
    if current_user.role == 'staff' and (not hasattr(current_user, 'is_office_staff') or not current_user.is_office_staff):
        query = query.join(Customer).filter(Customer.staff_id == current_user.id)
    elif staff_filter:
        query = query.join(Customer).filter(Customer.staff_id == staff_filter)
    
    if status_filter != 'all':
        query = query.filter(CollectionSchedule.status == status_filter)
    
    if date_filter == 'today':
        query = query.filter(db.func.date(CollectionSchedule.scheduled_date) == today)
    elif date_filter == 'tomorrow':
        tomorrow = today + timedelta(days=1)
        query = query.filter(db.func.date(CollectionSchedule.scheduled_date) == tomorrow)
    elif date_filter == 'week':
        week_end = today + timedelta(days=7)
        query = query.filter(CollectionSchedule.scheduled_date >= today, CollectionSchedule.scheduled_date <= week_end)
    elif date_filter == 'month':
        month_end = today + timedelta(days=30)
        query = query.filter(CollectionSchedule.scheduled_date >= today, CollectionSchedule.scheduled_date <= month_end)
    elif date_filter == 'overdue':
        query = query.filter(CollectionSchedule.scheduled_date < datetime.now(), CollectionSchedule.status == 'pending')
    
    schedules = query.order_by(CollectionSchedule.scheduled_date).all()
    
    for schedule in schedules:
        schedule.days_diff = (schedule.scheduled_date.date() - today).days
    
    today_schedules = [s for s in schedules if s.scheduled_date.date() == today and s.status == 'pending']
    week_schedules = [s for s in schedules if today <= s.scheduled_date.date() <= today + timedelta(days=7) and s.status == 'pending']
    overdue_schedules = [s for s in schedules if s.scheduled_date.date() < today and s.status == 'pending']
    
    today_count = len(today_schedules)
    today_amount = sum(s.expected_amount for s in today_schedules)
    week_count = len(week_schedules)
    week_amount = sum(s.expected_amount for s in week_schedules)
    overdue_count = len(overdue_schedules)
    overdue_amount = sum(s.expected_amount for s in overdue_schedules)
    total_pending = len([s for s in schedules if s.status == 'pending'])
    total_pending_amount = sum(s.expected_amount for s in schedules if s.status == 'pending')
    
    all_staff = User.query.filter_by(role='staff').all()
    
    return render_template('collection_schedule.html',
                         schedules=schedules,
                         date_filter=date_filter,
                         status_filter=status_filter,
                         staff_filter=staff_filter,
                         all_staff=all_staff,
                         today_count=today_count,
                         today_amount=today_amount,
                         week_count=week_count,
                         week_amount=week_amount,
                         overdue_count=overdue_count,
                         overdue_amount=overdue_amount,
                         total_pending=total_pending,
                         total_pending_amount=total_pending_amount)

@app.route('/collection_schedule/reschedule/<int:id>', methods=['POST'])
@login_required
def reschedule_collection(id):
    schedule = CollectionSchedule.query.get_or_404(id)
    data = request.get_json()
    new_date_str = data.get('new_date')
    
    if new_date_str:
        schedule.scheduled_date = datetime.strptime(new_date_str, '%Y-%m-%d')
        schedule.status = 'rescheduled'
        db.session.commit()
        return {'success': True}
    return {'success': False}, 400

@app.route('/application_forms')
@login_required
def application_forms():
    if hasattr(current_user, 'is_monitor') and current_user.is_monitor:
        flash('Monitor staff ????????? ????? ?????, ???? ??????? ???? ????? ??!', 'danger')
        return redirect(url_for('dashboard'))
    
    if current_user.role == 'field_staff':
        customers = Customer.query.filter_by(is_active=True, staff_id=current_user.id).order_by(Customer.member_no).all()
    else:
        customers = Customer.query.filter_by(is_active=True).order_by(Customer.member_no).all()
    return render_template('application_forms.html', customers=customers)

@app.route('/loan_application_form')
@login_required
def loan_application_form():
    if hasattr(current_user, 'is_monitor') and current_user.is_monitor:
        flash('Monitor staff ????????? ????? ?????, ???? ??????? ???? ????? ??!', 'danger')
        return redirect(url_for('dashboard'))
    
    customer_id_str = request.args.get('customer_id', '')
    customer_id = int(customer_id_str) if customer_id_str else None
    customer = Customer.query.get(customer_id) if customer_id else None
    
    if current_user.role == 'field_staff':
        customers = Customer.query.filter_by(is_active=True, staff_id=current_user.id).order_by(Customer.member_no).all()
    else:
        customers = Customer.query.filter_by(is_active=True).order_by(Customer.member_no).all()
    return render_template('loan_application_form.html', customer=customer, customers=customers)

@app.route('/commitment_form')
@login_required
def commitment_form():
    if hasattr(current_user, 'is_monitor') and current_user.is_monitor:
        flash('Monitor staff ????????? ????? ?????, ???? ??????? ???? ????? ??!', 'danger')
        return redirect(url_for('dashboard'))
    
    customer_id_str = request.args.get('customer_id', '')
    customer_id = int(customer_id_str) if customer_id_str else None
    customer = Customer.query.get(customer_id) if customer_id else None
    
    if current_user.role == 'field_staff':
        customers = Customer.query.filter_by(is_active=True, staff_id=current_user.id).order_by(Customer.member_no).all()
    else:
        customers = Customer.query.filter_by(is_active=True).order_by(Customer.member_no).all()
    return render_template('commitment_form.html', customer=customer, customers=customers)

@app.route('/angikarnama_form')
@login_required
def angikarnama_form():
    if hasattr(current_user, 'is_monitor') and current_user.is_monitor:
        flash('Monitor staff ????????? ????? ?????, ???? ??????? ???? ????? ??!', 'danger')
        return redirect(url_for('dashboard'))
    
    customer_id_str = request.args.get('customer_id', '')
    customer_id = int(customer_id_str) if customer_id_str else None
    customer = Customer.query.get(customer_id) if customer_id else None
    
    if current_user.role == 'field_staff':
        customers = Customer.query.filter_by(is_active=True, staff_id=current_user.id).order_by(Customer.member_no).all()
    else:
        customers = Customer.query.filter_by(is_active=True).order_by(Customer.member_no).all()
    return render_template('angikarnama_form.html', customer=customer, customers=customers)

@app.route('/loan_sheet/<int:loan_id>')
@login_required
def loan_sheet(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    customer = Customer.query.filter_by(name=loan.customer_name).first()
    
    if not customer:
        flash('Customer not found!', 'danger')
        return redirect(url_for('manage_loans'))
    
    # Get all loans for this customer
    loans = Loan.query.filter_by(customer_name=customer.name).order_by(Loan.loan_date).all()
    
    # Calculate financial data - ONLY for this specific loan
    total_loan_disbursed = loan.amount
    total_interest = loan.amount * loan.interest / 100
    
    # Get collections only for this loan period
    loan_start_date = loan.loan_date
    next_loan = Loan.query.filter(
        Loan.customer_name == customer.name,
        Loan.loan_date > loan.loan_date
    ).order_by(Loan.loan_date.asc()).first()
    collection_end_date = next_loan.loan_date if next_loan else datetime.now()
    
    total_loan_collected = db.session.query(db.func.coalesce(db.func.sum(LoanCollection.amount), 0)).filter(
        LoanCollection.customer_id == customer.id,
        LoanCollection.collection_date >= loan_start_date,
        LoanCollection.collection_date < collection_end_date
    ).scalar() or 0
    
    total_savings = db.session.query(db.func.coalesce(db.func.sum(SavingCollection.amount), 0)).filter(
        SavingCollection.customer_id == customer.id,
        SavingCollection.collection_date >= loan_start_date,
        SavingCollection.collection_date < collection_end_date
    ).scalar() or 0
    
    total_withdrawn = db.session.query(db.func.coalesce(db.func.sum(Withdrawal.amount), 0)).filter(
        Withdrawal.customer_id == customer.id,
        Withdrawal.date >= loan_start_date,
        Withdrawal.date < collection_end_date
    ).scalar() or 0
    
    actual_remaining = total_loan_disbursed + total_interest - total_loan_collected
    actual_savings_balance = total_savings - total_withdrawn
    
    # Current loan info
    loan_date = loan.loan_date.strftime('%d-%m-%Y')
    loan_end_date = loan.due_date.strftime('%d-%m-%Y') if loan.due_date else ''
    loan_principal = loan.amount
    interest_rate = loan.interest
    interest_amount = loan_principal * interest_rate / 100
    installment_count = loan.installment_count
    weekly_installment = loan.installment_amount
    
    # Get fees
    admission_fee = customer.admission_fee or 0
    welfare_fee = customer.welfare_fee or 0
    application_fee = customer.application_fee or 0
    
    # Get collections only for this loan period
    loan_collections = LoanCollection.query.filter(
        LoanCollection.customer_id == customer.id,
        LoanCollection.collection_date >= loan_start_date,
        LoanCollection.collection_date < collection_end_date
    ).order_by(LoanCollection.collection_date).all()
    
    saving_collections = SavingCollection.query.filter(
        SavingCollection.customer_id == customer.id,
        SavingCollection.collection_date >= loan_start_date,
        SavingCollection.collection_date < collection_end_date
    ).order_by(SavingCollection.collection_date).all()
    
    # Prepare collections data
    collections_data = []
    for lc in loan_collections:
        collections_data.append({
            'collection': lc,
            'loan_amount': lc.amount,
            'saving_amount': 0
        })
    for sc in saving_collections:
        found = False
        for cd in collections_data:
            if cd['collection'].collection_date.date() == sc.collection_date.date():
                cd['saving_amount'] = sc.amount
                found = True
                break
        if not found:
            collections_data.append({
                'collection': sc,
                'loan_amount': 0,
                'saving_amount': sc.amount
            })
    
    collections_data.sort(key=lambda x: x['collection'].collection_date)
    loans_with_collections = [{'loan': loan, 'collections': collections_data}]
    
    return render_template('customer_loan_sheet.html',
                         customer=customer,
                         loans=loans,
                         total_loan_disbursed=total_loan_disbursed,
                         total_interest=total_interest,
                         total_loan_collected=total_loan_collected,
                         total_savings=total_savings,
                         total_withdrawn=total_withdrawn,
                         actual_remaining=actual_remaining,
                         actual_savings_balance=actual_savings_balance,
                         loan_date=loan_date,
                         loan_end_date=loan_end_date,
                         loan_principal=loan_principal,
                         interest_rate=interest_rate,
                         interest_amount=interest_amount,
                         installment_count=installment_count,
                         weekly_installment=weekly_installment,
                         admission_fee=admission_fee,
                         welfare_fee=welfare_fee,
                         application_fee=application_fee,
                         staff=customer.staff,
                         loans_with_collections=loans_with_collections,
                         now=datetime.now())

@app.route('/admin/edit_collections')
@login_required
def admin_edit_collections():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    selected_date = request.args.get('date', '')
    collection_type = request.args.get('type', 'all')
    customer_filter = request.args.get('customer', '')
    
    loan_query = LoanCollection.query
    saving_query = SavingCollection.query
    
    if selected_date:
        try:
            filter_date = datetime.strptime(selected_date, '%Y-%m-%d')
            start = filter_date.replace(hour=0, minute=0, second=0)
            end = filter_date.replace(hour=23, minute=59, second=59)
            loan_query = loan_query.filter(LoanCollection.collection_date >= start, LoanCollection.collection_date <= end)
            saving_query = saving_query.filter(SavingCollection.collection_date >= start, SavingCollection.collection_date <= end)
        except:
            pass
    
    if customer_filter:
        loan_query = loan_query.join(Customer).filter(Customer.name.like(f'%{customer_filter}%'))
        saving_query = saving_query.join(Customer).filter(Customer.name.like(f'%{customer_filter}%'))
    
    loan_collections = loan_query.order_by(LoanCollection.collection_date.desc()).limit(50).all() if collection_type in ['all', 'loan'] else []
    saving_collections = saving_query.order_by(SavingCollection.collection_date.desc()).limit(50).all() if collection_type in ['all', 'saving'] else []
    
    # Combine collections by customer and date
    collections_dict = {}
    for lc in loan_collections:
        key = (lc.customer_id, lc.collection_date.date())
        if key not in collections_dict:
            collections_dict[key] = {
                'customer': lc.customer,
                'loan_amount': 0,
                'saving_amount': 0,
                'date': lc.collection_date,
                'staff': lc.staff
            }
        collections_dict[key]['loan_amount'] += lc.amount
    
    for sc in saving_collections:
        key = (sc.customer_id, sc.collection_date.date())
        if key not in collections_dict:
            collections_dict[key] = {
                'customer': sc.customer,
                'loan_amount': 0,
                'saving_amount': 0,
                'date': sc.collection_date,
                'staff': sc.staff
            }
        collections_dict[key]['saving_amount'] += sc.amount
    
    all_collections = list(collections_dict.values())
    all_collections.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('edit_collections.html', 
                         loan_collections=loan_collections,
                         saving_collections=saving_collections,
                         all_collections=all_collections,
                         selected_date=selected_date,
                         collection_type=collection_type,
                         customer_filter=customer_filter)

@app.route('/admin/delete_loan_collection/<int:id>', methods=['POST'])
@login_required
def delete_loan_collection(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    collection = LoanCollection.query.get_or_404(id)
    customer = collection.customer
    cash_balance = CashBalance.query.first()
    
    # Reverse the collection
    customer.remaining_loan += collection.amount
    if cash_balance:
        cash_balance.balance -= collection.amount
    
    db.session.delete(collection)
    db.session.commit()
    
    flash(f'Loan collection deleted! ?{collection.amount} reversed.', 'success')
    return redirect(url_for('admin_edit_collections'))

@app.route('/admin/edit_saving_collection/<int:id>', methods=['POST'])
@login_required
def edit_saving_collection(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    collection = SavingCollection.query.get_or_404(id)
    old_amount = collection.amount
    new_amount = float(request.form.get('amount', 0))
    collection_date_str = request.form.get('collection_date')
    
    if new_amount <= 0:
        flash('Amount must be greater than 0!', 'danger')
        return redirect(url_for('admin_edit_collections'))
    
    customer = collection.customer
    cash_balance = CashBalance.query.first()
    
    # Reverse old amount
    customer.savings_balance -= old_amount
    if cash_balance:
        cash_balance.balance -= old_amount
    
    # Apply new amount
    customer.savings_balance += new_amount
    if cash_balance:
        cash_balance.balance += new_amount
    
    collection.amount = new_amount
    if collection_date_str:
        collection.collection_date = datetime.strptime(collection_date_str, '%Y-%m-%dT%H:%M')
    
    db.session.commit()
    flash(f'Saving collection updated! Old: ?{old_amount}, New: ?{new_amount}', 'success')
    return redirect(url_for('admin_edit_collections'))

@app.route('/admin/delete_saving_collection/<int:id>', methods=['POST'])
@login_required
def delete_saving_collection(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    collection = SavingCollection.query.get_or_404(id)
    customer = collection.customer
    cash_balance = CashBalance.query.first()
    
    # Reverse the collection
    customer.savings_balance -= collection.amount
    if cash_balance:
        cash_balance.balance -= collection.amount
    
    db.session.delete(collection)
    db.session.commit()
    
    flash(f'Saving collection deleted! ?{collection.amount} reversed.', 'success')
    return redirect(url_for('admin_edit_collections'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/import_old_data', methods=['GET', 'POST'])
@login_required
def import_old_data():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            action = request.form.get('action')
            
            if action == 'add_customer':
                name = request.form.get('name', '').strip()
                phone = request.form.get('phone', '').strip()
                member_no = request.form.get('member_no', '').strip()
                village = request.form.get('village', '').strip()
                address = request.form.get('address', '').strip()
                staff_id_str = request.form.get('staff_id', '').strip()
                staff_id = int(staff_id_str) if staff_id_str else None
                total_loan = (lambda x: float(x) if x and x != '' else 0.0)(request.form.get('total_loan', ''))
                remaining_loan = (lambda x: float(x) if x and x != '' else 0.0)(request.form.get('remaining_loan', ''))
                savings_balance = (lambda x: float(x) if x and x != '' else 0.0)(request.form.get('savings_balance', ''))
                created_date_str = request.form.get('created_date', '')
                
                if not name:
                    flash('Name is required!', 'danger')
                    return redirect(url_for('import_old_data'))
                
                created_date = datetime.strptime(created_date_str, '%Y-%m-%d') if created_date_str else datetime.now()
                
                customer = Customer(
                    name=name,
                    phone=phone,
                    member_no=member_no,
                    village=village,
                    address=address,
                    staff_id=staff_id or current_user.id,
                    total_loan=total_loan,
                    remaining_loan=remaining_loan,
                    savings_balance=savings_balance,
                    created_date=created_date
                )
                db.session.add(customer)
                db.session.commit()
                
                # Update cash balance
                cash_balance_record = CashBalance.query.first()
                if cash_balance_record:
                    cash_balance_record.balance += savings_balance
                    db.session.commit()
                
                flash(f'Success! Customer "{name}" added successfully!', 'success')
                return redirect(url_for('import_old_data'))
            
            elif action == 'add_collection':
                customer_id_str = request.form.get('customer_id', '').strip()
                customer_id = int(customer_id_str) if customer_id_str else None
                loan_amount = (lambda x: float(x) if x and x != '' else 0.0)(request.form.get('loan_amount', ''))
                saving_amount = (lambda x: float(x) if x and x != '' else 0.0)(request.form.get('saving_amount', ''))
                collection_date_str = request.form.get('collection_date', '')
                staff_id_str = request.form.get('staff_id', '').strip()
                staff_id = int(staff_id_str) if staff_id_str else current_user.id
                
                if not customer_id:
                    flash('Please select a customer!', 'danger')
                    return redirect(url_for('import_old_data'))
                
                collection_date = datetime.strptime(collection_date_str, '%Y-%m-%d') if collection_date_str else datetime.now()
                
                if loan_amount > 0:
                    loan_col = LoanCollection(
                        customer_id=customer_id,
                        amount=loan_amount,
                        staff_id=staff_id,
                        collection_date=collection_date
                    )
                    db.session.add(loan_col)
                
                if saving_amount > 0:
                    saving_col = SavingCollection(
                        customer_id=customer_id,
                        amount=saving_amount,
                        staff_id=staff_id,
                        collection_date=collection_date
                    )
                    db.session.add(saving_col)
                
                db.session.commit()
                flash(f'Success! Collection added! Loan: ?{loan_amount}, Savings: ?{saving_amount}', 'success')
                return redirect(url_for('import_old_data'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('import_old_data'))
    
    customers = Customer.query.all()
    staffs = User.query.filter_by(role='staff').all()
    return render_template('import_old_data.html', customers=customers, staffs=staffs)

@app.route('/fix_database_migration')
def fix_database_migration():
    try:
        from sqlalchemy import text, inspect
        
        # Check if loan_id column exists using inspector
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('loan_collections')]
        
        if 'loan_id' in columns:
            return "✅ Database is already up to date! loan_id column exists."
        
        # Add loan_id column
        db.session.execute(text("ALTER TABLE loan_collections ADD COLUMN loan_id INTEGER"))
        
        # Update existing records with default loan_id
        db.session.execute(text("UPDATE loan_collections SET loan_id = 1 WHERE loan_id IS NULL"))
        
        db.session.commit()
        return "✅ SUCCESS! Database migration completed. loan_id column added and updated. Individual Loan Sheets will now work properly. Please refresh the page."
        
    except Exception as e:
        db.session.rollback()
        return f"❌ Migration failed: {str(e)}. Please try running the migration script manually or contact support."

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
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)














