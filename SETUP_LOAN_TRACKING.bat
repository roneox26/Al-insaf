@echo off
chcp 65001 >nul
echo ========================================
echo   লোন ট্র্যাকিং সিস্টেম Setup
echo ========================================
echo.

echo [1/2] Database আপডেট করা হচ্ছে...
python add_loan_id_to_collections.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ Error: Database আপডেট করতে সমস্যা হয়েছে!
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ Setup সম্পন্ন হয়েছে!
echo ========================================
echo.
echo এখন কি করবেন:
echo 1. App restart করুন: python run.py
echo 2. Login করুন
echo 3. নতুন collection করুন
echo.
echo বিস্তারিত জানতে LOAN_TRACKING_GUIDE.md দেখুন
echo.
pause
