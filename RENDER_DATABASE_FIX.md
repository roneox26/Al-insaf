# 🔧 Render.com Database Fix Guide

## ❌ Error যা আসছে:
```
psycopg2.errors.UndefinedColumn: column loan_collections.loan_id does not exist
```

## ✅ সমাধান (Step by Step):

---

### 🚀 পদ্ধতি ১: Render Shell থেকে (RECOMMENDED)

#### Step 1: Render Dashboard এ যান
- https://dashboard.render.com
- আপনার Web Service select করুন (Al-insaf)

#### Step 2: Shell Tab ক্লিক করুন
- উপরের menu তে "Shell" tab দেখবেন
- ক্লিক করলে একটি terminal খুলবে

#### Step 3: এই command run করুন:
```bash
python fix_render_database.py
```

**অথবা simple version:**
```bash
python simple_db_fix.py
```

#### Step 4: Service Restart করুন
- Shell থেকে বের হয়ে আসুন
- "Manual Deploy" dropdown > "Clear build cache & deploy" ক্লিক করুন
- **অথবা** Settings tab > "Restart Service" button

#### Step 5: Test করুন
- আপনার site এ যান
- Customer Details page test করুন
- Loan Sheet দেখুন

---

### 🗄️ পদ্ধতি ২: Direct SQL (যদি Shell কাজ না করে)

#### Step 1: Database Connect করুন
1. Render Dashboard > আপনার PostgreSQL database select করুন
2. "Info" tab এ "External Database URL" copy করুন
3. অথবা "Connect" button ক্লিক করুন

#### Step 2: psql দিয়ে connect করুন
```bash
psql <your-database-url>
```

#### Step 3: এই SQL command run করুন:
```sql
-- Check current columns
\d loan_collections

-- Add loan_id column
ALTER TABLE loan_collections ADD COLUMN loan_id INTEGER;

-- Verify
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name='loan_collections' AND column_name='loan_id';

-- Exit
\q
```

#### Step 4: Service Restart করুন

---

### 🔄 পদ্ধতি ৩: Environment Variable দিয়ে

#### Render Dashboard এ:
1. Settings tab > Environment
2. Add Environment Variable:
   - Key: `RUN_MIGRATION`
   - Value: `true`
3. Save Changes (auto restart হবে)
4. Migration complete হলে variable টি remove করুন

---

## 🔍 Troubleshooting

### যদি "Module not found" error আসে:
```bash
# Shell এ run করুন:
pip install -r requirements.txt
python fix_render_database.py
```

### যদি "Permission denied" error আসে:
```bash
# Shell এ run করুন:
chmod +x fix_render_database.py
python fix_render_database.py
```

### যদি Database connection fail করে:
```bash
# Check database URL:
echo $DATABASE_URL

# Test connection:
python -c "from app import db; print(db.engine.url)"
```

### Manual SQL যদি কাজ না করে:
```sql
-- Check if table exists
SELECT table_name FROM information_schema.tables WHERE table_name='loan_collections';

-- Check current structure
SELECT column_name, data_type FROM information_schema.columns WHERE table_name='loan_collections';

-- Add column with explicit NULL
ALTER TABLE loan_collections ADD COLUMN IF NOT EXISTS loan_id INTEGER NULL;
```

---

## ✅ Verification (Fix হয়েছে কিনা check করুন)

### Shell থেকে verify:
```bash
python -c "from app import app, db; from sqlalchemy import inspect; app.app_context().push(); inspector = inspect(db.engine); print([col['name'] for col in inspector.get_columns('loan_collections')])"
```

### এই URLs test করুন:
1. `/customer/details/1` - Customer Details
2. `/customer/loan_sheet/1` - Loan Sheet
3. `/manage_loans` - Manage Loans
4. `/loan_customers` - Loan Customers

---

## 📝 কেন এই Error আসছে?

1. **Local SQLite** database এ `loan_id` column আছে
2. **Render PostgreSQL** database এ নেই
3. Migration script deploy এর সময় run হয়নি
4. Model update হয়েছে কিন্তু database update হয়নি

---

## 🆘 এখনো Problem হলে

### Logs Check করুন:
```bash
# Render Dashboard > Logs tab
# অথবা Shell থেকে:
tail -f /var/log/render.log
```

### Database Reset (LAST RESORT - সব data মুছে যাবে!):
```bash
# Shell এ:
python create_db.py
```

⚠️ **Warning:** এটা করলে সব data মুছে যাবে!

---

## 📞 Support

যদি কোন সমস্যা হয়:
1. GitHub issue তৈরি করুন: https://github.com/roneox26/Al-insaf/issues
2. Error message এর screenshot দিন
3. Render logs share করুন

---

## 🎯 Quick Commands Summary

```bash
# Method 1: Python script
python fix_render_database.py

# Method 2: Simple script
python simple_db_fix.py

# Method 3: Direct SQL
psql $DATABASE_URL -c "ALTER TABLE loan_collections ADD COLUMN loan_id INTEGER;"

# Verify
python -c "from app import db; from sqlalchemy import inspect; print([c['name'] for c in inspect(db.engine).get_columns('loan_collections')])"

# Restart
# Use Render Dashboard UI
```
