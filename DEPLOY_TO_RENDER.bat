@echo off
echo ========================================
echo   Render.com Deployment Setup
echo ========================================
echo.

echo Step 1: Checking Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo Git not found! Please install Git first.
    echo Download: https://git-scm.com/download/win
    pause
    exit /b
)
echo Git found!
echo.

echo Step 2: Initialize Git repository...
if not exist .git (
    git init
    echo Git initialized!
) else (
    echo Git already initialized!
)
echo.

echo Step 3: Add all files...
git add .
echo Files added!
echo.

echo Step 4: Commit changes...
git commit -m "Ready for Render deployment"
echo Committed!
echo.

echo Step 5: GitHub Setup
echo.
echo Please create a repository on GitHub:
echo 1. Go to https://github.com/new
echo 2. Create a new repository (e.g., ngo-system)
echo 3. Copy the repository URL
echo.
set /p repo_url="Enter your GitHub repository URL: "

if "%repo_url%"=="" (
    echo No URL provided!
    pause
    exit /b
)

echo.
echo Step 6: Adding remote...
git remote remove origin 2>nul
git remote add origin %repo_url%
echo Remote added!
echo.

echo Step 7: Pushing to GitHub...
git branch -M main
git push -u origin main
echo.

if errorlevel 1 (
    echo Push failed! Please check:
    echo 1. GitHub repository exists
    echo 2. You have access to the repository
    echo 3. Git credentials are correct
    pause
    exit /b
)

echo ========================================
echo   SUCCESS! Code pushed to GitHub
echo ========================================
echo.
echo Next Steps:
echo 1. Go to https://render.com
echo 2. Sign up/Login with GitHub
echo 3. Click "New +" and select "Web Service"
echo 4. Connect your GitHub repository
echo 5. Render will auto-detect settings from render.yaml
echo 6. Click "Create Web Service"
echo.
echo Your app will be live in 5-10 minutes!
echo.
echo For detailed guide, read: RENDER_DEPLOY.md
echo.
pause
