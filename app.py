# -*- coding: utf-8 -*-
import os
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
from models.scheduled_expense_model import ScheduledExpense
from models.collection_schedule_model import CollectionSchedule
from datetime import datetime, timedelta, date
import csv
import io
import pytz


app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

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
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not email or not password:
            flash('????? ??? ?????????? ??????!', 'danger')
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
    import os
    logo_path = os.path.join('static', 'images', 'logo.jpg')
    logo_exists = os.path.exists(logo_path)
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
        unread_messages = Message.query.filter_by(receiver_id=current_user.id, is_read=False).count()
        is_monitor = current_user.is_monitor if hasattr(current_user, 'is_monitor') else False
        
        # Get all staff for office staff
        all_staff = []
        is_office = hasattr(current_user, 'is_office_staff') and current_user.is_office_staff
        if is_office:
            all_staff = User.query.filter_by(role='staff').filter(User.id != current_user.id).order_by(User.name).all()
        
        import os
        logo_path = os.path.join('static', 'images', 'logo.jpg')
        logo_exists = os.path.exists(logo_path)
        return render_template('staff_dashboard.html', name=current_user.name, my_customers=my_customers, total_remaining=total_remaining, today_collections=today_collections, unread_messages=unread_messages, due_customers=due_customers, is_monitor=is_monitor, logo_exists=logo_exists, today=datetime.now(), all_staff=all_staff, is_office_staff=is_office)
    else:
        flash('Invalid role!', 'danger')
        return redirect(url_for('logout'))

