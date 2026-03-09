# Collection Time Fix - টাইম ঠিক করার আপডেট

## সমস্যা
Collection করার সময় টাইম ঠিক দেখাচ্ছিল না। UTC time (6 ঘন্টা পিছিয়ে) সেভ হচ্ছিল।

## সমাধান
সব model এ `datetime.utcnow` থেকে `datetime.now` এ পরিবর্তন করা হয়েছে। এখন বাংলাদেশ সময় অনুযায়ী সঠিক টাইম সেভ হবে।

## পরিবর্তিত ফাইল
- `models/loan_collection_model.py` - Loan collection time
- `models/saving_collection_model.py` - Saving collection time
- `models/expense_model.py` - Expense date
- `models/withdrawal_model.py` - Withdrawal date
- `models/investment_model.py` - Investment date
- `models/customer_model.py` - Customer created date
- `models/loan_model.py` - Loan date
- `models/collection_model.py` - Collection date
- `models/message_model.py` - Message date
- `models/note_model.py` - Note date
- `models/cash_balance_model.py` - Balance update date
- `models/investor_model.py` - Investor created date
- `models/user_model.py` - User join date
- `models/staff_model.py` - Staff join date
- `models/saving_model.py` - Saving date

## কিভাবে ব্যবহার করবেন

### নতুন Installation
কোন কাজ করার দরকার নেই। সরাসরি চালান:
```bash
python run.py
```

### Existing Database এর জন্য
পুরাতন data এর টাইম পরিবর্তন হবে না। শুধু নতুন collection থেকে সঠিক টাইম দেখাবে।

**কোন migration script চালানোর দরকার নেই।**

## যাচাই করুন
1. Application চালান: `python run.py`
2. একটি collection করুন
3. Collection history দেখুন - সঠিক বাংলাদেশ সময় দেখাবে

## নোট
- পুরাতন collections এর টাইম 6 ঘন্টা পিছিয়ে থাকবে (UTC time)
- নতুন collections থেকে সঠিক সময় দেখাবে
- এটা স্বাভাবিক এবং কোন সমস্যা নয়

## Deploy করার পরে
Render/Railway/PythonAnywhere তে deploy করার পরে:
1. Application restart করুন
2. নতুন collection করুন
3. সঠিক টাইম দেখাবে

---
**Updated:** 2024
**Version:** 1.1
