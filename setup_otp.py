# -*- coding: utf-8 -*-
"""
Add OTP System to Admin Settings
"""

print("=" * 60)
print("OTP System Setup for Admin Settings")
print("=" * 60)
print()
print("✓ OTP Model created: models/otp_model.py")
print("✓ OTP Template created: templates/admin_settings_otp.html")
print()
print("Next steps:")
print("1. Run: python -c \"from app import app, db; app.app_context().push(); db.create_all()\"")
print("2. Restart your application")
print("3. Go to Admin Settings - it will ask for OTP")
print()
print("How it works:")
print("- Admin Settings এ যেতে OTP চাইবে")
print("- 6-digit OTP screen এ দেখাবে")
print("- OTP 5 মিনিটের জন্য valid থাকবে")
print("- OTP verify হলে Settings page খুলবে")
print()
print("=" * 60)
