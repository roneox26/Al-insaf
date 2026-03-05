from models_mongodb.user_model import db
from datetime import datetime

class CashBalance(db.Document):
    balance = db.FloatField(default=0.0)
    last_updated = db.DateTimeField(default=datetime.utcnow)
    
    meta = {'collection': 'cash_balance'}

class Investor(db.Document):
    name = db.StringField(max_length=100, required=True)
    phone = db.StringField(max_length=20)
    address = db.StringField(max_length=200)
    total_investment = db.FloatField(default=0.0)
    created_date = db.DateTimeField(default=datetime.utcnow)
    
    meta = {'collection': 'investors'}

class Investment(db.Document):
    investor_id = db.ReferenceField('Investor', required=True)
    amount = db.FloatField(required=True)
    investment_date = db.DateTimeField(default=datetime.utcnow)
    
    meta = {'collection': 'investments'}

class Expense(db.Document):
    title = db.StringField(max_length=200, required=True)
    amount = db.FloatField(required=True)
    category = db.StringField(max_length=100)
    expense_date = db.DateTimeField(default=datetime.utcnow)
    created_by = db.ReferenceField('User')
    
    meta = {'collection': 'expenses'}

class Withdrawal(db.Document):
    customer_id = db.ReferenceField('Customer', required=True)
    amount = db.FloatField(required=True)
    withdrawal_date = db.DateTimeField(default=datetime.utcnow)
    approved_by = db.ReferenceField('User')
    
    meta = {'collection': 'withdrawals'}
