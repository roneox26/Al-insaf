# -*- coding: utf-8 -*-
# Collection Schedule Routes
# Add these routes to app.py

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.collection_schedule_model import CollectionSchedule
from models.customer_model import Customer
from models.loan_model import Loan
from models.user_model import User, db
from datetime import datetime, timedelta, date

# Route 1: View Collection Schedule
@app.route('/collection_schedule')
@login_required
def collection_schedule():
    date_filter = request.args.get('date_filter', 'today')
    status_filter = request.args.get('status_filter', 'all')
    staff_filter = request.args.get('staff_filter', type=int)
    
    today = date.today()
    query = CollectionSchedule.query
    
    # Apply filters
    if current_user.role == 'staff' and not current_user.is_office_staff:
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
    
    # Add days_diff for each schedule
    for schedule in schedules:
        schedule.days_diff = (schedule.scheduled_date.date() - today).days
    
    # Calculate summary stats
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

# Route 2: Reschedule Collection
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
        return jsonify({'success': True})
    return jsonify({'success': False}), 400

# Route 3: Auto-generate schedules when loan is created
def generate_collection_schedules(loan, customer):
    """Generate collection schedules for a loan"""
    if loan.installment_count <= 0:
        return
    
    current_date = loan.loan_date
    
    for i in range(loan.installment_count):
        if loan.installment_type == 'Daily':
            scheduled_date = current_date + timedelta(days=i+1)
        elif loan.installment_type == 'Weekly':
            scheduled_date = current_date + timedelta(weeks=i+1)
        elif loan.installment_type == 'Monthly':
            scheduled_date = current_date + timedelta(days=30*(i+1))
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

# Add this to your add_loan route after creating the loan:
# generate_collection_schedules(loan, customer)
