# -*- coding: utf-8 -*-
from models.user_model import db
from datetime import datetime

class CollectionSchedule(db.Model):
    __tablename__ = 'collection_schedule'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, nullable=False)
    loan_id = db.Column(db.Integer, nullable=True)
    scheduled_date = db.Column(db.DateTime, nullable=False)
    expected_amount = db.Column(db.Float, default=0)
    collection_type = db.Column(db.String(20), default='loan')
    status = db.Column(db.String(20), default='pending')
    collected_amount = db.Column(db.Float, default=0)
    collected_date = db.Column(db.DateTime, nullable=True)
    staff_id = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return f'<CollectionSchedule {self.customer_id} - {self.scheduled_date}>'
