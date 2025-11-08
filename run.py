from app import app, db, bcrypt, User, CashBalance

with app.app_context():
    db.create_all()
    
    if not User.query.filter_by(email='admin@example.com').first():
        hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = User(name='Admin', email='admin@example.com', password=hashed_pw, role='admin')
        db.session.add(admin)
    
    if not User.query.filter_by(email='staff@example.com').first():
        hashed_pw = bcrypt.generate_password_hash('staff123').decode('utf-8')
        staff = User(name='Staff', email='staff@example.com', password=hashed_pw, role='staff')
        db.session.add(staff)
    
    db.session.commit()
    
    if not CashBalance.query.first():
        initial_balance = CashBalance(balance=0)
        db.session.add(initial_balance)
        db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
