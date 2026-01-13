from app import app, db
from models.scheduled_expense_model import ScheduledExpense

with app.app_context():
    db.create_all()
    print("Database updated with scheduled_expenses table!")
