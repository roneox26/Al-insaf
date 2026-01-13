@echo off
chcp 65001 >nul
cls
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║        File Attachment Support - Setup                ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo Adding file attachment support to messaging...
echo.

python add_file_attachment.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ╔════════════════════════════════════════════════════════╗
    echo ║              Setup Complete! ✓                         ║
    echo ╚════════════════════════════════════════════════════════╝
    echo.
    echo You can now send:
    echo   📷 Images (JPG, PNG, GIF)
    echo   📄 PDFs
    echo   📝 Documents (DOC, DOCX)
    echo   📊 Excel files (XLS, XLSX)
    echo.
    echo Max file size: 10MB
) else (
    echo.
    echo Setup failed! Check error above.
)

echo.
pause
