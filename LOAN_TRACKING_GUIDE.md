# লোন ট্র্যাকিং সিস্টেম আপডেট গাইড

## কি পরিবর্তন হয়েছে?

এখন প্রতিটি collection এর সাথে loan_id track করা হবে। এতে:
- একজন customer কে একাধিক বার লোন দেওয়া যাবে
- প্রতিটি লোনের আলাদা collection history থাকবে
- একটা লোন শোধ হলে নতুন লোন দেওয়া যাবে

## Setup করার নিয়ম:

### ১. Database Update করুন:
```bash
python add_loan_id_to_collections.py
```

এটি:
- loan_collections টেবিলে loan_id column যোগ করবে
- পুরাতন collections গুলোতে automatically loan_id assign করবে

### ২. App Restart করুন:
```bash
python run.py
```

## কিভাবে কাজ করবে?

### নতুন লোন দেওয়ার সময়:
1. Customer এর remaining_loan = 0 হলে নতুন লোন দিতে পারবেন
2. অথবা পুরাতন লোন চলমান থাকলেও নতুন লোন দিতে পারবেন

### Collection করার সময়:
1. System automatically সবচেয়ে নতুন active loan খুঁজে বের করবে
2. সেই loan এর জন্য collection record করবে
3. Customer এর remaining_loan কমবে

### Customer Loan Sheet এ:
1. সব loans এর তথ্য দেখাবে
2. প্রতিটি loan এর আলাদা collection history দেখাবে
3. কোন loan কত টাকা বাকি আছে সেটা দেখাবে

## ভবিষ্যতে আরও উন্নতি:

যদি আপনি চান যে:
- একাধিক active loan একসাথে চলবে
- নির্দিষ্ট loan এর জন্য collection করা যাবে
- Loan-wise বিস্তারিত report দেখা যাবে

তাহলে আরও কিছু পরিবর্তন করতে হবে। আমাকে জানান!

## সমস্যা হলে:

যদি কোনো error আসে, তাহলে:
1. Database backup নিন
2. আমাকে error message দেখান
3. আমি ঠিক করে দেব

---
তৈরি করেছেন: Amazon Q
