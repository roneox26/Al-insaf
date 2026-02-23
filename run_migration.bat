@echo off
echo ========================================
echo Individual Loan Sheet Fix - Migration
echo ========================================
echo.
echo Running migration to add loan_id column...
echo.

python migrate_add_loan_id.py

echo.
echo ========================================
echo Migration completed!
echo ========================================
echo.
echo Press any key to exit...
pause > nul
