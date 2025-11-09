# 🚀 PythonAnywhere Deployment Guide

## Step-by-Step Instructions

### 1️⃣ Create PythonAnywhere Account

1. Go to: https://www.pythonanywhere.com
2. Sign up for a **FREE** account
3. Verify your email

---

### 2️⃣ Upload Your Code

#### Option A: Using Git (Recommended)

1. Open **Bash Console** from PythonAnywhere dashboard
2. Clone your repository:
```bash
git clone https://github.com/roneox26/Al-insaf.git
cd Al-insaf
```

#### Option B: Upload Files

1. Go to **Files** tab
2. Create folder: `Al-insaf`
3. Upload all files manually

---

### 3️⃣ Install Dependencies

In the **Bash Console**:

```bash
cd Al-insaf
pip3 install --user -r requirements.txt
```

Wait for installation to complete (2-3 minutes).

---

### 4️⃣ Create Web App

1. Go to **Web** tab
2. Click **Add a new web app**
3. Choose **Manual configuration**
4. Select **Python 3.10** (or latest)
5. Click **Next**

---

### 5️⃣ Configure WSGI File

1. In **Web** tab, find **Code** section
2. Click on **WSGI configuration file** link
3. **Delete all content** in the file
4. **Copy and paste** this code:

```python
import sys
import os

# IMPORTANT: Replace 'yourusername' with your PythonAnywhere username
project_home = '/home/yourusername/Al-insaf'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

os.environ['FLASK_APP'] = 'app.py'

from app import app as application

# Initialize database
from app import db, bcrypt, User, CashBalance

with application.app_context():
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
```

5. **Save** the file (Ctrl+S or click Save button)

---

### 6️⃣ Set Source Code Directory

1. In **Web** tab, find **Code** section
2. Set **Source code:** `/home/yourusername/Al-insaf`
3. Set **Working directory:** `/home/yourusername/Al-insaf`

(Replace `yourusername` with your actual PythonAnywhere username)

---

### 7️⃣ Configure Virtual Environment (Optional but Recommended)

1. In **Web** tab, find **Virtualenv** section
2. Click **Enter path to a virtualenv**
3. Enter: `/home/yourusername/.virtualenvs/alinsaf`
4. In Bash Console:
```bash
mkvirtualenv alinsaf --python=python3.10
pip install -r Al-insaf/requirements.txt
```

---

### 8️⃣ Reload Web App

1. Scroll to top of **Web** tab
2. Click big green **Reload** button
3. Wait for reload to complete

---

### 9️⃣ Access Your Application

Your app will be available at:
```
https://yourusername.pythonanywhere.com
```

(Replace `yourusername` with your PythonAnywhere username)

---

## 🔐 Default Login Credentials

- **Admin:** admin@example.com / admin123
- **Office Staff:** office@example.com / office123
- **Field Staff:** staff@example.com / staff123

**⚠️ Change these passwords immediately after first login!**

---

## 🔄 Update Your Application

When you make changes to your code:

### Method 1: Using Git

```bash
cd ~/Al-insaf
git pull origin main
```

Then click **Reload** button in Web tab.

### Method 2: Manual Upload

1. Upload changed files via **Files** tab
2. Click **Reload** button in Web tab

---

## 🐛 Troubleshooting

### Error: "Something went wrong"

1. Check **Error log** in Web tab
2. Common issues:
   - Wrong path in WSGI file
   - Missing dependencies
   - Python version mismatch

### Fix: Reinstall Dependencies

```bash
cd ~/Al-insaf
pip3 install --user -r requirements.txt --force-reinstall
```

### Fix: Reset Database

```bash
cd ~/Al-insaf
python3 create_db.py
```

Then **Reload** web app.

### View Logs

In **Web** tab:
- **Error log** - Shows errors
- **Server log** - Shows requests
- **Access log** - Shows visitors

---

## 📊 Free Account Limitations

- ✅ 512 MB disk space
- ✅ 1 web app
- ✅ Custom domain (paid)
- ✅ Always-on tasks (paid)
- ⚠️ App sleeps after inactivity (free tier)

---

## 💡 Tips

1. **Keep app active:** Visit your site regularly
2. **Backup database:** Download `instance/loan.db` regularly
3. **Monitor logs:** Check error logs daily
4. **Update regularly:** Pull latest code from GitHub

---

## 🆙 Upgrade to Paid Plan

For production use, consider upgrading:
- No sleep time
- More disk space
- Custom domains
- Always-on tasks

Starting at $5/month: https://www.pythonanywhere.com/pricing/

---

## 📞 Support

- **PythonAnywhere Help:** https://help.pythonanywhere.com
- **Forums:** https://www.pythonanywhere.com/forums/
- **GitHub Issues:** https://github.com/roneox26/Al-insaf/issues

---

## ✅ Checklist

- [ ] Created PythonAnywhere account
- [ ] Uploaded/cloned code
- [ ] Installed dependencies
- [ ] Created web app
- [ ] Configured WSGI file
- [ ] Set source code directory
- [ ] Reloaded web app
- [ ] Tested login
- [ ] Changed default passwords
- [ ] Bookmarked your app URL

---

**🎉 Congratulations! Your NGO Management System is now live on PythonAnywhere!**

**Your URL:** https://yourusername.pythonanywhere.com

Share this URL with your team and start managing your NGO operations!

---

**Made with ❤️ by Roneo**
