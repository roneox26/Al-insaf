@echo off
echo ================================================
echo Loan Sheet Feature Setup
echo ================================================
echo.

echo Step 1: Running database migration...
python add_loan_id_column.py

echo.
echo ================================================
echo Setup Complete!
echo ================================================
echo.
echo You can now:
echo 1. Add new loans - they will automatically create loan sheets
echo 2. View existing loan sheets from Manage Loans page
echo.
echo Press any key to start the application...
pause > nul

python run.py
