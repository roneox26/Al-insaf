from models_mongodb.user_model import db
from datetime import datetime

class Loan(db.Document):
    customer_id = db.ReferenceField('Customer', required=True)
    amount = db.FloatField(required=True)
    interest_rate = db.FloatField(default=0.0)
    duration_months = db.IntField(default=12)
    installment_amount = db.FloatField(default=0.0)
    remaining_amount = db.FloatField(default=0.0)
    loan_date = db.DateTimeField(default=datetime.utcnow)
    status = db.StringField(max_length=20, default='active')
    
    meta = {'collection': 'loans'}

class LoanCollection(db.Document):
    customer_id = db.ReferenceField('Customer', required=True)
    loan_id = db.ReferenceField('Loan')
    staff_id = db.ReferenceField('User', required=True)
    amount = db.FloatField(required=True)
    collection_date = db.DateTimeField(default=datetime.utcnow)
    
    meta = {'collection': 'loan_collections'}
