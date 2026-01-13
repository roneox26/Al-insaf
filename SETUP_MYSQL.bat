@echo off
echo ========================================
echo   MySQL Database Setup for NGO System
echo ========================================
echo.

echo Step 1: Installing MySQL dependencies...
pip install PyMySQL cryptography
echo.

echo Step 2: Testing MySQL connection...
python test_mysql_connection.py
echo.

echo Step 3: Do you want to migrate data from SQLite to MySQL? (Y/N)
set /p migrate="Enter choice: "

if /i "%migrate%"=="Y" (
    echo.
    echo Starting migration...
    python migrate_to_mysql.py
    echo.
    echo Migration completed!
) else (
    echo.
    echo Skipping migration. You can run it later with:
    echo python migrate_to_mysql.py
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Your application is now configured for MySQL.
echo Run the application with: python run.py
echo.
pause
