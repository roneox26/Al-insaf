from flask_mongoengine import MongoEngine
from flask_login import UserMixin
from datetime import datetime

db = MongoEngine()

class User(db.Document, UserMixin):
    name = db.StringField(max_length=100)
    email = db.StringField(max_length=100, unique=True, required=True)
    password = db.StringField(max_length=200, required=True)
    role = db.StringField(max_length=20, required=True)
    is_office_staff = db.BooleanField(default=False)
    is_monitor = db.BooleanField(default=False)
    phone = db.StringField(max_length=20)
    address = db.StringField(max_length=200)
    photo = db.StringField(max_length=200)
    join_date = db.DateTimeField(default=datetime.utcnow)
    salary = db.FloatField(default=0.0)
    status = db.StringField(max_length=20, default='active')
    nid = db.StringField(max_length=50)
    plain_password = db.StringField(max_length=100)
    
    meta = {'collection': 'users'}
    
    def get_staff_type(self):
        if self.is_monitor:
            return 'Monitor Staff'
        elif self.is_office_staff:
            return 'Office Staff'
        else:
            return 'Field Staff'
