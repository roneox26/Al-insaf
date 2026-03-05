from models_mongodb.user_model import db
from datetime import datetime

class Saving(db.Document):
    customer_id = db.ReferenceField('Customer', required=True)
    amount = db.FloatField(required=True)
    saving_date = db.DateTimeField(default=datetime.utcnow)
    
    meta = {'collection': 'savings'}

class SavingCollection(db.Document):
    customer_id = db.ReferenceField('Customer', required=True)
    staff_id = db.ReferenceField('User', required=True)
    amount = db.FloatField(required=True)
    collection_date = db.DateTimeField(default=datetime.utcnow)
    
    meta = {'collection': 'saving_collections'}
