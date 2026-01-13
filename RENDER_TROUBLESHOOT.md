# 🔧 Render Internal Server Error - Fix Guide

## 📊 Step 1: Check Logs

1. Go to: https://dashboard.render.com
2. Click your service
3. Click "Logs" tab
4. Look for error messages

## 🔍 Common Errors & Solutions:

### Error 1: "No module named 'app'"
**Fix:** Check Start Command
```
Start Command: gunicorn app:app
```

### Error 2: "DATABASE_URL not set"
**Fix:** Add Environment Variable
```
DATABASE_URL = [Your PostgreSQL URL]
```

### Error 3: "Table doesn't exist"
**Fix:** Redeploy with Clear Cache
- Settings > Clear build cache & deploy

### Error 4: "Port binding error"
**Fix:** Gunicorn should bind to 0.0.0.0
```
Start Command: gunicorn app:app --bind 0.0.0.0:$PORT
```

## ✅ Correct Render Settings:

### Build Command:
```bash
./build.sh
```

### Start Command:
```bash
gunicorn app:app
```

### Environment Variables:
```
DATABASE_URL = [PostgreSQL Internal URL]
SECRET_KEY = your-secret-key-here
PYTHON_VERSION = 3.10.0
```

## 🚀 Quick Fix Steps:

1. **Check Logs First**
2. **Verify Environment Variables**
3. **Clear Build Cache & Redeploy**
4. **Check Database Connection**

## 📝 If Still Not Working:

Share the error from Render Logs and I'll help fix it!
