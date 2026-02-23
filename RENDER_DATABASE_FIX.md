# 🔧 Render.com Database Fix Guide

## ❌ Error যা আসছে:
```
psycopg2.errors.UndefinedColumn: column loan_collections.loan_id does not exist
```

## ✅ সমাধান (3টি পদ্ধতি):

---

### 🚀 পদ্ধতি ১: Render Shell থেকে (সবচেয়ে সহজ)

1. **Render Dashboard এ যান**
   - https://dashboard.render.com
   - আপনার Web Service select করুন

2. **Shell Tab এ ক্লিক করুন**
   - উপরের menu তে "Shell" tab খুঁজুন

3. **এই command run করুন:**
   ```bash
   python fix_render_database.py
   ```

4. **Application Restart করুন**
   - "Manual Deploy" > "Clear build cache & deploy" ক্লিক করুন
   - অথবা Settings > "Restart Service" ক্লিক করুন

---

### 🔄 পদ্ধতি ২: Migration Script দিয়ে

1. **Render Shell এ যান**

2. **Migration run করুন:**
   ```bash
   python migrate_add_loan_id.py
   ```

3. **Service Restart করুন**

---

### 🗄️ পদ্ধতি ৩: Manual SQL (Advanced)

1. **Render Dashboard > Database tab এ যান**

2. **"Connect" button ক্লিক করে psql access নিন**

3. **এই SQL commands run করুন:**
   ```sql
   -- Check if column exists
   SELECT column_name 
   FROM information_schema.columns 
   WHERE table_name='loan_collections' AND column_name='loan_id';

   -- Add loan_id column
   ALTER TABLE loan_collections 
   ADD COLUMN loan_id INTEGER;

   -- Add foreign key
   ALTER TABLE loan_collections 
   ADD CONSTRAINT fk_loan_collections_loan_id 
   FOREIGN KEY (loan_id) REFERENCES loans(id);
   ```

4. **Service Restart করুন**

---

## 📝 কেন এই Error আসছে?

- Local SQLite database এ `loan_id` column আছে
- কিন্তু Render.com এর PostgreSQL database এ নেই
- Migration script run করা হয়নি

## ✅ Fix হয়েছে কিনা Check করুন

Fix করার পরে এই URL গুলো test করুন:
- `/customer/details/<id>` - Customer Details page
- `/customer/loan_sheet/<id>` - Individual Loan Sheet
- `/manage_loans` - Manage Loans page

## 🆘 এখনো Problem হলে

1. **Logs check করুন:**
   - Render Dashboard > Logs tab

2. **Database connection check করুন:**
   ```bash
   python -c "from app import db; print(db.engine.url)"
   ```

3. **Table structure check করুন:**
   ```bash
   python -c "from app import db, LoanCollection; print(LoanCollection.__table__.columns.keys())"
   ```

---

## 📞 Support

যদি কোন সমস্যা হয়, GitHub issue তৈরি করুন:
https://github.com/roneox26/Al-insaf/issues
