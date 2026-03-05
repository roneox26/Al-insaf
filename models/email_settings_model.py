from models.user_model import db
from datetime import datetime

class EmailSettings(db.Model):
    __tablename__ = 'email_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    smtp_server = db.Column(db.String(100), default='smtp.gmail.com')
    smtp_port = db.Column(db.Integer, default=587)
    email = db.Column(db.String(100))
    password = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.now)
    
    @staticmethod
    def get_settings():
        return EmailSettings.query.filter_by(is_active=True).first()
