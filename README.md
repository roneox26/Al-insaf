# Al-Insaf ক্ষুদ্র ব্যবসায়ী সমবায় সমিতি লিঃ - NGO Management System

🏦 একটি সম্পূর্ণ NGO ম্যানেজমেন্ট সিস্টেম যেখানে লোন, সেভিংস, কালেকশন ম্যানেজ করা যায়।

## ✨ Features

### 👥 User Management
- ✅ 4 ধরনের User: Admin, Office Staff, Field Staff, Monitor Staff
- ✅ Role-based Access Control
- ✅ Staff Management

### 💰 Financial Management
- ✅ Customer Management
- ✅ Loan Distribution & Tracking
- ✅ Savings Management
- ✅ Daily/Monthly Collections
- ✅ Cash Balance Management
- ✅ Investor Management
- ✅ Expense Tracking

### 📊 Reports
- ✅ Daily Report
- ✅ Monthly Report
- ✅ Withdrawal Report
- ✅ Staff Collection Report
- ✅ Profit/Loss Report

### 🔐 Security
- ✅ Secure Authentication
- ✅ Password Hashing
- ✅ Role-based Permissions

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/roneox26/Al-insaf.git
cd Al-insaf
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Create database**
```bash
python create_db.py
```

4. **Run the application**
```bash
python run.py
```

5. **Open in browser**
```
http://localhost:5000
```

## 👤 User Roles

### Admin (প্রশাসক)
- Full system access
- Manage staff, loans, investors
- View all reports

### Office Staff (অফিস স্টাফ)
- View all customers
- Collect from all customers
- Add new customers
- View daily collections

### Field Staff (ফিল্ড স্টাফ)
- View only assigned customers
- Collect from own customers
- Add customers under own supervision

### Monitor Staff (মনিটর স্টাফ)
- View all customers (read-only)
- View loan customers
- View daily reports
- Cannot collect money
- Only monitoring access

## 📝 Default Login Credentials

**⚠️ Change these passwords after first login!**

- **Admin:** admin@example.com / admin123
- **Office Staff:** office@example.com / office123
- **Field Staff:** staff@example.com / staff123

## 🛠️ Utilities

### Add Office Staff
```bash
python add_office_staff.py
```

### Change Password
```bash
python change_password.py
```

### Reset Database
```bash
python create_db.py
```

### Fix Database (Deploy করার পরে যদি error আসে)
```bash
python fix_database_universal.py
```
**অথবা quick fix:**
```bash
python quick_fix.py
```

### Individual Loan Sheet Fix (FIFO Implementation)
```bash
python migrate_add_loan_id.py
```
**অথবা Windows এ:**
```bash
run_migration.bat
```

**Note:** Deploy করার পরে যদি "loan_id" বা "column does not exist" error দেখো, তাহলে এই command run করো।

**বিস্তারিত নির্দেশনা:** [LOAN_SHEET_FIX.md](LOAN_SHEET_FIX.md) দেখুন

**Render.com এ Fix করতে:**
1. Dashboard > Shell tab এ যাও
2. Run: `python migrate_add_loan_id.py`
3. Application restart করো

**বিস্তারিত নির্দেশনা:** [LOAN_SHEET_FIX.md](LOAN_SHEET_FIX.md) দেখুন

## 🌐 Deploy করার নিয়ম

### Render.com এ Deploy (Free)

