@echo off
echo Fixing Render deployment issues...
echo.

git add .
git commit -m "Fix Internal Server Error - Add proper error handling"
git push origin main

echo.
echo ✅ Fix pushed to GitHub!
echo.
echo Next steps:
echo 1. Go to Render Dashboard
echo 2. Your service will auto-deploy
echo 3. Check Logs if error persists
echo.
echo If still error, check:
echo - DATABASE_URL is set
echo - SECRET_KEY is set
echo - Build completed successfully
echo.
pause
