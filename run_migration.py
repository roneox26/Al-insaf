# -*- coding: utf-8 -*-
"""
Run the loan_id migration
"""
import subprocess
import sys
import os

def run_migration():
    try:
        print("Running loan_id migration...")
        result = subprocess.run([sys.executable, "migrate_add_loan_id.py"], 
                              capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("Migration completed successfully!")
            print(result.stdout)
        else:
            print("Migration failed!")
            print(result.stderr)
            
    except Exception as e:
        print(f"Error running migration: {e}")

if __name__ == "__main__":
    run_migration()