from models_mongodb.user_model import db
from datetime import datetime

class Customer(db.Document):
    name = db.StringField(max_length=100, required=True)
    member_no = db.StringField(max_length=50)
    phone = db.StringField(max_length=20)
    father_husband = db.StringField(max_length=100)
    village = db.StringField(max_length=100)
    post = db.StringField(max_length=100)
    thana = db.StringField(max_length=100)
    district = db.StringField(max_length=100)
    granter = db.StringField(max_length=100)
    profession = db.StringField(max_length=100)
    nid_no = db.StringField(max_length=50)
    admission_fee = db.FloatField(default=0.0)
    welfare_fee = db.FloatField(default=0.0)
    application_fee = db.FloatField(default=0.0)
    address = db.StringField(max_length=200)
    photo = db.StringField(max_length=200)
    staff_id = db.ReferenceField('User')
    total_loan = db.FloatField(default=0.0)
    remaining_loan = db.FloatField(default=0.0)
    savings_balance = db.FloatField(default=0.0)
    created_date = db.DateTimeField(default=datetime.utcnow)
    is_active = db.BooleanField(default=True)
    
    meta = {'collection': 'customers'}
