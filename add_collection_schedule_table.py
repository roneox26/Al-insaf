# -*- coding: utf-8 -*-
# Migration script to add collection_schedule table
from app import app, db

with app.app_context():
    # Import all models first
    from models.customer_model import Customer
    from models.collection_schedule_model import CollectionSchedule
    
    # This will create the table if it doesn't exist
    db.create_all()
    
    print("✅ Collection Schedule table created successfully!")
    print("\n📅 Collection Schedule System is now ready!")
    print("\nAccess it at: /collection_schedule")
