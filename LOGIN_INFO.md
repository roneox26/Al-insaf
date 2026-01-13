# Login Information - NGO Management System

## 🔐 Login Credentials

### Admin Account
- **Email:** admin@example.com
- **Password:** admin123
- **Access:** Full system access

### Office Staff Account
- **Email:** office@example.com
- **Password:** office123
- **Access:** All customers, collections, add customers

### Field Staff Account
- **Email:** staff@example.com
- **Password:** staff123
- **Access:** Only own customers

---

## 📝 Important Notes

1. **Login page এখন খালি থাকবে** - কোনো default credentials দেখাবে না
2. **প্রথমবার login করার সময়** উপরের credentials ব্যবহার করুন
3. **Production এ deploy করার আগে** অবশ্যই password পরিবর্তন করুন

---

## 🔒 Security Recommendations

### Admin Panel থেকে Password পরিবর্তন করুন:

1. Admin হিসেবে login করুন
2. "Manage Staff" এ যান
3. User select করুন
4. "Edit" ক্লিক করুন
5. নতুন password দিন
6. Save করুন

### অথবা Database থেকে সরাসরি:

```python
from app import app, db, bcrypt, User

with app.app_context():
    admin = User.query.filter_by(email='admin@example.com').first()
    admin.password = bcrypt.generate_password_hash('your_new_password').decode('utf-8')
    db.session.commit()
    print("Password changed successfully!")
```

---

## ⚠️ Production Deployment

Deploy করার আগে:

1. ✅ সব default passwords পরিবর্তন করুন
2. ✅ `debug=False` set করুন (run.py তে already আছে)
3. ✅ Strong passwords ব্যবহার করুন
4. ✅ Database backup নিন

---

**এই file টি secure জায়গায় রাখুন এবং production এ deploy করার সময় delete করে দিন!**
