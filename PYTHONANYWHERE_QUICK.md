# ⚡ PythonAnywhere Quick Reference

## 🚀 Quick Deploy (5 Minutes)

### 1. Create Account
→ https://www.pythonanywhere.com → Sign Up (FREE)

### 2. Clone Code
```bash
git clone https://github.com/roneox26/Al-insaf.git
cd Al-insaf
pip3 install --user -r requirements.txt
```

### 3. Create Web App
Web tab → Add new web app → Manual → Python 3.10

### 4. Configure WSGI
Click WSGI file → Replace content with:
```python
import sys
project_home = '/home/YOURUSERNAME/Al-insaf'
sys.path = [project_home] + sys.path
from app import app as application
```

### 5. Set Paths
- Source code: `/home/YOURUSERNAME/Al-insaf`
- Working directory: `/home/YOURUSERNAME/Al-insaf`

### 6. Reload
Click green **Reload** button

### 7. Access
→ https://YOURUSERNAME.pythonanywhere.com

---

## 🔄 Update Code

```bash
cd ~/Al-insaf
git pull origin main
```
Then click **Reload** in Web tab

---

## 🔐 Login

- Admin: admin@example.com / admin123
- Office: office@example.com / office123
- Staff: staff@example.com / staff123

---

## 🐛 Fix Errors

```bash
cd ~/Al-insaf
pip3 install --user -r requirements.txt --force-reinstall
python3 create_db.py
```
Then **Reload** web app

---

## 📝 Important

- Replace `YOURUSERNAME` with your PythonAnywhere username
- Check Error log if something breaks
- Reload after every change
- Change passwords after first login

---

**Full Guide:** See PYTHONANYWHERE_DEPLOY.md
