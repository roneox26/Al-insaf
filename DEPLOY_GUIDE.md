# 🚀 Render Deployment - সহজ গাইড

## 🎯 দুইটি Option:

### **Option 1: PostgreSQL (Recommended - Free & Easy)**
### **Option 2: MySQL (External Service দরকার)**

---

## ✅ Option 1: PostgreSQL দিয়ে Deploy (সবচেয়ে সহজ)

### ধাপ ১: GitHub এ Push
```bash
cd e:\ngo
git add .
git commit -m "Deploy to Render"
git push origin main
```

### ধাপ ২: Render.com এ যান
1. https://render.com এ যান
2. GitHub দিয়ে Sign up করুন

### ধাপ ৩: PostgreSQL Database তৈরি
1. "New +" > "PostgreSQL" ক্লিক করুন
2. Name: `ngo-database`
3. Database: `ngo_db`
4. Region: Singapore
5. "Create Database" ক্লিক করুন
6. **Internal Database URL** copy করুন

### ধাপ ৪: Web Service তৈরি
1. "New +" > "Web Service"
2. GitHub repository connect করুন
3. Settings:
   - Name: `ngo-system`
   - Build Command: `./build.sh`
   - Start Command: `gunicorn app:app`
   - Region: Singapore

### ধাপ ৫: Environment Variables
Add করুন:
```
DATABASE_URL = [আপনার PostgreSQL Internal URL]
SECRET_KEY = your-secret-key-change-this
```

### ধাপ ৬: Deploy!
"Create Web Service" ক্লিক করুন। Done! 🎉

---

## 🔧 Option 2: External MySQL দিয়ে Deploy

### ধাপ ১: Free MySQL Database নিন

**FreeMySQLHosting.net থেকে:**
1. https://www.freemysqlhosting.net এ যান
2. Sign up করুন
3. Database credentials note করুন:
   ```
   Host: sql12.freemysqlhosting.net
   Database: sql12xxxxx
   Username: sql12xxxxx
   Password: xxxxxxxxxx
   Port: 3306
   ```

### ধাপ ২: GitHub Push
```bash
git add .
git commit -m "MySQL deployment"
git push
```

### ধাপ ৩: Render Web Service
1. "New +" > "Web Service"
2. Repository connect করুন
3. Build Command: `./build.sh`
4. Start Command: `gunicorn app:app`

### ধাপ ৪: Environment Variables
```
MYSQL_HOST=sql12.freemysqlhosting.net
MYSQL_USER=sql12xxxxx
MYSQL_PASSWORD=xxxxxxxxxx
MYSQL_DB=sql12xxxxx
SECRET_KEY=your-secret-key
```

### ধাপ ৫: Deploy
"Create Web Service" ক্লিক করুন!

---

## 📊 কোনটা ভালো?

| Feature | PostgreSQL | MySQL |
|---------|-----------|-------|
| Cost | ✅ Free | ⚠️ External/Paid |
| Setup | ✅ Easy | ⚠️ Complex |
| Performance | ✅ Fast | ✅ Good |
| Storage | ✅ 1GB Free | ⚠️ Limited |
| Backups | ✅ Auto | ❌ Manual |

**Recommendation: PostgreSQL ব্যবহার করুন!**

---

## 🎯 Quick Start (PostgreSQL)

1. **GitHub Push:**
   ```bash
   DEPLOY_TO_RENDER.bat
   ```

2. **Render.com:**
   - PostgreSQL Database তৈরি করুন
   - Web Service তৈরি করুন
   - DATABASE_URL add করুন
   - Deploy!

3. **Live!**
   আপনার URL: `https://ngo-system.onrender.com`

---

## 🔐 Default Login

- **Admin:** admin@example.com / admin123
- **Office:** office@example.com / office123

⚠️ Login করে password change করুন!

---

## 💡 Tips

1. **Free Plan:** 750 hours/month
2. **Sleep:** 15 min inactivity পর sleep
3. **Wake:** First request slow হতে পারে
4. **Logs:** Dashboard এ real-time logs দেখুন
5. **Auto Deploy:** Git push = Auto deploy

---

## 🐛 Problem?

**Build Failed:**
```bash
git update-index --chmod=+x build.sh
git commit -m "Fix permissions"
git push
```

**Database Error:**
- Environment Variables check করুন
- Database running আছে কিনা দেখুন

**App Not Starting:**
- Render Logs check করুন
- `gunicorn app:app` command ঠিক আছে কিনা

---

## ✅ Success!

আপনার NGO System এখন live! 🎉

Share করুন এবং ব্যবহার শুরু করুন!