1. GitHub এ code push করো
2. [Render.com](https://render.com) এ যাও
3. "New +" > "Web Service" ক্লিক করো
4. GitHub repository connect করো
5. Build Command: `pip install -r requirements.txt`
6. Start Command: `python run.py`
7. Deploy করো!

### Railway.app এ Deploy

1. [Railway.app](https://railway.app) এ যাও
2. "New Project" > "Deploy from GitHub"
3. Repository select করো
4. Automatic deploy হবে!

### DigitalOcean App Platform এ Deploy

#### ১. Account তৈরি করো
- [DigitalOcean.com](https://www.digitalocean.com) এ যাও
- Sign up করো (প্রথম $200 credit পাবে)

#### ২. App তৈরি করো
- Dashboard > "Create" > "Apps"
- GitHub repository connect করো
- Repository select করো: `Al-insaf`
- Branch select করো: `main` বা `master`

#### ৩. App Configuration
- **Name:** al-insaf-ngo (বা যেকোনো নাম)
- **Region:** New York (বা কাছের region)
- **Plan:** Basic ($5/month) বা Dev ($0 - শুধু static sites)

#### ৪. Environment Variables (Optional)
```
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
```

#### ৫. Build & Deploy Settings
- **Build Command:** `pip install -r requirements.txt && python create_db.py`
- **Run Command:** `python run.py`
- **HTTP Port:** 5000

#### ৬. Deploy করো
- "Next" > "Create Resources"
- Deploy শুরু হবে (5-10 মিনিট লাগবে)
- URL পাবে: `https://al-insaf-ngo-xxxxx.ondigitalocean.app`

#### 🔧 Troubleshooting

**Build failed হলে:**
- Runtime logs check করো
- Python version check করো (3.10 recommended)

**Database reset করতে:**
- Console tab > "Run command"
- Command: `python create_db.py`

**Database migration করতে (deploy এর পরে প্রথমবার):**
- Console tab > "Run command"
- Command: `python migrate_add_loan_id.py`
- এটা `loan_collections` table এ `loan_id` column add করবে
- Individual Loan Sheets সঠিকভাবে কাজ করবে

**Code update করতে:**
- GitHub এ push করলে automatic deploy হবে
- অথবা manually "Deploy" button ক্লিক করো

### PythonAnywhere এ Deploy (Free - সবচেয়ে সহজ)

#### ১. Account তৈরি করো
- [PythonAnywhere.com](https://www.pythonanywhere.com) এ যাও
- "Pricing & signup" > "Create a Beginner account" (Free)
- Email verify করো

#### ২. Code Upload করো

**Option A: GitHub থেকে (Recommended)**
```bash
# PythonAnywhere Bash Console এ:
cd ~
git clone https://github.com/roneox26/Al-insaf.git
cd Al-insaf
```

**Option B: Manual Upload**
- Files tab > Upload files
- সব ফাইল upload করো

#### ৩. Virtual Environment তৈরি করো
```bash
# Bash Console এ:
mkvirtualenv --python=/usr/bin/python3.10 myenv
pip install -r requirements.txt
```

#### ৪. Database তৈরি করো
```bash
python create_db.py
```

#### ৫. Web App Setup করো
- "Web" tab এ যাও
- "Add a new web app" ক্লিক করো
- "Manual configuration" > Python 3.10 select করো
- "Next" ক্লিক করো

#### ৬. WSGI Configuration
- Web tab এ "WSGI configuration file" link এ ক্লিক করো
- সব কিছু delete করে এটা paste করো:

```python
import sys
import os

# আপনার username দিয়ে replace করো
project_home = '/home/yourusername/Al-insaf'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

from app import app as application
```

#### ৭. Virtual Environment Set করো
- Web tab এ "Virtualenv" section এ যাও
- Path দাও: `/home/yourusername/.virtualenvs/myenv`

#### ৮. Static Files Setup (Optional)
- Web tab এ "Static files" section এ:
- URL: `/static/`
- Directory: `/home/yourusername/Al-insaf/static`

#### ৯. Reload করো
- Web tab এ সবুজ "Reload" button ক্লিক করো
- আপনার site: `yourusername.pythonanywhere.com`

#### 🔧 Troubleshooting

**Error দেখলে:**
- Web tab > "Log files" > "Error log" দেখো
- Bash console এ: `python app.py` run করে error check করো

**Database issue হলে:**
```bash
cd ~/Al-insaf
python create_db.py
```

**Database migration করতে (deploy এর পরে প্রথমবার):**
```bash
cd ~/Al-insaf
python migrate_add_loan_id.py
# Web tab এ Reload button ক্লিক করো
```

**Individual Loan Sheet সমস্যা হলে:**
- Migration script run করো (uporer command)
- Browser cache clear করো
- Application reload করো

**Code update করতে:**
```bash
cd ~/Al-insaf
git pull
# Web tab এ Reload button ক্লিক করো
```

## 📁 Project Structure

```
Al-insaf/
├── app.py              # Main application
├── run.py              # Application runner
├── config.py           # Configuration
├── models/             # Database models
├── templates/          # HTML templates
├── static/             # CSS, JS, images
├── instance/           # Database (auto-created)
└── requirements.txt    # Dependencies
```

## 🛠️ Technology Stack

- **Backend:** Flask (Python)
- **Database:** SQLite
- **Authentication:** Flask-Login
- **Password Hashing:** Flask-Bcrypt
- **ORM:** SQLAlchemy
- **Frontend:** Bootstrap 5

## 📄 License

MIT License - Free to use and modify

## 👨‍💻 Developer

Developed by **Roneo**
- GitHub: [@roneox26](https://github.com/roneox26)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

**⭐ If you find this project helpful, please give it a star!**
