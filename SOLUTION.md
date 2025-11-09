# SQLAlchemy OperationalError সমাধান

## সমস্যা
Database এ কিছু column বা table missing থাকলে এই error আসে।

## সমাধান

### Option 1: Database Fix (যদি data রাখতে চান)
```bash
python fix_db.py
```

### Option 2: Fresh Start (সব data মুছে নতুন করে শুরু)

1. **সব application বন্ধ করুন** যেগুলো database ব্যবহার করছে

2. **Database file মুছে দিন:**
   ```bash
   del instance\loan.db
   ```

3. **Application run করুন:**
   ```bash
   python run.py
   ```
   অথবা
   ```bash
   python app.py
   ```

Database automatically তৈরি হবে সব table সহ।

## যদি এখনও error আসে

### Check 1: Database file locked আছে কিনা
- সব browser tab বন্ধ করুন
- Command prompt/terminal বন্ধ করে নতুন করে খুলুন
- Task Manager এ python.exe process kill করুন

### Check 2: Permissions
```bash
# Database folder এ write permission আছে কিনা check করুন
dir instance
```

### Check 3: Fresh install
```bash
# Dependencies reinstall
pip uninstall flask flask-sqlalchemy flask-login flask-bcrypt -y
pip install -r requirements.txt

# Database recreate
del instance\loan.db
python app.py
```

## Login Credentials
- **Admin:** admin@example.com / admin123
- **Staff:** staff@example.com / staff123

## Support
যদি এখনও সমস্যা হয়, error message টি পাঠান।
