"""
Migration script to update Message table for two-way messaging
Run this once to migrate existing messages
"""

from app import app, db
from models.message_model import Message
from models.user_model import User
from sqlalchemy import text

def migrate_messages():
    with app.app_context():
        try:
            print("Starting message table migration...")
            
            # Check if columns exist
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('messages')]
            
            # Add new columns if they don't exist
            if 'sender_id' not in columns:
                print("Adding sender_id column...")
                db.engine.execute(text('ALTER TABLE messages ADD COLUMN sender_id INTEGER'))
            
            if 'receiver_id' not in columns:
                print("Adding receiver_id column...")
                db.engine.execute(text('ALTER TABLE messages ADD COLUMN receiver_id INTEGER'))
            
            # Get admin user
            admin = User.query.filter_by(role='admin').first()
            if not admin:
                print("No admin found! Creating default admin...")
                from flask_bcrypt import Bcrypt
                bcrypt = Bcrypt(app)
                hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
                admin = User(name='Admin', email='admin@example.com', password=hashed_pw, role='admin')
                db.session.add(admin)
                db.session.commit()
            
            # Migrate existing messages (old messages were from admin to staff)
            print("Migrating existing messages...")
            messages = db.session.execute(text('SELECT * FROM messages WHERE sender_id IS NULL')).fetchall()
            
            for msg in messages:
                # Old format: admin sent to staff_id
                db.session.execute(
                    text('UPDATE messages SET sender_id = :admin_id, receiver_id = :staff_id WHERE id = :msg_id'),
                    {'admin_id': admin.id, 'staff_id': msg.staff_id, 'msg_id': msg.id}
                )
            
            db.session.commit()
            print(f"✅ Migration completed! Migrated {len(messages)} messages.")
            
            # Optional: Remove old staff_id column (commented out for safety)
            # print("Removing old staff_id column...")
            # db.engine.execute(text('ALTER TABLE messages DROP COLUMN staff_id'))
            
            print("✅ Message system upgraded successfully!")
            
        except Exception as e:
            print(f"❌ Migration error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    migrate_messages()
