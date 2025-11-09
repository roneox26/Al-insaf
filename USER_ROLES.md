# User Roles - NGO Management System

## 3 Types of Users

### 1. Admin (প্রশাসক)
**Login:** admin@example.com / admin123

**Permissions:**
- ✅ সব কিছু দেখতে এবং করতে পারবে
- ✅ Staff যোগ/সম্পাদনা/মুছে ফেলা
- ✅ Loan দেওয়া
- ✅ Cash Balance ম্যানেজ করা
- ✅ Investor ম্যানেজ করা
- ✅ Expense ম্যানেজ করা
- ✅ সব Reports দেখা
- ✅ সব Customers দেখা
- ✅ সব Collections দেখা

---

### 2. Office Staff (অফিস স্টাফ)
**Login:** office@example.com / office123

**Permissions:**
- ✅ **সব Customers দেখতে পারবে** (সব staff এর)
- ✅ **নতুন Customer যোগ করতে পারবে**
- ✅ **সব Customers থেকে Collection করতে পারবে**
- ✅ **সব Daily Collections দেখতে পারবে**
- ✅ Loan Customers দেখতে পারবে
- ❌ Loan দিতে পারবে না
- ❌ Admin features access করতে পারবে না

**Use Case:**
- অফিসে বসে সব field staff এর customers এর collection নিতে পারবে
- যেকোনো customer এর তথ্য দেখতে পারবে
- নতুন customer registration করতে পারবে

---

### 3. Field Staff (ফিল্ড স্টাফ)
**Login:** staff@example.com / staff123

**Permissions:**
- ✅ **শুধু নিজের Customers দেখতে পারবে**
- ✅ নতুন Customer যোগ করতে পারবে (নিজের অধীনে)
- ✅ শুধু নিজের Customers থেকে Collection করতে পারবে
- ✅ নিজের Daily Collections দেখতে পারবে
- ❌ অন্য staff এর customers দেখতে পারবে না
- ❌ Loan দিতে পারবে না
- ❌ Admin features access করতে পারবে না

**Use Case:**
- মাঠে গিয়ে নিজের assigned customers থেকে collection করবে
- নিজের customers এর তথ্য manage করবে

---

## কিভাবে Office Staff তৈরি করবেন?

### Option 1: Script দিয়ে
```bash
python add_office_staff.py
```

### Option 2: Admin Panel থেকে
1. Admin হিসেবে login করুন
2. "Manage Staff" এ যান
3. "Add Staff" ক্লিক করুন
4. তথ্য পূরণ করুন
5. ✅ "Office Staff" checkbox টি check করুন
6. Save করুন

---

## Summary

| Feature | Admin | Office Staff | Field Staff |
|---------|-------|--------------|-------------|
| সব Customers দেখা | ✅ | ✅ | ❌ |
| নিজের Customers দেখা | ✅ | ✅ | ✅ |
| সব থেকে Collection | ✅ | ✅ | ❌ |
| নিজের থেকে Collection | ✅ | ✅ | ✅ |
| Loan দেওয়া | ✅ | ❌ | ❌ |
| Staff ম্যানেজ | ✅ | ❌ | ❌ |
| Reports | ✅ | ❌ | ❌ |
| Cash Balance | ✅ | ❌ | ❌ |

---

**এখন application চালান এবং office staff দিয়ে login করে test করুন!**
