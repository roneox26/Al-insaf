# Logo Setup Instructions

## আপনার Logo যোগ করার নিয়ম

আপনার WhatsApp থেকে পাঠানো logo image টি website এ ব্যবহার করতে:

### Step 1: Logo Image Copy করুন
1. আপনার "WhatsApp Image 2025-12-15 at 7.31.56 PM.jpeg" file টি খুঁজে বের করুন
2. File টি copy করুন
3. এই folder এ paste করুন: `e:\ngo\static\images\`
4. File এর নাম পরিবর্তন করে `logo.jpg` রাখুন

### Step 2: অথবা Command দিয়ে Copy করুন
```bash
copy "WhatsApp Image 2025-12-15 at 7.31.56 PM.jpeg" "e:\ngo\static\images\logo.jpg"
```

## Logo কোথায় কোথায় দেখাবে:

✅ **Login Page** - Background watermark এবং header এ
✅ **Admin Dashboard** - Navbar এ এবং background watermark
✅ **All Pages** - Background watermark হিসেবে (subtle effect)

## Logo Features:

- 🎨 Beautiful circular logo with "AL" text
- 🇧🇩 Bengali organization name
- 💫 Watermark effect on all pages
- 🖼️ Navbar branding
- 📱 Responsive design

## যদি Logo না দেখায়:

1. Check করুন file টি সঠিক জায়গায় আছে কিনা: `static/images/logo.jpg`
2. Browser refresh করুন (Ctrl + F5)
3. Application restart করুন: `python run.py`

---

**Note:** Logo file টি অবশ্যই `static/images/logo.jpg` নামে থাকতে হবে।
