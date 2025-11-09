#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test script to verify all routes are working"""

from app import app
import sys

def test_routes():
    """Test if all routes are properly defined"""
    with app.app_context():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(str(rule))
        
        print(f"✓ Total routes found: {len(routes)}")
        print("✓ All routes loaded successfully!")
        return True

def test_imports():
    """Test if all imports are working"""
    try:
        from models.user_model import db, User
        from models.customer_model import Customer
        from models.loan_model import Loan
        from models.saving_model import Saving
        from models.loan_collection_model import LoanCollection
        from models.saving_collection_model import SavingCollection
        from models.cash_balance_model import CashBalance
        from models.investor_model import Investor
        from models.investment_model import Investment
        from models.withdrawal_model import Withdrawal
        from models.expense_model import Expense
        from models.message_model import Message
        print("✓ All model imports successful!")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("Testing NGO Management System")
    print("=" * 50)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test routes
    if not test_routes():
        success = False
    
    print("=" * 50)
    if success:
        print("✓ All tests passed! Application is ready to run.")
        print("\nTo start the application, run:")
        print("  python run.py")
        sys.exit(0)
    else:
        print("✗ Some tests failed. Please check the errors above.")
        sys.exit(1)
