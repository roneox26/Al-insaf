@echo off
echo ==========================================
echo   Pushing to GitHub
echo ==========================================
echo.

cd /d e:\ngo

echo [Step 1/3] Staging files...
git add .

echo.
echo [Step 2/3] Committing...
git commit -m "Fix Flask 3.0 compatibility - remove deprecated before_first_request"

echo.
echo [Step 3/3] Pushing to GitHub...
git push origin main

echo.
echo ==========================================
echo   SUCCESS! Code pushed to GitHub
echo ==========================================
echo.
echo Now update PythonAnywhere:
echo   1. Go to PythonAnywhere Bash Console
echo   2. Run: cd ~/Al-insaf
echo   3. Run: git pull origin main
echo   4. Run: python create_db.py
echo   5. Go to Web tab and click Reload
echo.
pause
