from models.user_model import db
from datetime import datetime

class Investment(db.Model):
    __tablename__ = 'investments'
    id = db.Column(db.Integer, primary_key=True)
    investor_id = db.Column(db.Integer, db.ForeignKey('investors.id', ondelete='CASCADE'), nullable=False)
    investor_name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    note = db.Column(db.String(200))
