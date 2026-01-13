@echo off
echo ========================================
echo Due Report Improvements Setup
echo ========================================
echo.

echo Step 1: Adding Follow-up Table...
python add_followup_table.py
echo.

echo Step 2: Verifying Installation...
python -c "from models.followup_model import FollowUp; print('✅ FollowUp model imported successfully')"
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo New Features Available:
echo - Advanced Filtering
echo - Risk Analytics
echo - CSV Export
echo - Follow-up Management
echo.
echo Access: http://localhost:5000/due_report
echo.
pause
