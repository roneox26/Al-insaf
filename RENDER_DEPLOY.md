# 🚀 Render.com এ Deploy করার সম্পূর্ণ গাইড

## ✅ Prerequisites

1. GitHub account
2. Render.com account (free)
3. আপনার code GitHub এ push করা থাকতে হবে

---

## 📝 Step by Step Deployment

### **ধাপ ১: GitHub এ Code Push করুন**

```bash
cd e:\ngo
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ngo-system.git
git push -u origin main
```

### **ধাপ ২: Render.com এ Account তৈরি করুন**

1. যান: https://render.com
2. "Get Started" ক্লিক করুন
3. GitHub দিয়ে Sign up করুন

### **ধাপ ৩: PostgreSQL Database তৈরি করুন**

1. Render Dashboard এ যান
2. "New +" ক্লিক করুন
3. "PostgreSQL" select করুন
4. Fill করুন:
   - **Name:** `ngo-database`
   - **Database:** `ngo_db`
   - **User:** `ngo_user`
   - **Region:** Singapore (closest to Bangladesh)
   - **Plan:** Free
5. "Create Database" ক্লিক করুন
6. **Internal Database URL** copy করে রাখুন

### **ধাপ ৪: Web Service তৈরি করুন**

1. "New +" > "Web Service" ক্লিক করুন
2. GitHub repository connect করুন
3. Repository select করুন
4. Fill করুন:
   - **Name:** `ngo-system`
   - **Region:** Singapore
   - **Branch:** `main`
   - **Root Directory:** (খালি রাখুন)
   - **Runtime:** Python 3
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free

### **ধাপ ৫: Environment Variables সেট করুন**

"Environment" section এ যান এবং add করুন:

```
DATABASE_URL = [আপনার PostgreSQL Internal Database URL]
SECRET_KEY = your-secret-key-here-change-this
PYTHON_VERSION = 3.10.0
```

### **ধাপ ৬: Deploy করুন**

1. "Create Web Service" ক্লিক করুন
2. Automatic deployment শুরু হবে
3. 5-10 মিনিট অপেক্ষা করুন
4. Deploy সফল হলে আপনার URL পাবেন: `https://ngo-system.onrender.com`

---

## 🔧 Important Files (Already Created)

✅ `build.sh` - Build script
✅ `requirements.txt` - Dependencies
✅ `config.py` - Database configuration
✅ `app.py` - Main application

---

## 🎯 Default Login Credentials

প্রথমবার login করার জন্য:

- **Admin:** admin@example.com / admin123
- **Office Staff:** office@example.com / office123
- **Field Staff:** staff@example.com / staff123

⚠️ **Login করার পর password change করুন!**

---

## 🔄 Code Update করার নিয়ম

যখন code change করবেন:

```bash
git add .
git commit -m "Your update message"
git push
```

Render automatically নতুন version deploy করবে!

---

## 📊 Free Plan Limitations

- ✅ 750 hours/month (যথেষ্ট)
- ✅ 512 MB RAM
- ✅ PostgreSQL 1GB storage
- ⚠️ 15 minutes inactivity এ sleep mode
- ⚠️ First request slow হতে পারে (sleep থেকে wake up)

---

## 🐛 Troubleshooting

### Problem 1: Build Failed
**Solution:** Check `build.sh` file permissions
```bash
git update-index --chmod=+x build.sh
git commit -m "Make build.sh executable"
git push
```

### Problem 2: Database Connection Error
**Solution:** 
- Environment Variables এ DATABASE_URL সঠিক আছে কিনা check করুন
- PostgreSQL database running আছে কিনা check করুন

### Problem 3: Application Not Starting
**Solution:** Logs check করুন:
- Render Dashboard > Your Service > Logs

### Problem 4: Static Files Not Loading
**Solution:** `app.py` তে check করুন:
```python
app.static_folder = 'static'
app.static_url_path = '/static'
```

---

## 🌟 Pro Tips

1. **Custom Domain:** Render এ custom domain add করতে পারবেন
2. **Auto Deploy:** GitHub push করলেই automatic deploy হবে
3. **Logs:** Real-time logs দেখতে পারবেন
4. **Metrics:** CPU, Memory usage monitor করতে পারবেন
5. **Backup:** PostgreSQL database regular backup নিন

---

## 📱 Mobile Access

Deploy হওয়ার পর যেকোনো device থেকে access করতে পারবেন:
- Computer
- Mobile
- Tablet

শুধু browser এ আপনার URL open করুন!

---

## 💰 Upgrade Options

যদি বেশি traffic আসে:

- **Starter Plan:** $7/month
  - No sleep
  - 512 MB RAM
  - Better performance

- **Standard Plan:** $25/month
  - 2 GB RAM
  - Priority support

---

## ✅ Deployment Checklist

- [ ] Code GitHub এ push করা
- [ ] Render account তৈরি করা
- [ ] PostgreSQL database তৈরি করা
- [ ] Web Service তৈরি করা
- [ ] Environment variables সেট করা
- [ ] Build successful
- [ ] Application running
- [ ] Login test করা
- [ ] Password change করা

---

## 🎉 Congratulations!

আপনার NGO Management System এখন live!

Share করুন: `https://your-app-name.onrender.com`

---

## 📞 Support

সমস্যা হলে:
1. Render Logs check করুন
2. GitHub Issues create করুন
3. Documentation পড়ুন: https://render.com/docs

**Happy Deploying! 🚀**
