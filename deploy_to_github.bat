@echo off
echo ========================================
echo   GitHub Push Script
echo ========================================
echo.

cd /d e:\ngo

echo [1/3] Adding files to git...
git add .

echo.
echo [2/3] Committing changes...
git commit -m "Fix Flask 3.0 compatibility - remove deprecated before_first_request"

echo.
echo [3/3] Pushing to GitHub...
git push origin main

echo.
echo ========================================
echo   DONE! Now go to PythonAnywhere
echo ========================================
echo.
echo Next steps:
echo 1. Go to PythonAnywhere Bash Console
echo 2. Run: cd ~/Al-insaf
echo 3. Run: git pull origin main
echo 4. Go to Web tab and click Reload
echo.
pause
