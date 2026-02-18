# Deployment Guide - সমস্যা সমাধান

## Deploy করার পরে যদি "loan_id" error আসে

### সমস্যা:
```
Error loading loan sheet: Entity namespace for "loan_collections" has no property "loan_id"
```

### কারণ:
Database এ `loan_collections` table এ `loan_id` column নেই।

### সমাধান:

#### Option 1: fix_database.py script (সবচেয়ে সহজ)
```bash
python fix_database.py
```

#### Option 2: migrate_loan_id.py script
```bash
python migrate_loan_id.py
```

#### Option 3: Manual SQL (যদি উপরের দুটো কাজ না করে)
```bash
# SQLite database এ যাও
sqlite3 instance/ngo.db

# এই command run করো
ALTER TABLE loan_collections ADD COLUMN loan_id INTEGER;

# Exit করো
.exit
```

## Deploy করার সঠিক পদ্ধতি

### 1. Local এ Test করো
```bash
# Database তৈরি করো
python create_db.py

# Application run করো
python run.py

# Browser এ test করো: http://localhost:5000
```

### 2. GitHub এ Push করো
```bash
git add .
git commit -m "Updated code"
git push origin main
```

### 3. Deploy Platform এ Deploy করো
- Render.com / Railway.app / PythonAnywhere
- Automatic deploy হবে

### 4. Deploy হওয়ার পরে Database Fix করো
```bash
# Platform এর console/terminal এ যাও
python fix_database.py
```

### 5. Application Restart করো
- Platform এর dashboard থেকে restart করো
- অথবা code এ একটা ছোট change করে push করো

## Common Errors এবং সমাধান

### Error 1: "No module named 'flask'"
**সমাধান:**
```bash
pip install -r requirements.txt
```

### Error 2: "Database not found"
**সমাধান:**
```bash
python create_db.py
```

### Error 3: "loan_id property not found"
**সমাধান:**
```bash
python fix_database.py
```

### Error 4: "Port already in use"
**সমাধান:**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5000 | xargs kill -9
```

## Deployment Checklist

- [ ] Local এ test করেছো
- [ ] requirements.txt updated আছে
- [ ] GitHub এ push করেছো
- [ ] Deploy platform এ deploy করেছো
- [ ] Database create করেছো (`python create_db.py`)
- [ ] Database fix করেছো (`python fix_database.py`)
- [ ] Application restart করেছো
- [ ] Browser এ test করেছো
- [ ] Login করতে পারছো
- [ ] Customer loan sheet দেখতে পারছো

## Support

যদি কোনো সমস্যা হয়, GitHub এ issue create করো:
https://github.com/roneox26/Al-insaf/issues
