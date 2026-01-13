@echo off
echo ========================================
echo DATABASE FIX SCRIPT
echo ========================================
echo.
echo IMPORTANT: Make sure Flask app is STOPPED (Ctrl+C)
echo Press any key to continue or Ctrl+C to cancel...
pause > nul

echo.
echo Step 1: Creating backup...
copy instance\loan.db instance\loan_backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%.db
echo Backup created!

echo.
echo Step 2: Deleting old database...
del instance\loan.db
echo Database deleted!

echo.
echo Step 3: Creating fresh database...
python create_db.py
echo Database recreated!

echo.
echo ========================================
echo FIX COMPLETE!
echo ========================================
echo.
echo Your old data is backed up in instance folder
echo Now start your Flask app: python run.py
echo.
pause
