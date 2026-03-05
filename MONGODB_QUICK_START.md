# MongoDB Migration - Quick Guide

## ⚡ দ্রুত Setup (5 মিনিট)

### 1️⃣ MongoDB Install করুন

**Windows:**
- Download: https://www.mongodb.com/try/download/community
- Install করুন (Next, Next, Finish)
- MongoDB Compass open করুন

**Linux:**
```bash
sudo apt-get install mongodb
sudo systemctl start mongodb
```

### 2️⃣ Dependencies Install করুন

```bash
pip install flask-mongoengine mongoengine pymongo
```

### 3️⃣ Migration Run করুন

```bash
python migrate_to_mongodb.py
```

**অথবা Windows এ:**
```bash
SETUP_MONGODB.bat
```

### 4️⃣ সম্পন্ন! ✅

আপনার সব data এখন MongoDB তে আছে।

---

## 🌐 Cloud Setup (MongoDB Atlas - Free)

### 1️⃣ Account তৈরি করুন
- যান: https://www.mongodb.com/cloud/atlas
- Sign up করুন (Free)

### 2️⃣ Cluster তৈরি করুন
- "Create Cluster" > Free tier (M0)
- Region: Singapore/Mumbai
- Create করুন

### 3️⃣ Database User তৈরি করুন
- Database Access > Add User
- Username: `ngo_admin`
- Password: strong password দিন
- Save করুন

### 4️⃣ Network Access
- Network Access > Add IP
- "Allow from Anywhere" (0.0.0.0/0)
- Confirm করুন

### 5️⃣ Connection String Copy করুন
- Clusters > Connect > Connect your application
- Copy করুন:
```
mongodb+srv://ngo_admin:PASSWORD@cluster.xxxxx.mongodb.net/ngo_db
```

### 6️⃣ Environment Variable Set করুন

**.env file তৈরি করুন:**
```
MONGODB_URI=mongodb+srv://ngo_admin:YOUR_PASSWORD@cluster.xxxxx.mongodb.net/ngo_db
```

### 7️⃣ Migration Run করুন
```bash
python migrate_to_mongodb.py
```

---

## 📊 Data Verify করুন

### MongoDB Compass দিয়ে:
1. Open MongoDB Compass
2. Connect: `mongodb://localhost:27017`
3. Database: `ngo_db`
4. Collections check করুন

### Command Line দিয়ে:
```bash
mongosh
use ngo_db
db.users.countDocuments()
db.customers.countDocuments()
db.loans.countDocuments()
```

---

## 🚀 Deploy করুন

### Render.com:
Environment Variables এ add করুন:
```
MONGODB_URI=mongodb+srv://...
```

### PythonAnywhere:
```bash
pip install --user flask-mongoengine pymongo
```

### Railway.app:
Variables tab এ:
```
MONGODB_URI=mongodb+srv://...
```

---

## ❓ সমস্যা হলে

### MongoDB start হচ্ছে না?
```bash
# Windows
mongod

# Linux
sudo systemctl start mongodb
```

### Connection error?
- MongoDB running আছে কিনা check করুন
- Connection string সঠিক আছে কিনা verify করুন
- Password এ special characters থাকলে URL encode করুন

### Migration error?
```bash
# Backup নিন
cp instance/loan.db instance/loan_backup.db

# আবার try করুন
python migrate_to_mongodb.py
```

---

## 📖 বিস্তারিত Guide

পূর্ণ documentation: [MONGODB_SETUP.md](MONGODB_SETUP.md)

---

**Made with ❤️ by Roneo**
