from app import create_app
from app.extensions import db
from app.models.user import User

# Create an instance of the app so we can talk to the database
app = create_app()

def seed_admin():
    with app.app_context():
        # Check if an admin already exists to prevent duplicates
        existing_admin = User.query.filter_by(email='admin@libra.com').first()
        if existing_admin:
            print("Admin user already exists!")
            return

        # Create the new Admin user
        admin = User(
            name='System Admin',
            email='admin@libra.com',
            role='admin',
            tier='staff'
        )
        # Hash the password securely!
        admin.set_password('admin123') 
        
        # Save to database
        db.session.add(admin)
        db.session.commit()
        
        print("Success! Admin user created.")
        print("Email: admin@libra.com")
        print("Password: admin123")

if __name__ == '__main__':
    seed_admin()