@echo off
echo ================================================
echo Git Push to GitHub
echo ================================================
echo.

cd /d "%~dp0"

echo Checking git status...
git status
echo.

echo Adding all files...
git add .
echo.

echo Committing changes...
git commit -m "Fix customer delete - preserve collection data for reports"
echo.

echo Pushing to GitHub...
git push origin main
echo.

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Push failed! Trying 'master' branch...
    git push origin master
)

echo.
echo ================================================
echo Done! Check Render.com for automatic deployment
echo ================================================
echo.
pause
