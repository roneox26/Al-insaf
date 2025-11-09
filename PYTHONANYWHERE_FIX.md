# 🔧 PythonAnywhere Error Fix Guide

## ❌ "Unhandled Exception" Error

### Step 1: Check Error Log

1. Go to **Web** tab on PythonAnywhere
2. Scroll down to **Log files**
3. Click on **Error log** link
4. Look for the actual error message

---

## 🔍 Common Errors & Solutions

### Error 1: ImportError / ModuleNotFoundError

**Error message:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
cd ~/Al-insaf
pip3 install --user -r requirements.txt
```

Then click **Reload** in Web tab.

---

### Error 2: Wrong Path in WSGI

**Error message:** `ImportError: No module named 'app'`

**Solution:** Update WSGI file with correct path

1. Go to **Web** tab
2. Click on **WSGI configuration file**
3. Change line 6 to:
```python
project_home = '/home/rone12/Al-insaf'
```
(Use YOUR username instead of `rone12`)

4. Save and **Reload**

---

### Error 3: Database Error

**Error message:** `OperationalError: no such table`

**Solution:** Create database
```bash
cd ~/Al-insaf
python3 create_db.py
```

Then **Reload** web app.

---

### Error 4: Permission Error

**Error message:** `PermissionError: [Errno 13]`

**Solution:** Fix permissions
```bash
cd ~/Al-insaf
chmod -R 755 .
mkdir -p instance
chmod 777 instance
```

Then **Reload**.

---

## ✅ Complete Fix (Try This First)

Run these commands in **Bash Console**:

```bash
# Go to project directory
cd ~/Al-insaf

# Reinstall all dependencies
pip3 install --user -r requirements.txt --force-reinstall

# Create instance directory
mkdir -p instance
chmod 777 instance

# Create database
python3 create_db.py

# Check if everything is OK
python3 -c "from app import app; print('Import successful!')"
```

Then go to **Web** tab and click **Reload**.

---

## 📋 Correct WSGI Configuration

Your WSGI file should look like this:

```python
import sys
import os

# Replace 'rone12' with YOUR username
project_home = '/home/rone12/Al-insaf'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

os.environ['FLASK_APP'] = 'app.py'

try:
    from app import app as application
    from app import db, bcrypt, User, CashBalance
    
    with application.app_context():
        try:
            db.create_all()
            
            if not User.query.filter_by(email='admin@example.com').first():
                hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
                admin = User(name='Admin', email='admin@example.com', password=hashed_pw, role='admin')
                db.session.add(admin)
            
            if not User.query.filter_by(email='office@example.com').first():
                hashed_pw = bcrypt.generate_password_hash('office123').decode('utf-8')
                office = User(name='Office Staff', email='office@example.com', password=hashed_pw, role='staff', is_office_staff=True)
                db.session.add(office)
            
            if not User.query.filter_by(email='staff@example.com').first():
                hashed_pw = bcrypt.generate_password_hash('staff123').decode('utf-8')
                staff = User(name='Field Staff', email='staff@example.com', password=hashed_pw, role='staff', is_office_staff=False)
                db.session.add(staff)
            
            db.session.commit()
            
            if not CashBalance.query.first():
                initial_balance = CashBalance(balance=0)
                db.session.add(initial_balance)
                db.session.commit()
        except Exception as e:
            print(f"Database error: {e}")
except Exception as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()
```

---

## 🎯 Step-by-Step Checklist

- [ ] Cloned/uploaded code to `/home/rone12/Al-insaf`
- [ ] Installed dependencies: `pip3 install --user -r requirements.txt`
- [ ] Created instance folder: `mkdir -p instance && chmod 777 instance`
- [ ] Updated WSGI file with correct username
- [ ] Set Source code path: `/home/rone12/Al-insaf`
- [ ] Set Working directory: `/home/rone12/Al-insaf`
- [ ] Clicked Reload button
- [ ] Checked error log for any remaining errors

---

## 🆘 Still Not Working?

### Check These:

1. **Python Version:** Use Python 3.10 or 3.9
2. **File Permissions:** All files should be readable
3. **Dependencies:** All packages in requirements.txt installed
4. **Paths:** All paths use YOUR username, not 'rone12'

### Get Help:

1. Copy error from error log
2. Post on PythonAnywhere forums: https://www.pythonanywhere.com/forums/
3. Or email: support@pythonanywhere.com

---

## 💡 Pro Tips

1. **Always check error log first** - It tells you exactly what's wrong
2. **Reload after every change** - Changes don't apply until you reload
3. **Use Bash console** - Easier to run commands and see output
4. **Test imports** - Run `python3 -c "from app import app"` to test

---

**Need more help? Check the error log and share the error message!**
