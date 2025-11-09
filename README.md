# Al-Insaf NGO Management System

🏦 একটি সম্পূর্ণ NGO ম্যানেজমেন্ট সিস্টেম যেখানে লোন, সেভিংস, কালেকশন ম্যানেজ করা যায়।

## ✨ Features

### 👥 User Management
- ✅ 3 ধরনের User: Admin, Office Staff, Field Staff
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

## 📝 Default Login Credentials

**⚠️ Change these passwords after first login!**

- **Admin:** admin@example.com / admin123
- **Office Staff:** office@example.com / office123
- **Field Staff:** staff@example.com / staff123

## 🔧 Utilities

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
