# পুরাতন Data Import করার নির্দেশনা

## 🎯 পুরাতন Data Import করার ৩টি পদ্ধতি

### ১. Web Interface দিয়ে (সবচেয়ে সহজ) ✅

1. Admin হিসেবে Login করুন
2. Dashboard থেকে **"পুরাতন Data Import"** button এ ক্লিক করুন
3. দুইটি form পাবেন:
   - **পুরাতন Customer যোগ করুন**: Customer এর সব তথ্য দিয়ে add করুন
   - **পুরাতন Collection যোগ করুন**: Customer select করে collection add করুন

**সুবিধা:**
- সবচেয়ে সহজ
- কোনো technical knowledge লাগবে না
- একটা একটা করে data add করতে পারবেন

---

### ২. Python Script দিয়ে (Bulk Import)

যদি অনেক data একসাথে import করতে চান:

#### Step 1: CSV File তৈরি করুন

`old_customers.csv` নামে একটি file তৈরি করুন:

```csv
name,phone,member_no,village,address,total_loan,remaining_loan,savings_balance
রহিম উদ্দিন,01712345678,M001,মিরপুর,ঢাকা,50000,30000,5000
করিম মিয়া,01812345679,M002,উত্তরা,ঢাকা,30000,20000,3000
```

#### Step 2: Script Edit করুন

`import_old_data.py` file খুলুন এবং নিচের code uncomment করুন:

```python
if __name__ == '__main__':
    # CSV থেকে import করুন
    import_from_csv('old_customers.csv')
```

#### Step 3: Run করুন

```bash
python import_old_data.py
```

---

### ৩. Manual Script দিয়ে (Custom Data)

যদি specific data add করতে চান:

#### `import_old_data.py` file edit করুন:

```python
if __name__ == '__main__':
    # Example: একটি customer add করুন
    customer_id = add_old_customer(
        name="রহিম উদ্দিন",
        phone="01712345678",
        member_no="M001",
        village="মিরপুর",
        total_loan=50000,
        remaining_loan=30000,
        savings_balance=5000,
        created_date=datetime(2023, 1, 15)  # পুরাতন তারিখ
    )
    
    # Loan add করুন
    add_old_loan(
        customer_id=customer_id,
        amount=50000,
        interest=10,
        loan_date=datetime(2023, 1, 20),
        installment_count=50,
        installment_amount=1100,
        installment_type='Weekly'
    )
    
    # Collection add করুন
    add_old_collection(
        customer_id=customer_id,
        loan_amount=1100,
        saving_amount=100,
        collection_date=datetime(2023, 1, 27)
    )
```

#### Run করুন:

```bash
python import_old_data.py
```

---

## 📋 CSV Template

`old_customers_template.csv` file এ একটি template আছে। এটা copy করে নিজের data দিয়ে fill করুন।

### CSV Format:

| Column | Description | Example |
|--------|-------------|---------|
| name | Customer এর নাম | রহিম উদ্দিন |
| phone | ফোন নম্বর | 01712345678 |
| member_no | সদস্য নং | M001 |
| village | গ্রাম | মিরপুর |
| address | ঠিকানা | ঢাকা |
| total_loan | মোট লোন | 50000 |
| remaining_loan | বাকি লোন | 30000 |
| savings_balance | সঞ্চয় | 5000 |

---

## ⚠️ গুরুত্বপূর্ণ নোট

1. **তারিখ Format**: `YYYY-MM-DD` (যেমন: 2023-01-15)
2. **Staff ID**: যদি staff_id না দেন, তাহলে current user এর ID use হবে
3. **Cash Balance**: Customer এর savings_balance automatically cash balance এ যোগ হবে
4. **Backup**: Import করার আগে database এর backup নিন

---

## 🔧 Troubleshooting

### Error: "Customer ID not found"
- প্রথমে customer add করুন, তারপর loan/collection add করুন

### Error: "CSV file not found"
- CSV file টি `ngo` folder এ রাখুন
- File path সঠিক আছে কিনা check করুন

### Error: "Database locked"
- Application বন্ধ করুন
- Script run করুন
- Application আবার চালু করুন

---

## 📞 Support

কোনো সমস্যা হলে GitHub এ issue create করুন।

---

**✅ সফলভাবে Import হলে Dashboard এ সব data দেখতে পাবেন!**
