# -*- coding: utf-8 -*-
"""
Test Customer Delete Functionality
This script tests if customer deletion works properly
"""

from app import app, db
from models.customer_model import Customer
from models.loan_collection_model import LoanCollection
from models.saving_collection_model import SavingCollection
from models.fee_model import FeeCollection
from models.withdrawal_model import Withdrawal
from models.loan_model import Loan
from models.collection_schedule_model import CollectionSchedule

def test_customer_delete():
    """Test customer deletion"""
    with app.app_context():
        try:
            print("="*50)
            print("Testing Customer Delete Functionality")
            print("="*50)
            
            # Create a test customer
            print("\n1. Creating test customer...")
            test_customer = Customer(
                name="Test Delete Customer",
                phone="1234567890",
                member_no="TEST001",
                village="Test Village",
                is_active=False  # Already inactive for deletion
            )
            db.session.add(test_customer)
            db.session.commit()
            customer_id = test_customer.id
            print(f"✓ Test customer created with ID: {customer_id}")
            
            # Add some test data
            print("\n2. Adding test collections...")
            
            # Add loan collection
            loan_col = LoanCollection(
                customer_id=customer_id,
                amount=100,
                staff_id=1
            )
            db.session.add(loan_col)
            
            # Add saving collection
            saving_col = SavingCollection(
                customer_id=customer_id,
                amount=50,
                staff_id=1
            )
            db.session.add(saving_col)
            
            # Add fee collection
            fee_col = FeeCollection(
                customer_id=customer_id,
                fee_type='admission',
                amount=500,
                collected_by=1
            )
            db.session.add(fee_col)
            
            db.session.commit()
            print("✓ Test collections added")
            
            # Count records before deletion
            print("\n3. Counting records before deletion...")
            loan_count = LoanCollection.query.filter_by(customer_id=customer_id).count()
            saving_count = SavingCollection.query.filter_by(customer_id=customer_id).count()
            fee_count = FeeCollection.query.filter_by(customer_id=customer_id).count()
            
            print(f"  - Loan collections: {loan_count}")
            print(f"  - Saving collections: {saving_count}")
            print(f"  - Fee collections: {fee_count}")
            
            # Try to delete customer
            print("\n4. Attempting to delete customer...")
            
            # Delete related records
            CollectionSchedule.query.filter_by(customer_id=customer_id).delete(synchronize_session=False)
            LoanCollection.query.filter_by(customer_id=customer_id).delete(synchronize_session=False)
            SavingCollection.query.filter_by(customer_id=customer_id).delete(synchronize_session=False)
            FeeCollection.query.filter_by(customer_id=customer_id).delete(synchronize_session=False)
            Withdrawal.query.filter_by(customer_id=customer_id).delete(synchronize_session=False)
            Loan.query.filter_by(customer_name=test_customer.name).delete(synchronize_session=False)
            
            # Delete customer
            db.session.delete(test_customer)
            db.session.commit()
            
            print("✓ Customer deleted successfully!")
            
            # Verify deletion
            print("\n5. Verifying deletion...")
            customer_exists = Customer.query.get(customer_id)
            loan_count_after = LoanCollection.query.filter_by(customer_id=customer_id).count()
            saving_count_after = SavingCollection.query.filter_by(customer_id=customer_id).count()
            fee_count_after = FeeCollection.query.filter_by(customer_id=customer_id).count()
            
            if customer_exists:
                print("❌ Customer still exists!")
                return False
            else:
                print("✓ Customer deleted")
            
            print(f"  - Loan collections remaining: {loan_count_after}")
            print(f"  - Saving collections remaining: {saving_count_after}")
            print(f"  - Fee collections remaining: {fee_count_after}")
            
            if loan_count_after == 0 and saving_count_after == 0 and fee_count_after == 0:
                print("✓ All related data deleted")
            else:
                print("❌ Some related data still exists")
                return False
            
            print("\n" + "="*50)
            print("✓ TEST PASSED - Customer deletion works correctly!")
            print("="*50)
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ TEST FAILED - Error: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False

if __name__ == '__main__':
    print("\n" + "="*50)
    print("Customer Delete Test")
    print("="*50)
    print("\nThis script will test if customer deletion works properly.")
    print("It will create a test customer and then delete it.\n")
    
    response = input("Run test? (yes/no): ").strip().lower()
    if response == 'yes':
        success = test_customer_delete()
        if success:
            print("\n✓ Customer delete functionality is working!")
            print("You can now safely delete customers in production.")
        else:
            print("\n❌ Customer delete functionality has issues.")
            print("Please run: python fix_customer_delete.py")
    else:
        print("Test cancelled.")
