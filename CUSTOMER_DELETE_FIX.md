# Customer Delete Fix - Collection History Preserved

## সমস্যা
Customer ডিলেট করলে তার সব collection data ডিলেট হয়ে যাচ্ছিল এবং রিপোর্ট থেকে হারিয়ে যাচ্ছিল।

## সমাধান
এখন customer ডিলেট করলে:
- ✅ Collection data রাখা হবে (রিপোর্টের জন্য)
- ✅ Customer name "[DELETED]" tag দিয়ে mark করা হবে
- ✅ Cash balance সঠিক থাকবে
- ✅ সব রিপোর্টে পুরনো data দেখা যাবে

## Migration চালানোর নিয়ম

### Windows:
```bash
python fix_customer_delete.py
```

### Render.com / PythonAnywhere:
```bash
python fix_customer_delete.py
```

## কি পরিবর্তন হয়েছে?

### 1. Database Models
- `loan_collections.customer_id` → nullable
- `saving_collections.customer_id` → nullable  
- `fee_collections.customer_id` → nullable

### 2. Delete Function
Customer ডিলেট করলে:
- Collections **ডিলেট হবে না** (রিপোর্টের জন্য রাখা হবে)
- শুধু `customer_id = NULL` set করা হবে
- Loan name এ `[DELETED]` tag যোগ হবে

### 3. Reports
সব রিপোর্টে deleted customer এর data দেখা যাবে:
- Daily Report
- Monthly Report
- Staff Collection Report
- Profit/Loss Report

## উদাহরণ

**আগে:**
```
Customer "রহিম" ডিলেট → সব collection data মুছে যেত → রিপোর্ট থেকে হারিয়ে যেত
```

**এখন:**
```
Customer "রহিম" ডিলেট → Collection data থাকবে → রিপোর্টে "[DELETED] রহিম" দেখাবে
```

## Important Notes

1. **Deactivate করাই ভালো**: Customer কে permanent delete না করে deactivate করা উচিত
2. **Backup নিন**: Migration চালানোর আগে database backup নিন
3. **Test করুন**: Local এ test করে তারপর production এ deploy করুন

## Troubleshooting

### Error: "FOREIGN KEY constraint failed"
**Solution:** Migration script চালান:
```bash
python fix_customer_delete.py
```

### রিপোর্টে customer name দেখাচ্ছে না
**Solution:** Template এ `customer.name if customer else '[Deleted Customer]'` ব্যবহার করুন

## Deploy করার পর

1. Migration চালান: `python fix_customer_delete.py`
2. Application restart করুন
3. Test করুন: একটি inactive customer ডিলেট করে দেখুন
4. রিপোর্ট check করুন

---

**Developer:** Roneo  
**Date:** 2024
