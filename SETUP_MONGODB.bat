@echo off
echo ============================================================
echo MongoDB Setup - Al-Insaf NGO System
echo ============================================================
echo.

echo Step 1: Installing MongoDB dependencies...
pip install flask-mongoengine mongoengine pymongo
echo.

echo Step 2: Testing MongoDB connection...
python -c "from pymongo import MongoClient; client = MongoClient('mongodb://localhost:27017/'); print('MongoDB Connected!')"
echo.

echo Step 3: Starting data migration...
python migrate_to_mongodb.py
echo.

echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Next steps:
echo 1. Update app.py to use MongoDB models
echo 2. Run: python run.py
echo.
pause
