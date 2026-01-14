#!/bin/bash
# DigitalOcean Error Log Checker

echo "=== Checking Application Logs ==="
echo ""

# Check if running with gunicorn
if pgrep -f gunicorn > /dev/null; then
    echo "✓ Gunicorn is running"
else
    echo "✗ Gunicorn is NOT running"
fi

echo ""
echo "=== Recent Error Logs ==="
# Check common log locations
if [ -f "/var/log/nginx/error.log" ]; then
    echo "--- Nginx Error Log (last 20 lines) ---"
    tail -n 20 /var/log/nginx/error.log
fi

if [ -f "/var/log/gunicorn/error.log" ]; then
    echo "--- Gunicorn Error Log (last 20 lines) ---"
    tail -n 20 /var/log/gunicorn/error.log
fi

echo ""
echo "=== Python Test ==="
python3 -c "from app import app; print('✓ App imports successfully')" 2>&1

echo ""
echo "=== Database Check ==="
if [ -f "instance/loan.db" ]; then
    echo "✓ Database file exists"
else
    echo "✗ Database file NOT found - Run: python3 create_db.py"
fi

echo ""
echo "=== Environment Variables ==="
echo "DATABASE_URL: ${DATABASE_URL:-Not set}"
echo "SECRET_KEY: ${SECRET_KEY:-Not set (using default)}"
