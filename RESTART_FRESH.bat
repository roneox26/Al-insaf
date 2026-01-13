@echo off
echo ==========================================
echo FRESH DATABASE RESTART
echo ==========================================
echo.
echo This will:
echo 1. Backup your current database
echo 2. Create a fresh database
echo 3. Start Flask app
echo.
echo Press Ctrl+C to cancel or
pause

echo.
echo Backing up database...
ren instance\loan.db loan_backup_%time:~0,2%%time:~3,2%%time:~6,2%.db

echo Creating fresh database...
python create_db.py

echo.
echo Starting Flask app...
python run.py
