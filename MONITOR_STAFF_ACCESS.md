# Monitor Staff Access Control

## Overview
Monitor Staff হলো একটি বিশেষ ধরনের staff যারা শুধুমাত্র সিস্টেমের তথ্য দেখতে পারবে, কিন্তু কোনো পরিবর্তন করতে পারবে না।

## Monitor Staff এর Access

### ✅ যা করতে পারবে (Read-Only Access):

1. **Customer Management**
   - সব customers দেখতে পারবে
   - Customer details দেখতে পারবে
   - Loan customers দেখতে পারবে
   - Inactive customers দেখতে পারবে

2. **Reports & Analytics**
   - Daily collections দেখতে পারবে
   - Daily reports দেখতে পারবে
   - Due reports দেখতে পারবে
   - Collections history দেখতে পারবে
   - Loan collections history দেখতে পারবে
   - Savings collections history দেখতে পারবে

3. **Dashboard**
   - সব customers এর সংখ্যা দেখতে পারবে
   - Total বকেয়া লোন দেখতে পারবে
   - Due customers দেখতে পারবে
   - System status দেখতে পারবে

### ❌ যা করতে পারবে না:

1. **Collections**
   - কোনো collection করতে পারবে না
   - লোন collection করতে পারবে না
   - সঞ্চয় collection করতে পারবে না

2. **Customer Management**
   - নতুন customer যোগ করতে পারবে না
   - Customer edit করতে পারবে না
   - Customer delete করতে পারবে না

3. **Loan Management**
   - নতুন loan দিতে পারবে না
   - Loan edit করতে পারবে না
   - Loan delete করতে পারবে না

4. **Forms & Documents**
   - Application forms print করতে পারবে না
   - Loan application form print করতে পারবে না
   - Commitment form print করতে পারবে না
   - Angikarnama form print করতে পারবে না

5. **Financial Operations**
   - Cash balance manage করতে পারবে না
   - Expenses add করতে পারবে না
   - Withdrawals করতে পারবে না
   - Investments manage করতে পারবে না

## Monitor Staff তৈরি করার নিয়ম

### Option 1: Admin Dashboard থেকে

1. Admin হিসেবে login করুন
2. "Manage Staff" এ যান
3. "Add Staff" ক্লিক করুন
4. Staff এর তথ্য দিন
5. "Staff Type" এ "Monitor Staff" select করুন
6. Save করুন

### Option 2: Database Script দিয়ে

```python
from app import app, db, User, bcrypt

with app.app_context():
    # Create monitor staff
    hashed_pw = bcrypt.generate_password_hash('monitor123').decode('utf-8')
    monitor = User(
        name='Monitor Staff',
        email='monitor@example.com',
        password=hashed_pw,
        role='staff',
        is_monitor=True,
        plain_password='monitor123'
    )
    db.session.add(monitor)
    db.session.commit()
    print("Monitor staff created successfully!")
```

## Dashboard এ Monitor Staff এর View

Monitor Staff login করলে dashboard এ দেখাবে:

```
Welcome, Monitor Staff Name
Monitor Staff | Read-Only Access (শুধুমাত্র দেখার অনুমতি)
⚠️ আপনি শুধুমাত্র তথ্য দেখতে পারবেন, কোনো পরিবর্তন করতে পারবেন না।
```

## Error Messages

যখন Monitor Staff কোনো restricted action করতে চাইবে:

- **Collection করতে চাইলে:** "Monitor staff শুধুমাত্র দেখতে পারবে, কালেকশন করতে পারবে না!"
- **Customer add করতে চাইলে:** "Monitor staff শুধুমাত্র দেখতে পারবে, নতুন কাস্টমার যোগ করতে পারবে না!"
- **Loan দিতে চাইলে:** "Monitor staff শুধুমাত্র দেখতে পারবে, লোন দিতে পারবে না!"
- **Form print করতে চাইলে:** "Monitor staff শুধুমাত্র দেখতে পারবে, ফর্ম প্রিন্ট করতে পারবে না!"

## Security Features

1. **Route Level Protection:** সব routes এ monitor staff check করা হয়
2. **Template Level Protection:** Templates এ monitor staff এর জন্য buttons hide করা হয়
3. **Database Level Protection:** Monitor staff কোনো data modify করতে পারবে না
4. **Flash Messages:** সব restricted actions এ Bengali error message দেখাবে

## Use Cases

Monitor Staff কখন ব্যবহার করবেন:

1. **Auditing:** যখন কেউ শুধু audit করবে
2. **Supervision:** যখন supervisor শুধু monitor করবে
3. **Training:** নতুন staff training এর সময়
4. **Reporting:** যখন শুধু reports দেখতে হবে
5. **Management:** Management level এ শুধু overview দেখতে হবে

## Technical Implementation

### Database Model
```python
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(20))  # "admin" or "staff"
    is_office_staff = db.Column(db.Boolean, default=False)
    is_monitor = db.Column(db.Boolean, default=False)  # Monitor flag
```

### Route Protection Example
```python
@app.route('/collection', methods=['GET', 'POST'])
@login_required
def collection():
    if hasattr(current_user, 'is_monitor') and current_user.is_monitor:
        flash('Monitor staff শুধুমাত্র দেখতে পারবে, কালেকশন করতে পারবে না!', 'danger')
        return redirect(url_for('dashboard'))
    # ... rest of the code
```

### Template Protection Example
```html
{% if not current_user.is_monitor %}
<div class="col-md-4">
  <a href="{{ url_for('collection') }}" class="btn btn-success">
    <i class="fas fa-coins"></i> কালেকশন করুন
  </a>
</div>
{% endif %}
```

## Testing

Monitor Staff test করার জন্য:

1. Monitor staff হিসেবে login করুন
2. সব pages visit করুন এবং verify করুন যে:
   - সব data দেখা যাচ্ছে
   - কোনো modification button নেই
   - Restricted actions এ error message আসছে

## Troubleshooting

### Problem: Monitor staff collection করতে পারছে
**Solution:** Check করুন `is_monitor` flag properly set আছে কিনা

### Problem: Monitor staff কিছু pages দেখতে পারছে না
**Solution:** Route protection check করুন এবং ensure করুন monitor staff access আছে

### Problem: Error messages English এ আসছে
**Solution:** Flash messages Bengali তে convert করুন

## Future Enhancements

1. **Granular Permissions:** আরো detailed permissions add করা
2. **Activity Logging:** Monitor staff কি কি দেখছে তার log রাখা
3. **Time-based Access:** নির্দিষ্ট সময়ে access দেওয়া
4. **Report Generation:** Monitor staff এর জন্য special reports

## Support

কোনো সমস্যা হলে:
- GitHub Issues: https://github.com/roneox26/Al-insaf/issues
- Email: support@al-insaf.com

---

**Last Updated:** 2024
**Version:** 1.0
