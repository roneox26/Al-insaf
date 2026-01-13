@echo off
echo ========================================
echo   Pushing to GitHub
echo ========================================
echo.

echo Checking Git status...
git status
echo.

echo Adding all files...
git add .
echo.

echo Committing changes...
git commit -m "Updated NGO System - MySQL support, Application Forms, Staff Collections"
echo.

echo Setting remote repository...
git remote remove origin 2>nul
git remote add origin https://github.com/roneox26/Al-insaf.git
echo.

echo Setting branch to main...
git branch -M main
echo.

echo Pushing to GitHub...
git push -u origin main --force
echo.

if errorlevel 1 (
    echo.
    echo ========================================
    echo   Push Failed!
    echo ========================================
    echo.
    echo Please check:
    echo 1. Git is installed
    echo 2. You have access to the repository
    echo 3. GitHub credentials are correct
    echo.
    echo Try manual push:
    echo git push -u origin main --force
    echo.
) else (
    echo.
    echo ========================================
    echo   SUCCESS! Pushed to GitHub
    echo ========================================
    echo.
    echo Repository: https://github.com/roneox26/Al-insaf.git
    echo.
    echo Next Steps:
    echo 1. Go to https://render.com
    echo 2. Sign in with GitHub
    echo 3. Create New Web Service
    echo 4. Select Al-insaf repository
    echo 5. Deploy!
    echo.
)

pause
