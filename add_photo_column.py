from app import app, db
from models.customer_model import Customer

with app.app_context():
    try:
        with db.engine.connect() as conn:
            conn.execute(db.text("ALTER TABLE customers ADD COLUMN photo VARCHAR(200)"))
            conn.commit()
        print("Photo column added successfully!")
    except Exception as e:
        if "duplicate column name" in str(e).lower():
            print("Photo column already exists!")
        else:
            print(f"Error: {e}")
