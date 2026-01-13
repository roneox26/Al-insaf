from models.user_model import db
from datetime import datetime

class ScheduledExpense(db.Model):
    __tablename__ = 'scheduled_expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    frequency = db.Column(db.String(20), nullable=False)  # daily, weekly, monthly, yearly
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    next_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<ScheduledExpense {self.category} - {self.amount}>'
