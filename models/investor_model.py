from models.user_model import db
from datetime import datetime

class Investor(db.Model):
    __tablename__ = 'investors'
    id = db.Column(db.Integer, primary_key=True)
    investor_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    total_investment = db.Column(db.Float, default=0)
    total_withdrawal = db.Column(db.Float, default=0)
    current_balance = db.Column(db.Float, default=0)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    investments = db.relationship('Investment', backref='investor', lazy=True)
    withdrawals = db.relationship('Withdrawal', backref='investor', lazy=True)
