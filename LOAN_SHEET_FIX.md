# Individual Loan Sheet Fix - FIFO Implementation

## সমস্যা
Individual Loan Sheets blank আসছিল কারণ:
1. `loan_collections` table এ `loan_id` column ছিল না
2. Collection করার সময় কোন loan এর জন্য collection হচ্ছে সেটা track করা হচ্ছিল না
3. FIFO (First In First Out) principle অনুযায়ী পুরনো loan আগে পরিশোধ করার logic ছিল না

## সমাধান
এখন FIFO principle implement করা হয়েছে:
- যে loan আগে দেওয়া হয়েছে সেটা আগে পরিশোধ হবে
- প্রতিটি collection এর সাথে loan_id track করা হবে
- Individual Loan Sheet এ সঠিক data দেখাবে

## Migration Run করার নিয়ম

### Local Development এ:
```bash
python migrate_add_loan_id.py
```

### Render.com এ:
1. Dashboard > Shell tab এ যাও
2. Run করো:
```bash
python migrate_add_loan_id.py
```
3. Application restart করো

### PythonAnywhere এ:
1. Bash Console খোলো
2. Project directory তে যাও:
```bash
cd ~/Al-insaf
```
3. Migration run করো:
```bash
python migrate_add_loan_id.py
```
4. Web tab এ গিয়ে Reload button ক্লিক করো

### Railway.app এ:
1. Project > Settings > Variables
2. Add command: `python migrate_add_loan_id.py && python run.py`
3. অথবা Console থেকে manually run করো

## কিভাবে কাজ করে

### FIFO Logic:
1. Customer এর সব loans তারিখ অনুযায়ী sort করা হয় (পুরনো আগে)
2. Collection amount দিয়ে প্রথমে পুরনো loan পরিশোধ করা হয়
3. যদি amount বেশি থাকে তাহলে পরের loan এ যায়
4. প্রতিটি collection এর সাথে loan_id save হয়

### Example:
```
Customer এর 3টি loan আছে:
- Loan 1 (Jan 2024): ৳10,000 (বাকি: ৳5,000)
- Loan 2 (Feb 2024): ৳15,000 (বাকি: ৳15,000)
- Loan 3 (Mar 2024): ৳20,000 (বাকি: ৳20,000)

Collection: ৳18,000

Payment distribution:
- Loan 1: ৳5,000 (সম্পূর্ণ পরিশোধ)
- Loan 2: ৳13,000 (বাকি: ৳2,000)
- Loan 3: ৳0 (এখনো শুরু হয়নি)
```

## Changes Made

### 1. Model Update (`models/loan_collection_model.py`):
- Added `loan_id` column
- Added relationship with Loan model

### 2. Collection Logic Update (`app.py`):
- Implemented FIFO algorithm in `collect_loan()` function
- Collections now track which loan they belong to

### 3. Loan Sheet Route (`app.py`):
- `/loan_sheet/<loan_id>` - Individual loan sheet for specific loan
- Shows collections for that specific loan only

## Testing

After migration, test করো:
1. একটি customer এ multiple loans দাও
2. Collection করো
3. Individual Loan Sheet দেখো - এখন সঠিক data দেখাবে
4. পুরনো loan আগে পরিশোধ হচ্ছে কিনা check করো

## Troubleshooting

### Error: "no such column: loan_collections.loan_id"
**Solution:** Migration script run করো:
```bash
python migrate_add_loan_id.py
```

### Individual Loan Sheet এখনো blank
**Solution:** 
1. Browser cache clear করো
2. Application restart করো
3. Database migration সঠিকভাবে হয়েছে কিনা check করো

### Old collections এ loan_id নেই
**Note:** এটা normal। পুরনো collections এ loan_id NULL থাকবে। নতুন collections থেকে সঠিকভাবে track হবে।

## Support

কোনো সমস্যা হলে GitHub issue create করো অথবা developer এর সাথে যোগাযোগ করো।
