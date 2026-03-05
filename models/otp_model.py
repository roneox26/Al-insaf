from models.user_model import db
from datetime import datetime, timedelta
import random

class OTP(db.Model):
    __tablename__ = 'otps'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    purpose = db.Column(db.String(50), nullable=False)  # 'admin_settings', 'password_reset', etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    
    user = db.relationship('User', backref='otps')
    
    @staticmethod
    def generate_code():
        """Generate 6-digit OTP"""
        return str(random.randint(100000, 999999))
    
    @staticmethod
    def create_otp(user_id, purpose='admin_settings', validity_minutes=5):
        """Create new OTP"""
        code = OTP.generate_code()
        expires_at = datetime.utcnow() + timedelta(minutes=validity_minutes)
        
        otp = OTP(
            user_id=user_id,
            code=code,
            purpose=purpose,
            expires_at=expires_at
        )
        db.session.add(otp)
        db.session.commit()
        return otp
    
    def is_valid(self):
        """Check if OTP is still valid"""
        return not self.is_used and datetime.utcnow() < self.expires_at
    
    def mark_used(self):
        """Mark OTP as used"""
        self.is_used = True
        db.session.commit()
