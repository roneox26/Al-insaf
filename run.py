import os
from app import app as application, db, bcrypt, User, CashBalance

def init_db():
    """Initialize database with default data"""
    try:
        with application.app_context():
            # Create tables
            db.create_all()
            
            # Add default admin user
            if not User.query.filter_by(email='admin@example.com').first():
                hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
                admin = User(name='Admin', email='admin@example.com', password=hashed_pw, role='admin')
                db.session.add(admin)
            
            # Add default staff user
            if not User.query.filter_by(email='staff@example.com').first():
                hashed_pw = bcrypt.generate_password_hash('staff123').decode('utf-8')
                staff = User(name='Staff', email='staff@example.com', password=hashed_pw, role='staff')
                db.session.add(staff)
            
            db.session.commit()
            
            # Initialize cash balance
            if not CashBalance.query.first():
                initial_balance = CashBalance(balance=0)
                db.session.add(initial_balance)
                db.session.commit()
                
            print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")
        import traceback
        traceback.print_exc()

# Initialize database on first request
@application.before_request
def initialize_database():
    """Initialize database on first request"""
    if not hasattr(application, '_db_initialized'):
        init_db()
        application._db_initialized = True

# For backwards compatibility
app = application

if __name__ == '__main__':
    # Initialize database when running directly
    init_db()
    application.run(host='0.0.0.0', port=5000, debug=False)
