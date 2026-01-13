# 📅 Collection Schedule System - Installation Guide

## ✅ যা ইতিমধ্যে তৈরি হয়েছে:

1. **Model**: `models/collection_schedule_model.py`
2. **Template**: `templates/collection_schedule.html`
3. **Routes**: `collection_schedule_routes.py`

---

## 🔧 Installation Steps:

### Step 1: Database Model Import করুন

`app.py` ফাইলের শুরুতে import section এ যোগ করুন:

```python
from models.collection_schedule_model import CollectionSchedule
```

### Step 2: Routes যোগ করুন

`app.py` ফাইলে `@app.route('/logout')` এর আগে নিচের routes গুলো যোগ করুন:

```python
# Collection Schedule Routes
@app.route('/collection_schedule')
@login_required
def collection_schedule():
    date_filter = request.args.get('date_filter', 'today')
    status_filter = request.args.get('status_filter', 'all')
    staff_filter = request.args.get('staff_filter', type=int)
    
    today = date.today()
    query = CollectionSchedule.query
    
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
        return jsonify({'success': True})
    return jsonify({'success': False}), 400
```

### Step 3: Auto Schedule Generation

`add_loan()` function এ loan তৈরির পর এই code যোগ করুন:

```python
# After: db.session.add(loan)
# Before: db.session.commit()

# Generate collection schedules
if loan.installment_count > 0:
    current_date = loan_date
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
```

### Step 4: Update Collection Status

`collect_loan()` function এ collection এর পর schedule update করুন:

```python
# After successful collection
# Find and update schedule
schedule = CollectionSchedule.query.filter_by(
    customer_id=customer_id,
    status='pending'
).order_by(CollectionSchedule.scheduled_date).first()

if schedule:
    schedule.status = 'collected'
    schedule.collected_amount = amount
    schedule.collected_date = datetime.now()
```

### Step 5: Database Update

Terminal এ run করুন:

```bash
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

অথবা:

```bash
python create_db.py
```

### Step 6: Navigation Link যোগ করুন

Dashboard template এ link যোগ করুন:

```html
<a href="{{ url_for('collection_schedule') }}" class="btn btn-primary">
  📅 কালেকশন শিডিউল
</a>
```

---

## 🎯 Features:

✅ **স্বয়ংক্রিয় শিডিউল তৈরি** - লোন দেওয়ার সময়
✅ **আজকের কালেকশন** - আজ কার কাছ থেকে টাকা নিতে হবে
✅ **আগামী সপ্তাহ** - পরবর্তী ৭ দিনের শিডিউল
✅ **বকেয়া ট্র্যাকিং** - মিসড কালেকশন দেখা
✅ **রিশিডিউল** - তারিখ পরিবর্তন করা
✅ **স্টাফ ফিল্টার** - স্টাফ অনুযায়ী দেখা
✅ **স্ট্যাটাস ট্র্যাকিং** - Pending, Collected, Missed

---

## 📊 Dashboard Integration:

Admin/Staff Dashboard এ আজকের কালেকশন দেখানোর জন্য:

```python
# In dashboard() function
from datetime import date
today = date.today()
today_schedules = CollectionSchedule.query.filter(
    db.func.date(CollectionSchedule.scheduled_date) == today,
    CollectionSchedule.status == 'pending'
).count()

# Pass to template: today_schedules=today_schedules
```

---

## 🔗 URL:

- **View Schedule**: `/collection_schedule`
- **Filter by Date**: `/collection_schedule?date_filter=today`
- **Filter by Status**: `/collection_schedule?status_filter=pending`
- **Filter by Staff**: `/collection_schedule?staff_filter=1`

---

## 📱 Mobile Friendly:

Template টি Bootstrap 5 দিয়ে তৈরি, তাই mobile এ ভালো দেখাবে।

---

## 🎨 Color Coding:

- 🟢 **আজ** - সবুজ background
- 🟡 **আগামী** - হলুদ background  
- 🔴 **বকেয়া** - লাল background
- ⚪ **সংগৃহীত** - ধূসর

---

## ⚠️ Important Notes:

1. প্রথমে database backup নিন
2. Test environment এ প্রথমে চেষ্টা করুন
3. Existing loans এর জন্য manually schedule তৈরি করতে হবে

---

## 🐛 Troubleshooting:

**Error: No module named 'collection_schedule_model'**
- Solution: `models/collection_schedule_model.py` ফাইল আছে কিনা check করুন

**Error: Table doesn't exist**
- Solution: `python create_db.py` run করুন

**Schedule দেখাচ্ছে না**
- Solution: নতুন loan দিয়ে test করুন

---

## 📞 Support:

কোনো সমস্যা হলে GitHub এ issue করুন।

---

**Happy Coding! 🚀**
