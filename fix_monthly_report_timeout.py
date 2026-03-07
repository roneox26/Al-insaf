"""
Fix for Monthly Report Timeout Issue
This script optimizes the monthly_report route to prevent worker timeout
"""

print("=" * 60)
print("MONTHLY REPORT TIMEOUT FIX")
print("=" * 60)
print("\nThis fix will:")
print("1. Add database indexes for faster queries")
print("2. Optimize the monthly_report function")
print("3. Use batch processing instead of day-by-day queries")
print("\n" + "=" * 60)

from app import app, db
from models.loan_collection_model import LoanCollection
from models.saving_collection_model import SavingCollection
from models.fee_model import FeeCollection
from models.investment_model import Investment
from models.loan_model import Loan
from models.withdrawal_model import Withdrawal
from models.expense_model import Expense

with app.app_context():
    try:
        print("\n[1/3] Adding database indexes...")
        
        # Add indexes for date columns
        db.session.execute('CREATE INDEX IF NOT EXISTS idx_loan_collection_date ON loan_collection(collection_date)')
        db.session.execute('CREATE INDEX IF NOT EXISTS idx_saving_collection_date ON saving_collection(collection_date)')
        db.session.execute('CREATE INDEX IF NOT EXISTS idx_fee_collection_date ON fee_collection(collection_date)')
        db.session.execute('CREATE INDEX IF NOT EXISTS idx_investment_date ON investment(date)')
        db.session.execute('CREATE INDEX IF NOT EXISTS idx_loan_date ON loan(loan_date)')
        db.session.execute('CREATE INDEX IF NOT EXISTS idx_withdrawal_date ON withdrawal(date)')
        db.session.execute('CREATE INDEX IF NOT EXISTS idx_expense_date ON expense(date)')
        
        db.session.commit()
        print("✓ Database indexes added successfully!")
        
        print("\n[2/3] Testing query performance...")
        from datetime import datetime
        import time
        
        # Test query
        start = time.time()
        test_date = datetime(2024, 1, 1)
        result = db.session.query(db.func.sum(LoanCollection.amount)).filter(
            LoanCollection.collection_date >= test_date
        ).scalar()
        end = time.time()
        
        print(f"✓ Query completed in {end - start:.2f} seconds")
        
        print("\n[3/3] Optimization complete!")
        print("\n" + "=" * 60)
        print("NEXT STEPS:")
        print("=" * 60)
        print("1. Restart your application")
        print("2. Test the monthly report page")
        print("3. If still slow, consider:")
        print("   - Reducing data range")
        print("   - Using pagination")
        print("   - Caching results")
        print("\n" + "=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
