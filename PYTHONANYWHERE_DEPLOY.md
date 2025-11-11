# 🚀 PythonAnywhere Deployment Guide

## ✅ Step-by-Step Checklist

### 1️⃣ Account তৈরি করো (5 মিনিট)
- [ ] [PythonAnywhere.com](https://www.pythonanywhere.com) এ যাও
- [ ] "Create a Beginner account" ক্লিক করো (Free)
- [ ] Email verify করো
- [ ] Login করো

### 2️⃣ Code Upload করো (5 মিনিট)

#### GitHub থেকে (সহজ):
```bash
# Dashboard > "Consoles" > "Bash" ক্লিক করো
cd ~
git clone https://github.com/roneox26/Al-insaf.git
cd Al-insaf
ls  # ফাইল দেখো
```

#### Manual Upload (যদি GitHub না থাকে):
- "Files" tab এ যাও
- "Upload a file" ক্লিক করো
- সব ফাইল upload করো

### 3️⃣ Virtual Environment তৈরি করো (3 মিনিট)
```bash
# Bash Console এ:
mkvirtualenv --python=/usr/bin/python3.10 alinsaf
pip install -r requirements.txt
```

**⏳ Wait করো... Dependencies install হচ্ছে (2-3 মিনিট)**

### 4️⃣ Database তৈরি করো (1 মিনিট)
```bash
cd ~/Al-insaf
python create_db.py
```

**✅ Success message দেখবে!**

### 5️⃣ Web App তৈরি করো (5 মিনিট)

1. **"Web" tab এ যাও**
2. **"Add a new web app" ক্লিক করো**
3. **Domain name confirm করো** (yourusername.pythonanywhere.com)
4. **"Manual configuration" select করো**
5. **Python 3.10 select করো**
6. **"Next" ক্লিক করো**

### 6️⃣ WSGI File Configure করো (3 মিনিট)

1. **Web tab এ "WSGI configuration file" link ক্লিক করো**
2. **সব কিছু delete করো**
3. **এই code paste করো:**

```python
import sys
import os

# ⚠️ IMPORTANT: 'yourusername' replace করো তোমার PythonAnywhere username দিয়ে
project_home = '/home/yourusername/Al-insaf'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

from app import app as application
```

4. **Save করো (Ctrl+S বা Save button)**

### 7️⃣ Virtual Environment Path Set করো (1 মিনিট)

1. **Web tab এ scroll করো**
2. **"Virtualenv" section খুঁজো**
3. **Path দাও:**
```
/home/yourusername/.virtualenvs/alinsaf
```
4. **✅ Check mark দেখবে**

### 8️⃣ Static Files Setup করো (Optional - 2 মিনিট)

1. **Web tab এ "Static files" section এ যাও**
2. **"Enter URL" এ লিখো:** `/static/`
3. **"Enter path" এ লিখো:** `/home/yourusername/Al-insaf/static`
4. **✅ Save করো**

### 9️⃣ Reload করো! (1 মিনিট)

1. **Web tab এ scroll up করো**
2. **সবুজ "Reload yourusername.pythonanywhere.com" button ক্লিক করো**
3. **⏳ 10 সেকেন্ড wait করো**
4. **🎉 Site visit করো: `yourusername.pythonanywhere.com`**

---

## 🎯 Default Login Credentials

**⚠️ প্রথম login এর পর password change করো!**

- **Admin:** admin@example.com / admin123
- **Office Staff:** office@example.com / office123  
- **Field Staff:** staff@example.com / staff123

---

## 🔧 Common Issues & Solutions

### ❌ "ImportError: No module named flask"
**Solution:**
```bash
workon alinsaf
pip install -r requirements.txt
```

### ❌ "Application object must be callable"
**Solution:** WSGI file এ check করো:
- `from app import app as application` আছে কিনা
- Path সঠিক আছে কিনা

### ❌ "Database not found"
**Solution:**
```bash
cd ~/Al-insaf
python create_db.py
# Web tab এ Reload করো
```

### ❌ "500 Internal Server Error"
**Solution:**
1. Web tab > "Log files" > "Error log" দেখো
2. Bash console এ test করো:
```bash
cd ~/Al-insaf
workon alinsaf
python app.py
```

### ❌ Static files (CSS/JS) load হচ্ছে না
**Solution:**
- Web tab > Static files section check করো
- Path: `/home/yourusername/Al-insaf/static`
- URL: `/static/`

---

## 🔄 Code Update করার নিয়ম

### GitHub থেকে update:
```bash
cd ~/Al-insaf
git pull
# Web tab এ Reload button ক্লিক করো
```

### Manual update:
1. Files tab এ যাও
2. File edit করো
3. Save করো
4. Web tab এ Reload করো

---

## 📊 Database Backup

### Backup নাও:
```bash
cd ~/Al-insaf/instance
cp ngo.db ngo_backup_$(date +%Y%m%d).db
```

### Restore করো:
```bash
cd ~/Al-insaf/instance
cp ngo_backup_20240101.db ngo.db
# Web tab এ Reload করো
```

---

## 🎓 Pro Tips

1. **Error log regularly check করো:** Web tab > Error log
2. **Database backup নিয়মিত নাও** (সপ্তাহে একবার)
3. **Password change করো** first login এর পর
4. **Free account limit:** 
   - 1 web app
   - 512 MB storage
   - Daily CPU limit
5. **Custom domain:** Paid account এ upgrade করলে পাবে

---

## 📞 Help & Support

- **PythonAnywhere Help:** https://help.pythonanywhere.com
- **Forum:** https://www.pythonanywhere.com/forums/
- **GitHub Issues:** https://github.com/roneox26/Al-insaf/issues

---

## ✅ Deployment Checklist Summary

- [ ] Account তৈরি করেছো
- [ ] Code upload করেছো
- [ ] Virtual environment তৈরি করেছো
- [ ] Dependencies install করেছো
- [ ] Database তৈরি করেছো
- [ ] Web app তৈরি করেছো
- [ ] WSGI file configure করেছো
- [ ] Virtual environment path set করেছো
- [ ] Static files setup করেছো
- [ ] Reload করেছো
- [ ] Site test করেছো
- [ ] Login করতে পেরেছো
- [ ] Password change করেছো

**🎉 Congratulations! Your NGO Management System is now LIVE!**
