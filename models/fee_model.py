from models.user_model import db
from datetime import datetime

class FeeCollection(db.Model):
    __tablename__ = 'fee_collections'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    fee_type = db.Column(db.String(50), nullable=False)  # 'admission', 'welfare', 'application'
    amount = db.Column(db.Float, nullable=False)
    collection_date = db.Column(db.DateTime, default=datetime.utcnow)
    collected_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    note = db.Column(db.String(200))
    
    customer = db.relationship('Customer', backref='fee_collections')
    collector = db.relationship('User', backref='fee_collections')
