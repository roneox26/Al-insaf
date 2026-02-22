# Loan Sheet Feature Setup

## নতুন Feature: প্রতিটি Loan এর জন্য আলাদা Sheet

এখন যখন নতুন loan দেওয়া হবে, তখন সেই loan এর জন্য একটি আলাদা loan sheet page তৈরি হবে।

## Setup করার নিয়ম

### ১. Database Migration চালান

```bash
python add_loan_id_column.py
```

এটি `loan_collections` table এ `loan_id` column add করবে এবং existing collections কে তাদের loans এর সাথে link করবে।

### ২. Application Restart করুন

```bash
python run.py
```

## কিভাবে কাজ করে

### নতুন Loan দেওয়ার সময়:

1. **Admin Dashboard** > **Manage Loans** > **Add New Loan**
2. Loan এর সব তথ্য দিন (Customer, Amount, Interest, etc.)
3. **Submit** করুন
4. Automatically নতুন loan এর জন্য একটি **Loan Sheet** page খুলবে

### Existing Loans এর Sheet দেখতে:

1. **Manage Loans** page এ যান
2. যেকোনো loan এর পাশে **"📄 Loan Sheet"** button ক্লিক করুন
3. সেই loan এর সম্পূর্ণ details এবং collection history দেখতে পারবেন

## Features

### Individual Loan Sheet এ থাকবে:

- ✅ Customer এর সম্পূর্ণ তথ্য
- ✅ Loan Amount + Interest
- ✅ শুধুমাত্র এই loan এর collections
- ✅ Installment details
- ✅ Remaining balance
- ✅ Savings balance
- ✅ Print option

### Benefits:

- 📊 প্রতিটি loan আলাদাভাবে track করা যাবে
- 🎯 Specific loan এর payment history দেখা যাবে
- 📄 Individual loan sheet print করা যাবে
- 🔍 Multiple loans থাকলে confusion হবে না

## Database Changes

### loan_collections table:
- **নতুন column:** `loan_id` (INTEGER, nullable)
- **Purpose:** প্রতিটি collection কোন loan এর জন্য তা track করা

### Relationship:
```
Loan (1) -----> (Many) LoanCollection
```

## Troubleshooting

### যদি "loan_id column does not exist" error আসে:

```bash
python add_loan_id_column.py
```

### যদি existing collections link না হয়:

Migration script automatically সব existing collections কে তাদের সবচেয়ে recent loan এর সাথে link করবে।

### Deploy করার পরে:

**Render.com:**
```bash
# Dashboard > Shell
python add_loan_id_column.py
```

**PythonAnywhere:**
```bash
cd ~/Al-insaf
python add_loan_id_column.py
# Web tab > Reload button
```

## Routes

### নতুন Routes:

1. **`/loan_sheet/<loan_id>`** - Individual loan এর sheet
2. **`/customer_loan_sheet/<customer_id>`** - Customer এর সব loans (existing)

### Updated Routes:

- **`/loan/add`** - এখন loan sheet এ redirect করে

## Files Changed

1. **app.py** - নতুন `loan_sheet()` route added
2. **models/loan_collection_model.py** - `loan_id` column added
3. **templates/manage_loans.html** - Loan Sheet button added
4. **add_loan_id_column.py** - Migration script (নতুন)

## Testing

### Test করার জন্য:

1. নতুন loan দিন
2. Check করুন loan sheet automatically খুলছে কিনা
3. Manage Loans থেকে loan sheet button test করুন
4. Print করে দেখুন সব ঠিক আছে কিনা

---

**✅ Setup Complete!**

এখন প্রতিটি loan এর জন্য আলাদা sheet page তৈরি হবে! 🎉
