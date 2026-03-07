@echo off
echo ========================================
echo   Al-Insaf NGO - Database Migration
echo   Fixing loan_id column issue
echo ========================================
echo.

echo Running database migration...
python migrate_add_loan_id_universal.py

echo.
echo ========================================
echo Migration completed!
echo.
echo If you're on Render.com:
echo 1. Go to your Render dashboard
echo 2. Open Shell tab
echo 3. Run: python migrate_add_loan_id_universal.py
echo 4. Restart your application
echo ========================================
pause