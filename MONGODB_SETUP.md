# MongoDB Setup Guide - Al-Insaf NGO System

## 🎯 MongoDB কেন ব্যবহার করবেন?

### সুবিধা:
- ✅ **Scalability**: বড় data handle করতে পারে
- ✅ **Performance**: Fast read/write operations
- ✅ **Flexibility**: Schema-less design
- ✅ **Cloud Ready**: MongoDB Atlas (Free tier available)
- ✅ **No Migration Issues**: Deploy করার সময় database migration এর ঝামেলা নেই

## 📋 Prerequisites

### 1. MongoDB Install করুন

**Windows:**
1. [MongoDB Download](https://www.mongodb.com/try/download/community) থেকে download করুন
2. Install করুন (default settings রাখুন)
3. MongoDB Compass install করুন (GUI tool)

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt-get install mongodb

# Mac
brew install mongodb-community
```

### 2. MongoDB Start করুন

**Windows:**
- MongoDB Compass open করুন
- অথবা Command Prompt এ: `mongod`

**Linux/Mac:**
```bash
sudo systemctl start mongod
sudo systemctl enable mongod
```

## 🚀 Setup Steps

### Step 1: Dependencies Install করুন

```bash
pip install -r requirements_mongodb.txt
```

### Step 2: MongoDB Connection Test করুন

```bash
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017/'); print('✅ MongoDB Connected!')"
```

### Step 3: Data Migration করুন (SQLite থেকে MongoDB তে)

```bash
python migrate_to_mongodb.py
```

এটি আপনার সব data SQLite থেকে MongoDB তে transfer করবে:
- ✅ Users
- ✅ Customers
- ✅ Loans
- ✅ Savings
- ✅ Collections
- ✅ Investors
- ✅ Expenses
- ✅ Withdrawals

### Step 4: Application Update করুন

`app.py` তে MongoDB configuration add করুন:

```python
# config.py এর পরিবর্তে config_mongodb.py import করুন
from config_mongodb import *

# models import করুন
from models_mongodb.user_model import db, User
from models_mongodb.customer_model import Customer
from models_mongodb.loan_model import Loan, LoanCollection
from models_mongodb.saving_model import Saving, SavingCollection
from models_mongodb.other_models import CashBalance, Investor, Investment, Expense, Withdrawal

# Initialize MongoDB
db.init_app(app)
```

### Step 5: Application Run করুন

```bash
python run.py
```

## 🌐 MongoDB Atlas (Cloud) Setup

### Free Tier (512MB Storage)

1. **Account তৈরি করুন**
   - [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) এ যান
   - Sign up করুন (Free)

2. **Cluster তৈরি করুন**
   - "Create a Cluster" ক্লিক করুন
   - Free tier (M0) select করুন
   - Region: Singapore/Mumbai (closest)
   - Cluster Name: `ngo-cluster`

3. **Database User তৈরি করুন**
   - Database Access > Add New Database User
   - Username: `ngo_admin`
   - Password: একটি strong password দিন
   - Role: Read and write to any database

4. **Network Access Setup করুন**
   - Network Access > Add IP Address
   - "Allow Access from Anywhere" (0.0.0.0/0)
   - অথবা specific IP add করুন

5. **Connection String পান**
   - Clusters > Connect > Connect your application
   - Copy করুন: `mongodb+srv://ngo_admin:<password>@ngo-cluster.xxxxx.mongodb.net/ngo_db`

6. **Environment Variable Set করুন**

**Local Development (.env file):**
```
MONGODB_URI=mongodb+srv://ngo_admin:YOUR_PASSWORD@ngo-cluster.xxxxx.mongodb.net/ngo_db
```

**Production (Render/Railway/PythonAnywhere):**
- Environment Variables section এ যান
- Add: `MONGODB_URI` = `mongodb+srv://...`

## 🔧 Migration Script Details

### migrate_to_mongodb.py কি করে?

1. **SQLite Database থেকে data read করে**
2. **MongoDB তে data insert করে**
3. **Relationships maintain করে** (User → Customer → Loan)
4. **Progress show করে** (কোন data migrate হচ্ছে)

### Migration Run করার আগে:

```bash
# Backup নিন
cp instance/loan.db instance/loan_backup.db

# MongoDB running আছে কিনা check করুন
mongosh --eval "db.version()"
```

### Migration Run করুন:

```bash
python migrate_to_mongodb.py
```

### Output দেখবেন:

```
============================================================
SQLite থেকে MongoDB তে Data Migration শুরু হচ্ছে...
============================================================
Migrating Users...
✓ Migrated user: Admin User
✓ Migrated user: Office Staff
✓ Migrated user: Field Staff

Migrating Customers...
✓ Migrated customer: রহিম মিয়া
✓ Migrated customer: করিম মিয়া
...

✅ Migration সফলভাবে সম্পন্ন হয়েছে!
```

## 📊 MongoDB Compass দিয়ে Data দেখুন

1. MongoDB Compass open করুন
2. Connect: `mongodb://localhost:27017`
3. Database: `ngo_db`
4. Collections দেখুন:
   - users
   - customers
   - loans
   - loan_collections
   - saving_collections
   - investors
   - expenses

## 🔍 Troubleshooting

### Error: "Connection refused"
```bash
# MongoDB start করুন
sudo systemctl start mongod  # Linux
mongod  # Windows
```

### Error: "Authentication failed"
```bash
# MongoDB Atlas এ password check করুন
# Special characters encode করুন (%, @, : etc.)
```

### Error: "Database not found"
```bash
# Migration script আবার run করুন
python migrate_to_mongodb.py
```

### Data verify করুন:
```bash
mongosh
use ngo_db
db.users.countDocuments()
db.customers.countDocuments()
db.loans.countDocuments()
```

## 🚀 Deploy করার সময়

### Render.com:
1. Environment Variables এ add করুন:
   ```
   MONGODB_URI=mongodb+srv://...
   ```
2. Build Command:
   ```
   pip install -r requirements_mongodb.txt
   ```

### PythonAnywhere:
1. Bash console এ:
   ```bash
   pip install --user flask-mongoengine pymongo
   ```
2. Web app configuration এ environment variable add করুন

### Railway.app:
1. Variables tab এ:
   ```
   MONGODB_URI=mongodb+srv://...
   ```
2. Automatic deploy হবে

## 📝 Important Notes

1. **Backup**: Migration করার আগে SQLite database এর backup নিন
2. **Testing**: Local এ test করে তারপর production এ deploy করুন
3. **Connection String**: Password এ special characters থাকলে URL encode করুন
4. **Free Tier Limits**: MongoDB Atlas free tier এ 512MB storage limit আছে

## 🎉 Migration সফল হলে

- ✅ SQLite dependency remove করতে পারবেন
- ✅ Better performance পাবেন
- ✅ Cloud database ব্যবহার করতে পারবেন
- ✅ Scalability improve হবে

## 📞 Support

কোন সমস্যা হলে GitHub issue create করুন।

---

**Made with ❤️ by Roneo**