@app.route('/admin/staffs')
@login_required
def manage_staff():
    if current_user.role != 'admin':
        flash('Access denied! Only admin can view this page.', 'danger')
        return redirect(url_for('dashboard'))

    period = request.args.get('period', 'daily')
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    
    today = datetime.now()
    
    if from_date and to_date:
        try:
            start_date = datetime.strptime(from_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
        except:
            start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == 'daily':
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == 'monthly':
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    else:
        start_date = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    staffs = User.query.filter_by(role='staff').all()
    staff_data = []
    
    query_loan = LoanCollection.query.filter(LoanCollection.collection_date >= start_date, LoanCollection.collection_date <= end_date)
    query_saving = SavingCollection.query.filter(SavingCollection.collection_date >= start_date, SavingCollection.collection_date <= end_date)
    
    all_loan_collections = query_loan.all()
    all_saving_collections = query_saving.all()
    
    for staff in staffs:
        loan_collection = sum(lc.amount for lc in all_loan_collections if lc.staff_id == staff.id)
        saving_collection = sum(sc.amount for sc in all_saving_collections if sc.staff_id == staff.id)
        total_collection = loan_collection + saving_collection
        
        staff_data.append({
            'staff': staff,
            'total_collection': total_collection
        })
    
    return render_template('manage_staff.html', staff_data=staff_data, period=period, from_date=from_date, to_date=to_date)

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
        staff_type = request.form.get('staff_type', 'field')
        
        if not name or not email or not password:
            flash('?? ???? ???? ????!', 'danger')
            return redirect(url_for('add_staff'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('add_staff'))
        
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
        
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        is_office_staff = staff_type == 'office'
        is_monitor = staff_type == 'monitor'
        salary = float(request.form.get('salary', 0) or 0)
        new_staff = User(name=name, email=email, password=hashed_pw, role='staff', is_office_staff=is_office_staff, is_monitor=is_monitor, phone=request.form.get('phone', '').strip(), nid=request.form.get('nid', '').strip(), address=request.form.get('address', '').strip(), salary=salary, photo=photo_filename)
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
            flash('??? ??? ????? ??????!', 'danger')
            return redirect(url_for('edit_staff', id=id))
        
        if request.form.get('remove_photo'):
            if staff.photo:
                import os
                photo_path = os.path.join('static', 'uploads', staff.photo)
                if os.path.exists(photo_path):
                    os.remove(photo_path)
                staff.photo = None
        
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo and photo.filename:
                import os
                from werkzeug.utils import secure_filename
                if staff.photo:
                    old_photo_path = os.path.join('static', 'uploads', staff.photo)
                    if os.path.exists(old_photo_path):
                        os.remove(old_photo_path)
                filename = secure_filename(photo.filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                photo_filename = f"{timestamp}_{filename}"
                photo_path = os.path.join('static', 'uploads', photo_filename)
                photo.save(photo_path)
                staff.photo = photo_filename
        
        staff.name = name
        staff.email = email
        staff_type = request.form.get('staff_type', 'field')
        staff.is_office_staff = staff_type == 'office'
        staff.is_monitor = staff_type == 'monitor'
        staff.phone = request.form.get('phone', '').strip()
        staff.nid = request.form.get('nid', '').strip()
        staff.address = request.form.get('address', '').strip()
        staff.status = request.form.get('status', 'active')
        staff.salary = float(request.form.get('salary', 0) or 0)
        
        if request.form.get('password'):
            staff.password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        
        db.session.commit()
        flash('Staff updated successfully!', 'success')
        return redirect(url_for('manage_staff'))
    
    return render_template('edit_staff.html', staff=staff)

@app.route('/staff/collection_report/<int:id>')
@login_required
def staff_collection_report(id):
    # Allow admin and office_staff to view any staff report, field staff can only view their own
    if current_user.role == 'staff':
        is_office = hasattr(current_user, 'is_office_staff') and current_user.is_office_staff
        if not is_office and current_user.id != id:
            flash('Access denied!', 'danger')
            return redirect(url_for('dashboard'))
    elif current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    staff = User.query.get_or_404(id)
    if staff.role != 'staff':
        flash('Invalid staff!', 'danger')
        return redirect(url_for('manage_staff'))
    
    period = request.args.get('period', 'daily')
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    
    today = datetime.now()
    
    if from_date and to_date:
        try:
            start_date = datetime.strptime(from_date, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, microsecond=999999)
        except:
            start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == 'daily':
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    elif period == 'monthly':
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    else:
        start_date = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    query_loan = LoanCollection.query.filter_by(staff_id=id).filter(LoanCollection.collection_date >= start_date, LoanCollection.collection_date <= end_date)
    query_saving = SavingCollection.query.filter_by(staff_id=id).filter(SavingCollection.collection_date >= start_date, SavingCollection.collection_date <= end_date)
    
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
    
    # Format dates for display
    period_display = ''
    if from_date and to_date:
        period_display = f"{datetime.strptime(from_date, '%Y-%m-%d').strftime('%d %B %Y')} to {datetime.strptime(to_date, '%Y-%m-%d').strftime('%d %B %Y')}"
    elif period == 'daily':
        period_display = f"Today ({today.strftime('%d %B %Y')})"
    elif period == 'monthly':
        period_display = f"{today.strftime('%B %Y')}"
    else:
        period_display = f"Year {today.year}"
    
    return render_template('staff_collection_report.html', staff=staff, daily_collections=daily_collections, total_loan=total_loan, total_saving=total_saving, period=period, from_date=from_date, to_date=to_date, period_display=period_display)

@app.route('/all_staff_report_print')
@login_required
def all_staff_report_print():
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    period = request.args.get('period', 'daily')
    
    today = datetime.now()
    if period == 'daily':
        start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'monthly':
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start_date = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    staffs = User.query.filter_by(role='staff').all()
    staff_data = []
    
    query_loan = LoanCollection.query.filter(LoanCollection.collection_date >= start_date)
    query_saving = SavingCollection.query.filter(SavingCollection.collection_date >= start_date)
    
    for staff in staffs:
        customers = Customer.query.filter_by(staff_id=staff.id).count()
        total_loan = query_loan.filter_by(staff_id=staff.id).with_entities(db.func.sum(LoanCollection.amount)).scalar() or 0
        total_saving = query_saving.filter_by(staff_id=staff.id).with_entities(db.func.sum(SavingCollection.amount)).scalar() or 0
        remaining_loan = db.session.query(db.func.sum(Customer.remaining_loan)).filter_by(staff_id=staff.id).scalar() or 0
        
        staff_data.append({
            'staff': staff,
            'customers': customers,
            'total_loan': total_loan,
            'total_saving': total_saving,
            'remaining_loan': remaining_loan,
            'total_collection': total_loan + total_saving
        })
    
    return render_template('all_staff_report_print.html', staff_data=staff_data, period=period)

@app.route('/admin/staff/delete/<int:id>', methods=['POST'])
@login_required
def delete_staff(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    password = request.form.get('password', '').strip()
    if not password:
        flash('?????????? ??????!', 'danger')
        return redirect(url_for('manage_staff'))
    
    if not bcrypt.check_password_hash(current_user.password, password):
        flash('?????????? ???! Staff ????? ??? ???????', 'danger')
        return redirect(url_for('manage_staff'))
    
    staff = User.query.get_or_404(id)
    if staff.role != 'staff':
        flash('Invalid staff!', 'danger')
        return redirect(url_for('manage_staff'))
    
    db.session.delete(staff)
    db.session.commit()
    flash('Staff ??????? ????? ??????!', 'success')
    return redirect(url_for('manage_staff'))

@app.route('/admin/staff/view/<int:id>')
@login_required
def staff_dashboard_view(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    staff = User.query.get_or_404(id)
    if staff.role != 'staff':
        flash('Invalid staff!', 'danger')
        return redirect(url_for('manage_staff'))
    
    my_customers = Customer.query.filter_by(staff_id=staff.id).count()
    total_remaining = db.session.query(db.func.sum(Customer.remaining_loan)).filter_by(staff_id=staff.id).scalar() or 0
    due_customers = Customer.query.filter_by(staff_id=staff.id).filter(Customer.remaining_loan > 0).count()
    today = datetime.now().replace(hour=0, minute=0, second=0)
    today_loan_collections = LoanCollection.query.filter_by(staff_id=staff.id).filter(LoanCollection.collection_date >= today).count()
    today_saving_collections = SavingCollection.query.filter_by(staff_id=staff.id).filter(SavingCollection.collection_date >= today).count()
    today_collections = today_loan_collections + today_saving_collections
    unread_messages = Message.query.filter_by(staff_id=staff.id, is_read=False).count()
    is_monitor = staff.is_monitor if hasattr(staff, 'is_monitor') else False
    
    return render_template('staff_dashboard_view.html', staff=staff, name=staff.name, my_customers=my_customers, total_remaining=total_remaining, today_collections=today_collections, unread_messages=unread_messages, due_customers=due_customers, is_monitor=is_monitor)




@app.route('/loans')
@login_required
def manage_loans():
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
    staffs = User.query.filter_by(role='staff').all()
    return render_template('manage_loans.html', loans=loans, staffs=staffs, filter_type=filter_type, month=month, year=year, total_amount=total_amount, total_interest=total_interest)

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
        flash('????????? Admin ??? ???? ?????!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            customer_id = request.form.get('customer_id', type=int)
            amount = request.form.get('amount', type=float, default=0)
            interest_rate = request.form.get('interest', type=float, default=0)
            
            if not customer_id or amount <= 0:
                flash('?? ???? ???????? ???? ????!', 'danger')
                return redirect(url_for('add_loan'))
            customer = Customer.query.get_or_404(customer_id)
            
            cash_balance_record = CashBalance.query.first()
            if not cash_balance_record:
                cash_balance_record = CashBalance(balance=0)
                db.session.add(cash_balance_record)
            
            if cash_balance_record.balance < amount:
                flash(f'???????? ???? ???! ??????? ?????????: ?{cash_balance_record.balance}', 'danger')
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
            
            # Generate collection schedules
            if loan.installment_count > 0:
                for i in range(loan.installment_count):
                    if loan.installment_type == 'Daily':
                        scheduled_date = loan_date + timedelta(days=i+1)
                    elif loan.installment_type == 'Weekly':
                        scheduled_date = loan_date + timedelta(weeks=i+1)
                    elif loan.installment_type == 'Monthly':
                        scheduled_date = loan_date + timedelta(days=30*(i+1))
                    else:
                        continue
                    
                    schedule = CollectionSchedule(
                        customer_id=customer.id,
                        loan_id=loan.id,
                        scheduled_date=scheduled_date,
                        expected_amount=loan.installment_amount,
                        collection_type='loan',
                        status='pending',
                        staff_id=customer.staff_id
                    )
                    db.session.add(schedule)
            
            db.session.commit()
            flash(f'?? ??? ???! ??????: ?{amount}, ???: ?{interest_amount}, ??????? ?????: ?{service_charge}, ?????? ??: ?{welfare_fee}, ????? ??: ?{application_fee}, ???: ?{total_with_interest}', 'success')
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
                flash('?? ???? ???????? ???? ????!', 'danger')
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
            flash('?? ???? ???????? ???? ????!', 'danger')
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
    try:
        # Monitor staff can view but not edit
        is_monitor = hasattr(current_user, 'is_monitor') and current_user.is_monitor
        
        if current_user.role == 'staff':
            # Office staff and monitor can see all customers
            is_office = hasattr(current_user, 'is_office_staff') and current_user.is_office_staff
            if is_office or is_monitor:
                customers = Customer.query.filter_by(is_active=True).all()
            else:
                # Field staff can only see their own customers
                customers = Customer.query.filter_by(staff_id=current_user.id, is_active=True).all()
        else:
            # Admin can see all customers
            customers = Customer.query.filter_by(is_active=True).all()
        
        return render_template('manage_customers.html', customers=customers)
    except Exception as e:
        flash(f'Error loading customers: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/all_customers_print')
@login_required
def all_customers_print():
    if current_user.role == 'staff' and (not hasattr(current_user, 'is_office_staff') or not current_user.is_office_staff):
        customers = Customer.query.filter_by(staff_id=current_user.id).order_by(Customer.member_no).all()
    else:
        customers = Customer.query.order_by(Customer.member_no).all()
    return render_template('all_customers_print.html', customers=customers)

@app.route('/loan_customers')
@login_required
def loan_customers():
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    
    if current_user.role == 'staff' and not current_user.is_office_staff and not current_user.is_monitor:
        query = Customer.query.filter_by(staff_id=current_user.id).filter(Customer.total_loan > 0)
    else:
        query = Customer.query.filter(Customer.total_loan > 0)
    
    from_date_display = ''
    to_date_display = ''
    
    if from_date and to_date:
        try:
            start = datetime.strptime(from_date, '%Y-%m-%d')
            end = datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            from_date_display = start.strftime('%d %B %Y')
            to_date_display = end.strftime('%d %B %Y')
            
            customer_ids = db.session.query(Customer.id).join(
                Loan, Customer.name == Loan.customer_name
            ).filter(
                Loan.loan_date >= start,
                Loan.loan_date <= end
            ).distinct().all()
            
            ids = [cid[0] for cid in customer_ids]
            
            if ids:
                query = query.filter(Customer.id.in_(ids))
            else:
                query = query.filter(Customer.id == -1)
        except Exception as e:
            print(f"Date filter error: {e}")
    elif from_date:
        try:
            start = datetime.strptime(from_date, '%Y-%m-%d')
            from_date_display = start.strftime('%d %B %Y')
            
            customer_ids = db.session.query(Customer.id).join(
                Loan, Customer.name == Loan.customer_name
            ).filter(
                Loan.loan_date >= start
            ).distinct().all()
            
            ids = [cid[0] for cid in customer_ids]
            
            if ids:
                query = query.filter(Customer.id.in_(ids))
            else:
                query = query.filter(Customer.id == -1)
        except Exception as e:
            print(f"Date filter error: {e}")
    
    customers = query.all()
    return render_template('loan_customers.html', customers=customers, from_date=from_date, to_date=to_date, from_date_display=from_date_display, to_date_display=to_date_display, now=datetime.now())

@app.route('/customer_details/<int:id>')
@login_required
def customer_details(id):
    customer = Customer.query.get_or_404(id)
    
    if current_user.role == 'staff' and not current_user.is_office_staff and not current_user.is_monitor and customer.staff_id != current_user.id:
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

@app.route('/customer_loan_sheet/<int:id>')
@login_required
def customer_loan_sheet(id):
    customer = Customer.query.get_or_404(id)
    loans = Loan.query.filter_by(customer_name=customer.name).all()
    loan_collections = LoanCollection.query.filter_by(customer_id=id).order_by(LoanCollection.collection_date).all()
    saving_collections = SavingCollection.query.filter_by(customer_id=id).all()
    withdrawals = Withdrawal.query.filter_by(customer_id=id).order_by(Withdrawal.date).all()
    from models.fee_model import FeeCollection
    admission_fee = db.session.query(db.func.sum(FeeCollection.amount)).filter_by(customer_id=id, fee_type='admission').scalar() or 0
    welfare_fee = db.session.query(db.func.sum(FeeCollection.amount)).filter_by(customer_id=id, fee_type='welfare').scalar() or 0
    application_fee = db.session.query(db.func.sum(FeeCollection.amount)).filter_by(customer_id=id, fee_type='application').scalar() or 0
    
    loan_principal = sum(loan.amount for loan in loans)
    interest_amount = sum(loan.amount * loan.interest / 100 for loan in loans)
    service_charge_total = sum(loan.service_charge for loan in loans)
    total_loan = sum(loan.amount + (loan.amount * loan.interest / 100) + loan.service_charge for loan in loans)
    total_collected = sum(lc.amount for lc in loan_collections)
    total_savings = sum(sc.amount for sc in saving_collections)
    total_withdrawn = sum(w.amount for w in withdrawals)
    
    installment_count = sum(loan.installment_count for loan in loans)
    weekly_installment = loans[0].installment_amount if loans else 0
    loan_date = loans[0].loan_date.strftime('%d-%m-%Y') if loans else ''
    loan_end_date = ''
    if loans and loans[0].loan_date and installment_count > 0:
        from datetime import timedelta
        loan_end_date = (loans[0].loan_date + timedelta(weeks=installment_count)).strftime('%d-%m-%Y')
    interest_rate = loans[0].interest if loans else 0
    
    staff = User.query.get(customer.staff_id) if customer.staff_id else None
    
    return render_template('customer_loan_sheet.html', customer=customer, loans=loans, loan_collections=loan_collections, withdrawals=withdrawals, total_loan=total_loan, total_collected=total_collected, total_withdrawn=total_withdrawn, installment_count=installment_count, weekly_installment=weekly_installment, staff=staff, loan_date=loan_date, loan_end_date=loan_end_date, interest_rate=interest_rate, loan_principal=loan_principal, interest_amount=interest_amount, service_charge_total=service_charge_total, total_savings=total_savings, admission_fee=admission_fee, welfare_fee=welfare_fee, application_fee=application_fee, now=datetime.now())

@app.route('/customer/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    
    if current_user.role == 'staff' and not current_user.is_office_staff and customer.staff_id != current_user.id:
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
            flash('??? ??? ??? ????? ??????!', 'danger')
            return redirect(url_for('edit_customer', id=id))
        
        db.session.commit()
        flash('???????? ????? ??? ??????!', 'success')
        return redirect(url_for('manage_customers'))
    
    return render_template('edit_customer.html', customer=customer)

@app.route('/customer/delete/<int:id>', methods=['POST'])
@login_required
def delete_customer(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('manage_customers'))
    
    password = request.form.get('password', '').strip()
    if not password:
        flash('?????????? ??????!', 'danger')
        return redirect(url_for('manage_customers'))
    
    if not bcrypt.check_password_hash(current_user.password, password):
        flash('?????????? ???! Customer ????? ??? ???????', 'danger')
        return redirect(url_for('manage_customers'))
    
    customer = Customer.query.get_or_404(id)
    customer.is_active = False
    db.session.commit()
    flash('Customer ??????? Deactivate ??????!', 'success')
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
    flash('Customer ??????? Activate ??????!', 'success')
    return redirect(url_for('inactive_customers'))

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
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            phone = request.form.get('phone', '').strip()
            member_no = request.form.get('member_no', '').strip()
            
            if not name or not phone:
                flash('??? ??? ??? ????? ??????!', 'danger')
                return redirect(url_for('add_customer'))
            
            # Check if member_no already exists
            if member_no and Customer.query.filter_by(member_no=member_no).first():
                flash(f'????? ?? "{member_no}" ???????? ??????? ??????!', 'danger')
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
            flash(f'????? ??????? ??? ??????! ????? ??: ?{admission_fee}', 'success')
            return redirect(url_for('manage_customers'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('add_customer'))
    return render_template('add_customer.html')

@app.route('/collections')
@login_required
def manage_collections():
    staff_id = request.args.get('staff_id', type=int)
    period = request.args.get('period', 'all')
    selected_date = request.args.get('date')
    
    if current_user.role == 'staff' and (not hasattr(current_user, 'is_office_staff') or not current_user.is_office_staff):
        query_loan = LoanCollection.query.filter_by(staff_id=current_user.id)
        query_saving = SavingCollection.query.filter_by(staff_id=current_user.id)
    else:
        query_loan = LoanCollection.query
        query_saving = SavingCollection.query
        
        if staff_id:
            query_loan = query_loan.filter_by(staff_id=staff_id)
            query_saving = query_saving.filter_by(staff_id=staff_id)
    
    from datetime import date
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
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        query_loan = query_loan.filter(LoanCollection.collection_date >= start_date)
        query_saving = query_saving.filter(SavingCollection.collection_date >= start_date)
        month_names = ['?????????', '???????????', '?????', '??????', '??', '???', '?????', '?????', '??????????', '???????', '???????', '????????']
        period_info['month'] = month_names[today.month - 1]
        period_info['year'] = today.year
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
        loan_id = request.form.get('loan_id', type=int)
        amount = request.form.get('amount', type=float, default=0)
        
        if not loan_id or amount <= 0:
            flash('?? ???? ???????? ???? ????!', 'danger')
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
    if current_user.role == 'staff' and hasattr(current_user, 'is_monitor') and current_user.is_monitor:
        flash('Monitor staff ??????? ???? ????? ??!', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        customer_id = request.form.get('customer_id', type=int)
        loan_amount = request.form.get('loan_amount', type=float, default=0)
        saving_amount = request.form.get('saving_amount', type=float, default=0)
        
        if not customer_id:
            flash('?????? ???????? ????!', 'danger')
            return redirect(url_for('collection'))
        
        if loan_amount <= 0 and saving_amount <= 0:
            flash('????? ???? ??????? ?????? ???!', 'danger')
            return redirect(url_for('collection'))
        
        customer = Customer.query.get_or_404(customer_id)
        
        cash_balance_record = CashBalance.query.first()
        if not cash_balance_record:
            cash_balance_record = CashBalance(balance=0)
            db.session.add(cash_balance_record)
        
        # Process loan collection
        if loan_amount > 0:
            if loan_amount > customer.remaining_loan:
                flash(f'??? ???? ???? ??? (?{customer.remaining_loan}) ???? ???? ??? ????? ??!', 'danger')
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
            msg.append(f'???: ?{loan_amount}')
        if saving_amount > 0:
            msg.append(f'??????: ?{saving_amount}')
        flash(f'??????? ??????? ??????? ??????! {" | ".join(msg)}', 'success')
        return redirect(url_for('collection'))
    
    if current_user.role == 'staff' and (not hasattr(current_user, 'is_office_staff') or not current_user.is_office_staff):
        customers = Customer.query.filter_by(staff_id=current_user.id).all()
    else:
        customers = Customer.query.all()
    return render_template('collection.html', customers=customers)

@app.route('/loan_collection', methods=['GET'])
@login_required
def loan_collection():
    if current_user.role == 'staff' and hasattr(current_user, 'is_monitor') and current_user.is_monitor:
        flash('Monitor staff ??????? ???? ????? ??!', 'danger')
        return redirect(url_for('dashboard'))
    
    if current_user.role == 'staff' and (not hasattr(current_user, 'is_office_staff') or not current_user.is_office_staff):
        customers = Customer.query.filter_by(staff_id=current_user.id).filter(Customer.remaining_loan > 0).all()
    else:
        customers = Customer.query.filter(Customer.remaining_loan > 0).all()
    return render_template('loan_collection.html', customers=customers)

@app.route('/saving_collection', methods=['GET'])
@login_required
def saving_collection():
    if current_user.role == 'staff' and hasattr(current_user, 'is_monitor') and current_user.is_monitor:
        flash('Monitor staff ??????? ???? ????? ??!', 'danger')
        return redirect(url_for('dashboard'))
    
    if current_user.role == 'staff' and (not hasattr(current_user, 'is_office_staff') or not current_user.is_office_staff):
        customers = Customer.query.filter_by(staff_id=current_user.id).all()
    else:
        customers = Customer.query.all()
    return render_template('saving_collection.html', customers=customers)

@app.route('/loan_collection/collect', methods=['POST'])
@login_required
def collect_loan():
    if current_user.role == 'staff' and hasattr(current_user, 'is_monitor') and current_user.is_monitor:
        flash('Monitor staff ??????? ???? ????? ??!', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        customer_id = request.form.get('customer_id', type=int)
        amount = request.form.get('amount', type=float, default=0)
        
        if not customer_id or amount <= 0:
            flash('?? ???? ???????? ???? ????!', 'danger')
            return redirect(url_for('loan_collection'))
        
        customer = Customer.query.get_or_404(customer_id)
        
        if amount <= 0:
            flash('????? ?????? ? ?? ???? ??? ???!', 'danger')
            return redirect(url_for('loan_collection'))
        
        if amount > customer.remaining_loan:
            flash(f'???? ???? ??? (?{customer.remaining_loan}) ???? ???? ??? ????? ??!', 'danger')
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
        
        # Update collection schedule
        schedule = CollectionSchedule.query.filter_by(
            customer_id=customer_id,
            status='pending'
        ).order_by(CollectionSchedule.scheduled_date).first()
        
        if schedule:
            schedule.status = 'collected'
            schedule.collected_amount = amount
            schedule.collected_date = datetime.now()
        
        db.session.commit()
        
        flash(f'??????? ?{amount} ??????? ??????? ??????! ????: ?{customer.remaining_loan}', 'success')
        return redirect(url_for('loan_collection'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('loan_collection'))

@app.route('/saving_collection/collect', methods=['POST'])
@login_required
def collect_saving():
    if current_user.role == 'staff' and hasattr(current_user, 'is_monitor') and current_user.is_monitor:
        flash('Monitor staff ??????? ???? ????? ??!', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        customer_id = request.form.get('customer_id', type=int)
        amount = request.form.get('amount', type=float, default=0)
        
        if not customer_id or amount <= 0:
            flash('?? ???? ???????? ???? ????!', 'danger')
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
        
        flash(f'??????? ?{amount} ?????? ??? ??????!', 'success')
        return redirect(url_for('saving_collection'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('saving_collection'))

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
    
    if current_user.role == 'staff' and (not hasattr(current_user, 'is_office_staff') or not current_user.is_office_staff):
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
    
    return render_template('daily_collections.html', all_collections=all_collections, total_loan=total_loan, total_saving=total_saving, logo_exists=logo_exists, today=datetime.now(), selected_date=today_date)

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
                flash('?? ???? ???????? ???? ????!', 'danger')
                return redirect(url_for('manage_cash_balance'))
            
            cash_balance_record = CashBalance.query.first()
            if not cash_balance_record:
                cash_balance_record = CashBalance(balance=0)
                db.session.add(cash_balance_record)
            
            if action == 'add':
                investor_name = request.form.get('investor_name', '').strip()
                note = request.form.get('note', '')
                
                if not investor_name:
                    flash('Investor ??? ??????!', 'danger')
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
                flash(f'Investor ID: {investor.investor_id} | ?{amount} ??? ??? ??????! Balance: ?{investor.current_balance}', 'success')
            elif action == 'subtract':
                if cash_balance_record.balance >= amount:
                    cash_balance_record.balance -= amount
                    flash(f'?{amount} ?????? ??? ??????!', 'success')
                else:
                    flash('???????? ???? ???!', 'danger')
            elif action == 'withdraw':
                investor_name = request.form.get('investor_name', '').strip()
                note = request.form.get('note', '')
                
                if not investor_name:
                    flash('Investor ??? ??????!', 'danger')
                    return redirect(url_for('manage_cash_balance'))
                
                if cash_balance_record.balance >= amount:
                    investor = Investor.query.filter_by(name=investor_name).first()
                    if not investor:
                        flash('Investor ????? ?????? ??????!', 'danger')
                        return redirect(url_for('manage_cash_balance'))
                    
                    if investor.current_balance < amount:
                        flash(f'Investor ?? balance (?{investor.current_balance}) ?????? ???!', 'danger')
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
                    flash(f'Investor ID: {investor.investor_id} | ?{amount} Withdrawal ??? ??????! Balance: ?{investor.current_balance}', 'success')
                else:
                    flash('???????? ???? ???!', 'danger')
            
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
                flash('?? ???? ???????? ???? ????!', 'danger')
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
                flash(f'{category} - ?{amount} ????? ??? ??????!', 'success')
            else:
                flash('???????? ???? ???!', 'danger')
            
            return redirect(url_for('manage_expenses'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('manage_expenses'))
    
    filter_type = request.args.get('filter_type', 'all')
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    
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
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    
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
    
    # Net Profit/Loss = Income - (Expenses + Withdrawals)
    net_profit = total_income - (total_expenses + total_withdrawals)
    
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
                         net_profit=net_profit,
                         salary_exp=salary_exp,
                         office_exp=office_exp,
                         transport_exp=transport_exp,
                         other_exp=other_exp)

@app.route('/messages')
@login_required
def view_messages():
    # Get conversation partner ID from query params
    partner_id = request.args.get('user_id', type=int)
    
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
    receiver_id = request.form.get('receiver_id', type=int)
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
                flash('?? ???? ???????? ???? ????!', 'danger')
                return redirect(url_for('manage_withdrawals'))
            
            customer = Customer.query.get_or_404(customer_id)
            
            if customer.savings_balance < amount:
                flash(f'???????? ?????? ???! ???????: ?{customer.savings_balance}', 'danger')
                return redirect(url_for('manage_withdrawals'))
            
            cash_balance_record = CashBalance.query.first()
            if not cash_balance_record or cash_balance_record.balance < amount:
                flash('???????? ????? ???!', 'danger')
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
            flash(f'?{amount} ??????? ??? ??????!', 'success')
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
    
    month_names = ['', '?????????', '???????????', '?????', '??????', '??', '???', '?????', '?????', '??????????', '???????', '???????', '????????']
    month_name = month_names[month]
    last_day = calendar.monthrange(year, month)[1]
    
    month_start = datetime(year, month, 1)
    month_end = datetime(year, month, last_day, 23, 59, 59)
    
    daily_data = {}
    running_balance = 0
    
    # Get opening balance (cash balance at start of month)
    prev_month_end = month_start - timedelta(days=1)
    cash_balance_record = CashBalance.query.first()
    current_cash = cash_balance_record.balance if cash_balance_record else 0
    
    # Calculate opening balance by working backwards from current balance
    future_income = 0
    future_expense = 0
    
    if month_end < datetime.now():
        # Past month - calculate from transactions after month end
        after_month = datetime.now()
        loan_after = LoanCollection.query.filter(LoanCollection.collection_date > month_end).all()
        saving_after = SavingCollection.query.filter(SavingCollection.collection_date > month_end).all()
        loans_after = Loan.query.filter(Loan.loan_date > month_end).all()
        withdrawals_after = Withdrawal.query.filter(Withdrawal.date > month_end).all()
        expenses_after = Expense.query.filter(Expense.date > month_end).all()
        investments_after = Investment.query.filter(Investment.date > month_end).all()
        
        future_income = sum(lc.amount for lc in loan_after) + sum(sc.amount for sc in saving_after) + sum(inv.amount for inv in investments_after)
        future_expense = sum(l.amount for l in loans_after) + sum(w.amount for w in withdrawals_after) + sum(e.amount for e in expenses_after)
    
    opening_balance = current_cash - future_income + future_expense
    running_balance = opening_balance
    
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
        
        # Get actual fees from FeeCollection
        welfare_fee = db.session.query(db.func.sum(FeeCollection.amount)).filter(
            FeeCollection.fee_type == 'welfare',
            FeeCollection.collection_date >= day_start,
            FeeCollection.collection_date <= day_end
        ).scalar() or 0
        
        application_fee_actual = db.session.query(db.func.sum(FeeCollection.amount)).filter(
            FeeCollection.fee_type == 'application',
            FeeCollection.collection_date >= day_start,
            FeeCollection.collection_date <= day_end
        ).scalar() or 0
        
        loan_with_interest = loan_given + interest
        savings_return = sum(w.amount for w in withdrawals)
        expenses_total = sum(e.amount for e in expenses)
        investment_amount = sum(inv.amount for inv in investments)
        
        total_income = installments + savings + service_charge + admission_fee + welfare_fee + application_fee_actual + investment_amount
        total_expense = loan_given + savings_return + expenses_total
        day_balance = total_income - total_expense
        running_balance += day_balance
        
        daily_data[day] = {
            'savings': savings,
            'installments': installments,
            'welfare_fee': welfare_fee,
            'admission_fee': admission_fee,
            'service_charge': application_fee_actual,
            'capital_savings': investment_amount,
            'total_income': total_income,
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
    
    # Calculate monthly due (this month's expected collections that weren't collected)
    total_installments_collected = sum(d['installments'] for d in daily_data.values())
    
    # Calculate expected installments for this month
    expected_installments = 0
    for customer in Customer.query.filter(Customer.total_loan > 0).all():
        loans = Loan.query.filter_by(customer_name=customer.name).all()
        for loan in loans:
            if loan.loan_date <= month_end:
                if loan.installment_type == 'Daily':
                    days_in_month = min(last_day, (datetime.now() - month_start).days + 1) if month == today.month and year == today.year else last_day
                    expected_installments += loan.installment_amount * days_in_month
                elif loan.installment_type == 'Weekly':
                    weeks_in_month = last_day // 7
                    expected_installments += loan.installment_amount * weeks_in_month
                elif loan.installment_type == 'Monthly':
                    expected_installments += loan.installment_amount
    
    monthly_due = max(0, expected_installments - total_installments_collected)
    
    # Calculate closing balance (cash in hand at end of month)
    closing_balance = running_balance
    
    return render_template('monthly_report.html', month=month, month_name=month_name, year=year, daily_data=daily_data, last_day=last_day, total_capital_savings=total_capital_savings, total_loan_distributed=total_loan_distributed, total_interest=total_interest, prev_remaining=prev_remaining, current_remaining=current_remaining, total_monthly_expenses=total_monthly_expenses, opening_balance=opening_balance, closing_balance=closing_balance, monthly_due=monthly_due)

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
    return {'customers': [{
        'id': c.id,
        'name': c.name,
        'member_no': c.member_no or 'N/A',
        'phone': c.phone or 'N/A',
        'village': c.village or 'N/A',
        'remaining_loan': float(c.remaining_loan),
        'savings_balance': float(c.savings_balance),
        'staff_name': c.staff.name if c.staff else 'N/A'
    } for c in customers]}

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
    
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    
    query = FeeCollection.query.filter_by(fee_type=fee_type)
    if from_date:
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
    return render_template('fee_history.html', fees=fees, total=total, fee_type=fee_type, fee_name=fee_types[fee_type], from_date=from_date, to_date=to_date)

@app.route('/fee_print/<fee_type>')
@login_required
def fee_print(fee_type):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    fee_types = {'admission': 'ভর্তি ফি', 'welfare': 'কল্যাণ ফি', 'application': 'আবেদন ফি'}
    if fee_type not in fee_types:
        flash('Invalid fee type!', 'danger')
        return redirect(url_for('dashboard'))
    
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    
    query = FeeCollection.query.filter_by(fee_type=fee_type)
    if from_date:
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
    return render_template('fee_print.html', fees=fees, total=total, fee_type=fee_type, fee_name=fee_types[fee_type], from_date=from_date, to_date=to_date, now=datetime.now())

@app.route('/all_fees_history')
@login_required
def all_fees_history():
    if current_user.role not in ['admin', 'office', 'staff']:
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    
    query = FeeCollection.query
    if from_date:
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
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    
    query = FeeCollection.query
    if from_date:
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
    return render_template('all_fees_print.html', fees=grouped_fees, total=total, admission_total=admission_total, welfare_total=welfare_total, application_total=application_total, from_date=from_date, to_date=to_date)

@app.route('/due_report')
@login_required
def due_report():
    from datetime import date, timedelta
    
    staff_filter = request.args.get('staff_id', type=int)
    min_due = request.args.get('min_due', type=float, default=0)
    max_due = request.args.get('max_due', type=float)
    min_days = request.args.get('min_days', type=int, default=0)
    risk_level = request.args.get('risk_level', '')
    village_filter = request.args.get('village', '')
    
    if current_user.role == 'staff' and (not hasattr(current_user, 'is_office_staff') or not current_user.is_office_staff):
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
    writer.writerow(['??????', '????? ??', '???', '???', '??????', '?????? ????', '??? ??????', 
                     '????????', '?????? ??????', '??? ???????', '??????? ?????', '??? ????', '????? ????'])
    
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
    amount_promised = request.form.get('amount_promised', type=float, default=0)
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
    
    flash('???-?? ??? ??????!', 'success')
    return redirect(url_for('customer_details', id=customer_id))

@app.route('/followup/complete/<int:id>', methods=['POST'])
@login_required
def complete_followup(id):
    from models.followup_model import FollowUp
    
    followup = FollowUp.query.get_or_404(id)
    amount_collected = request.form.get('amount_collected', type=float, default=0)
    
    followup.status = 'completed'
    followup.amount_collected = amount_collected
    
    db.session.commit()
    flash('???-?? ??????? ??????!', 'success')
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
            flash('??????? ??? ?????????? ??????!', 'danger')
            return redirect(url_for('manage_notes'))
        
        reminder_date = None
        if reminder_date_str:
            reminder_date = datetime.strptime(reminder_date_str, '%Y-%m-%d')
        
        note = Note(title=title, content=content, priority=priority, reminder_date=reminder_date, created_by=current_user.id)
        db.session.add(note)
        db.session.commit()
        flash('??? ??????? ??? ??????!', 'success')
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
            flash('??????? ??? ?????????? ??????!', 'danger')
            return redirect(url_for('edit_note', id=id))
        
        db.session.commit()
        flash('??? ????? ???!', 'success')
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
    flash('??? ????? ???!', 'success')
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
                flash('?? ???? ???? ????!', 'danger')
                return redirect(url_for('admin_settings'))
            
            if not bcrypt.check_password_hash(current_user.password, password):
                flash('?????????? ???!', 'danger')
                return redirect(url_for('admin_settings'))
            
            if User.query.filter(User.email == new_email, User.id != current_user.id).first():
                flash('?? ????? ???????? ??????? ?????!', 'danger')
                return redirect(url_for('admin_settings'))
            
            current_user.email = new_email
            db.session.commit()
            flash('????? ??????? ???????? ??????!', 'success')
            return redirect(url_for('admin_settings'))
        
        elif action == 'change_password':
            current_password = request.form.get('current_password', '').strip()
            new_password = request.form.get('new_password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            if not current_password or not new_password or not confirm_password:
                flash('?? ???? ???? ????!', 'danger')
                return redirect(url_for('admin_settings'))
            
            if not bcrypt.check_password_hash(current_user.password, current_password):
                flash('??????? ?????????? ???!', 'danger')
                return redirect(url_for('admin_settings'))
            
            if new_password != confirm_password:
                flash('???? ?????????? ????? ??!', 'danger')
                return redirect(url_for('admin_settings'))
            
            if len(new_password) < 6:
                flash('?????????? ??????? ? ??????? ??? ???!', 'danger')
                return redirect(url_for('admin_settings'))
            
            current_user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            db.session.commit()
            flash('?????????? ??????? ???????? ??????!', 'success')
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
            amount = request.form.get('amount', type=float, default=0)
            description = request.form.get('description', '')
            frequency = request.form.get('frequency', '')
            start_date_str = request.form.get('start_date')
            
            if not category or amount <= 0 or not frequency:
                flash('?? ???? ???????? ???? ????!', 'danger')
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
            flash(f'?????? ????? ??? ??????! {frequency} - ?{amount}', 'success')
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
    flash(f'?????? ????? {status} ??? ??????!', 'success')
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
    flash('?????? ????? ????? ??????!', 'success')
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
    
    return render_template('investor_details.html', investor=investor, investments=investments, withdrawals=withdrawals)

@app.route('/investor_details_print/<int:id>')
@login_required
def investor_details_print(id):
    if current_user.role != 'admin':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    investor = Investor.query.get_or_404(id)
    investments = Investment.query.filter_by(investor_id=id).order_by(Investment.date.desc()).all()
    withdrawals = Withdrawal.query.filter_by(investor_id=id).order_by(Withdrawal.date.desc()).all()
    
    return render_template('investor_details_print.html', investor=investor, investments=investments, withdrawals=withdrawals)

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
            
            loan_amount = db.session.query(db.func.sum(LoanCollection.amount)).filter(
                LoanCollection.customer_id == customer.id,
                LoanCollection.collection_date >= day_start,
                LoanCollection.collection_date <= day_end
            ).scalar() or 0
            
            saving_amount = db.session.query(db.func.sum(SavingCollection.amount)).filter(
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
    staff_filter = request.args.get('staff_filter', type=int)
    
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
    if current_user.role == 'monitor':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    if current_user.role == 'field_staff':
        customers = Customer.query.filter_by(is_active=True, staff_id=current_user.id).order_by(Customer.member_no).all()
    else:
        customers = Customer.query.filter_by(is_active=True).order_by(Customer.member_no).all()
    return render_template('application_forms.html', customers=customers)

@app.route('/loan_application_form')
@login_required
def loan_application_form():
    if current_user.role == 'monitor':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    customer_id = request.args.get('customer_id', type=int)
    customer = Customer.query.get(customer_id) if customer_id else None
    
    if current_user.role == 'field_staff':
        customers = Customer.query.filter_by(is_active=True, staff_id=current_user.id).order_by(Customer.member_no).all()
    else:
        customers = Customer.query.filter_by(is_active=True).order_by(Customer.member_no).all()
    return render_template('loan_application_form.html', customer=customer, customers=customers)

@app.route('/commitment_form')
@login_required
def commitment_form():
    if current_user.role == 'monitor':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    customer_id = request.args.get('customer_id', type=int)
    customer = Customer.query.get(customer_id) if customer_id else None
    
    if current_user.role == 'field_staff':
        customers = Customer.query.filter_by(is_active=True, staff_id=current_user.id).order_by(Customer.member_no).all()
    else:
        customers = Customer.query.filter_by(is_active=True).order_by(Customer.member_no).all()
    return render_template('commitment_form.html', customer=customer, customers=customers)

@app.route('/angikarnama_form')
@login_required
def angikarnama_form():
    if current_user.role == 'monitor':
        flash('Access denied!', 'danger')
        return redirect(url_for('dashboard'))
    
    customer_id = request.args.get('customer_id', type=int)
    customer = Customer.query.get(customer_id) if customer_id else None
    
    if current_user.role == 'field_staff':
        customers = Customer.query.filter_by(is_active=True, staff_id=current_user.id).order_by(Customer.member_no).all()
    else:
        customers = Customer.query.filter_by(is_active=True).order_by(Customer.member_no).all()
    return render_template('angikarnama_form.html', customer=customer, customers=customers)

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
                staff_id = request.form.get('staff_id', type=int)
                total_loan = float(request.form.get('total_loan', 0) or 0)
                remaining_loan = float(request.form.get('remaining_loan', 0) or 0)
                savings_balance = float(request.form.get('savings_balance', 0) or 0)
                created_date_str = request.form.get('created_date', '')
                
                if not name:
                    flash('??? ????????!', 'danger')
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
                
                flash(f'?????? Customer "{name}" ??????? ??? ??? ??????!', 'success')
                return redirect(url_for('import_old_data'))
            
            elif action == 'add_collection':
                customer_id = request.form.get('customer_id', type=int)
                loan_amount = float(request.form.get('loan_amount', 0) or 0)
                saving_amount = float(request.form.get('saving_amount', 0) or 0)
                collection_date_str = request.form.get('collection_date', '')
                staff_id = request.form.get('staff_id', type=int) or current_user.id
                
                if not customer_id:
                    flash('Customer ???????? ????!', 'danger')
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
                flash(f'?????? Collection ??? ??? ??????! ???: ?{loan_amount}, ??????: ?{saving_amount}', 'success')
                return redirect(url_for('import_old_data'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('import_old_data'))
    
    customers = Customer.query.all()
    staffs = User.query.filter_by(role='staff').all()
    return render_template('import_old_data.html', customers=customers, staffs=staffs)

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
    app.run(debug=True, host='0.0.0.0', port=5000)






