from datetime import datetime
from app import db

class FollowUp(db.Model):
    __tablename__ = 'followups'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    follow_date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    next_follow_date = db.Column(db.DateTime)
    status = db.Column(db.String(50), default='pending')  # pending, completed, failed
    method = db.Column(db.String(50))  # call, visit, sms, whatsapp
    notes = db.Column(db.Text)
    amount_promised = db.Column(db.Float, default=0)
    amount_collected = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    customer = db.relationship('Customer', backref='followups')
    staff = db.relationship('User', backref='followups')
    
    def __repr__(self):
        return f'<FollowUp {self.customer_id} - {self.status}>'
