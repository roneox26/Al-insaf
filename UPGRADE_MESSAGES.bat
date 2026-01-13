@echo off
echo ========================================
echo   Message System Migration
echo ========================================
echo.
echo This will upgrade your messaging system to WhatsApp style
echo.
pause

python migrate_messages.py

echo.
echo ========================================
echo   Migration Complete!
echo ========================================
echo.
echo You can now use the new messaging system.
echo.
pause
