@echo off
chcp 65001 >nul
cls
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   Enhanced Messaging System - Database Update         ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo This will update your database to support:
echo   ✓ Voice Messages
echo   ✓ Call System  
echo   ✓ Two-way Messaging
echo   ✓ Modern UI
echo.
echo Press any key to continue...
pause >nul

echo.
echo Updating database...
python update_messages_db.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ╔════════════════════════════════════════════════════════╗
    echo ║              Update Successful! ✓                      ║
    echo ╚════════════════════════════════════════════════════════╝
    echo.
    echo You can now use:
    echo   • Voice Messages 🎤
    echo   • Voice/Video Calls 📞
    echo   • Modern Chat UI 💬
    echo   • Real-time Updates ⚡
    echo.
    echo Run 'python run.py' to start the application
) else (
    echo.
    echo ╔════════════════════════════════════════════════════════╗
    echo ║              Update Failed! ✗                          ║
    echo ╚════════════════════════════════════════════════════════╝
    echo.
    echo Please check the error message above
)

echo.
echo Press any key to exit...
pause >nul
