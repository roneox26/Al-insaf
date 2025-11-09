@echo off
echo ========================================
echo NGO Management System - Fresh Start
echo ========================================
echo.

echo Stopping any running Python processes...
taskkill /F /IM python.exe /T 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Deleting old database...
if exist instance\loan.db (
    del /F instance\loan.db
    echo Database deleted successfully!
) else (
    echo No existing database found.
)

echo.
echo Creating new database...
python -c "from app import app, db; from flask_bcrypt import Bcrypt; from models.user_model import User; from models.cash_balance_model import CashBalance; bcrypt = Bcrypt(app); app.app_context().push(); db.create_all(); admin = User(name='Admin', email='admin@example.com', password=bcrypt.generate_password_hash('admin123').decode('utf-8'), role='admin'); staff = User(name='Staff', email='staff@example.com', password=bcrypt.generate_password_hash('staff123').decode('utf-8'), role='staff'); cash = CashBalance(balance=0); db.session.add(admin); db.session.add(staff); db.session.add(cash); db.session.commit(); print('Database created successfully!')"

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Login Credentials:
echo   Admin: admin@example.com / admin123
echo   Staff: staff@example.com / staff123
echo.
echo To start the application, run:
echo   python run.py
echo.
pause
