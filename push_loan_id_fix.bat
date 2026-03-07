@echo off
echo ========================================
echo   Pushing Loan ID Fix to GitHub
echo ========================================
echo.

git add .
git commit -m "Fix: Add loan_id column migration for PostgreSQL/Render deployment"
git push origin main

echo.
echo ========================================
echo Push completed!
echo.
echo Next steps for Render.com:
echo 1. Wait for auto-deploy to complete
echo 2. Go to Shell tab in Render dashboard
echo 3. Run: python migrate_add_loan_id_universal.py
echo 4. Restart application
echo ========================================
pause
