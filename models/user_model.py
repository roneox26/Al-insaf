from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(20))  # "admin" or "staff"
    is_office_staff = db.Column(db.Boolean, default=False)
    is_monitor = db.Column(db.Boolean, default=False)
    
    # Staff Details
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    photo = db.Column(db.String(200))
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    salary = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='active')  # active, inactive
    nid = db.Column(db.String(50))
    plain_password = db.Column(db.String(100))  # Store plain password for admin view
    
    def get_staff_type(self):
        if self.is_monitor:
            return 'Monitor Staff'
        elif self.is_office_staff:
            return 'Office Staff'
        else:
            return 'Field Staff'
