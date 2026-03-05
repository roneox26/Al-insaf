# Email Setup for OTP System

## Gmail Setup (Recommended)

1. **Enable 2-Step Verification:**
   - Go to: https://myaccount.google.com/security
   - Enable "2-Step Verification"

2. **Generate App Password:**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Copy the 16-character password

3. **Set Environment Variables:**

### Windows (CMD):
```cmd
set MAIL_USERNAME=your-email@gmail.com
set MAIL_PASSWORD=your-app-password
```

### Windows (PowerShell):
```powershell
$env:MAIL_USERNAME="your-email@gmail.com"
$env:MAIL_PASSWORD="your-app-password"
```

### Linux/Mac:
```bash
export MAIL_USERNAME=your-email@gmail.com
export MAIL_PASSWORD=your-app-password
```

## Install Flask-Mail

```bash
pip install Flask-Mail
```

## Test Email

Run application and try Admin Settings. OTP will be sent to admin email.

## Production Deployment

Add to environment variables on hosting platform:
- `MAIL_USERNAME`: your-email@gmail.com
- `MAIL_PASSWORD`: your-app-password

## Fallback

If email fails, OTP will still display on screen as backup.
