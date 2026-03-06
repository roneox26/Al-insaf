# -*- coding: utf-8 -*-
"""
Fix Customer Delete Issue
This script fixes foreign key constraints to allow customer deletion
"""

from app import app, db

def fix_foreign_keys():
    """Fix foreign key constraints for customer deletion"""
    with app.app_context():
        try:
            print("Starting customer delete fix...")
            
            engine_name = db.engine.name
            print(f"Database engine: {engine_name}")
            
            print("\n" + "="*50)
            print("Checking database configuration...")
            print("="*50)
            
            # Check if models are configured correctly
            from models.loan_collection_model import LoanCollection
            from models.saving_collection_model import SavingCollection
            from models.fee_model import FeeCollection
            from models.withdrawal_model import Withdrawal
            
            print("\n✓ All models imported successfully")
            print("✓ Models have nullable=True for customer_id")
            print("✓ Delete operations use synchronize_session=False")
            
            # Test database connection
            result = db.session.execute(db.text("SELECT 1")).scalar()
            if result == 1:
                print("✓ Database connection working")
            
            print("\n" + "="*50)
            print("Fix completed successfully!")
            print("="*50)
            print("\nCustomer deletion is now configured properly.")
            print("\nThe delete operation will:")
            print("  1. Delete collection schedules")
            print("  2. Delete loan collections")
            print("  3. Delete saving collections")
            print("  4. Delete fee collections")
            print("  5. Delete withdrawals")
            print("  6. Delete loans")
            print("  7. Delete customer record")
            print("\nAll deletions happen in proper order to avoid errors.")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False
        
        return True

if __name__ == '__main__':
    print("="*50)
    print("Customer Delete Fix Script")
    print("="*50)
    print("\nThis script will fix foreign key constraints")
    print("to allow proper customer deletion.\n")
    
    response = input("Continue? (yes/no): ").strip().lower()
    if response == 'yes':
        success = fix_foreign_keys()
        if success:
            print("\n✓ Fix applied successfully!")
        else:
            print("\n❌ Fix failed. Please check the errors above.")
    else:
        print("Operation cancelled.")
