from app import app, db, bcrypt, User

with app.app_context():
    # Check if office staff already exists
    office_staff = User.query.filter_by(email='office@example.com').first()
    
    if office_staff:
        print("Office staff already exists!")
        print("Email: office@example.com")
        print("Password: office123")
    else:
        # Create office staff
        hashed_pw = bcrypt.generate_password_hash('office123').decode('utf-8')
        office_staff = User(
            name='Office Staff',
            email='office@example.com',
            password=hashed_pw,
            role='staff',
            is_office_staff=True
        )
        db.session.add(office_staff)
        db.session.commit()
        
        print("Office staff created successfully!")
        print("\nLogin credentials:")
        print("  Email: office@example.com")
        print("  Password: office123")
        print("\nOffice staff can:")
        print("  - View all customers")
        print("  - Add new customers")
        print("  - Collect from all customers")
        print("  - View all daily collections")
