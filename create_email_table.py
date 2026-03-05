from app import app, db
from models.email_settings_model import EmailSettings

with app.app_context():
    db.create_all()
    print('Email settings table created!')
