# OTP System for Admin Settings

## ✅ কি করা হয়েছে

1. **OTP Model** তৈরি করা হয়েছে (`models/otp_model.py`)
   - 6-digit OTP generate করে
   - 5 মিনিটের জন্য valid থাকে
   - একবার use করলে expire হয়ে যায়

2. **OTP Template** তৈরি করা হয়েছে (`templates/admin_settings_otp.html`)
   - OTP screen এ দেখায়
   - User OTP input করতে পারে

3. **OTP Routes** তৈরি করা হয়েছে
   - `/admin/settings/request_otp` - OTP generate করে
   - `/admin/settings/verify_otp` - OTP verify করে

## 🚀 Setup করার নিয়ম

### Step 1: Database Update করুন
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Step 2: Application Restart করুন
```bash
python run.py
```

### Step 3: Test করুন
1. Admin login করুন
2. Admin Settings এ যান
3. OTP screen দেখাবে
4. OTP code input করুন
5. Settings page খুলবে

## 📝 কিভাবে কাজ করে

```
Admin Settings ক্লিক
    ↓
OTP Generate হবে (6-digit)
    ↓
OTP Screen এ দেখাবে
    ↓
User OTP Input করবে
    ↓
Verify হলে Settings Page খুলবে
```

## 🔐 Security Features

- ✅ 6-digit random OTP
- ✅ 5 মিনিট validity
- ✅ একবার use করলে expire
- ✅ Wrong OTP reject করবে
- ✅ Expired OTP reject করবে

## 📧 Production এ Email/SMS পাঠানো

`app.py` তে `request_admin_otp` function এ:

```python
# Email পাঠানোর জন্য
from flask_mail import Mail, Message

mail = Mail(app)

@app.route('/admin/settings/request_otp', methods=['GET'])
@login_required
def request_admin_otp():
    otp = OTP.create_otp(current_user.id, purpose='admin_settings')
    
    # Send email
    msg = Message('Your OTP Code', 
                  recipients=[current_user.email])
    msg.body = f'Your OTP code is: {otp.code}'
    mail.send(msg)
    
    flash('OTP sent to your email!', 'success')
    return render_template('admin_settings_otp.html')
```

## 🎯 Future Enhancements

- [ ] SMS integration
- [ ] Email integration  
- [ ] Resend OTP option
- [ ] OTP history tracking
- [ ] Multiple OTP purposes (password reset, etc.)

---

**Developer:** Roneo  
**Date:** 2024
