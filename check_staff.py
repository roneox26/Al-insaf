from app import app, db, User

with app.app_context():
    staff_users = User.query.filter_by(role='staff').all()
    
    print("\n=== All Staff Users ===")
    for user in staff_users:
        is_office = hasattr(user, 'is_office_staff') and user.is_office_staff
        is_monitor = hasattr(user, 'is_monitor') and user.is_monitor
        print(f"\nID: {user.id}")
        print(f"Name: {user.name}")
        print(f"Email: {user.email}")
        print(f"Is Office Staff: {is_office}")
        print(f"Is Monitor: {is_monitor}")
        print("-" * 40)
