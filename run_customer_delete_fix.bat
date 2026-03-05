@echo off
echo ========================================
echo Customer Delete Fix - Migration
echo ========================================
echo.
echo This will update the database to preserve
echo collection history when customers are deleted.
echo.
pause

python fix_customer_delete.py

echo.
echo ========================================
echo Migration Complete!
echo ========================================
echo.
echo You can now delete customers without losing
echo collection history in reports.
echo.
pause
