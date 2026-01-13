from app import app, db
from models.note_model import Note
from sqlalchemy import text

with app.app_context():
    try:
        # Add columns if they don't exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('notes')]
        
        if 'reminder_date' not in columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE notes ADD COLUMN reminder_date DATETIME'))
                conn.commit()
            print("Added reminder_date column")
        
        if 'is_notified' not in columns:
            with db.engine.connect() as conn:
                conn.execute(text('ALTER TABLE notes ADD COLUMN is_notified BOOLEAN DEFAULT 0'))
                conn.commit()
            print("Added is_notified column")
        
        print("Database updated successfully!")
    except Exception as e:
        print(f"Error: {e}")
