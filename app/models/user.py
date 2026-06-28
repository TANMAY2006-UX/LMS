
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.extensions import login_manager

# We inherit from db.Model (to map to Postgres)
# UserMixin (to handle Flask-Login sessions automatically)
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # Admin / Librarian / Member
    role = db.Column(db.String(20), nullable=False)

    # Tiers for Fine_Policy (Only applies to 'member' role)
    tier = db.Column(db.String(20), nullable=True)

    is_active = db.Column(db.Boolean, default=True)
    joined_date = db.Column(db.Date, default=datetime.utcnow)
    must_change_password = db.Column(db.Boolean, default=False)

    __table_args__ = (
        # Check for Roles & Tiers
        db.CheckConstraint("role IN ('admin', 'librarian', 'member')", name='chk_users_role'),
        db.CheckConstraint("tier IS NULL OR tier IN ('student', 'faculty', 'staff')", name='chk_users_tier'),
    )

    # Hashes the password before saving it to the database.
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    # Checks if the provided password matches the hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # repr - representation function... Basically returning the name and role as to easy debug
    def __repr__(self):
        return f"<User {self.name} ({self.role})>"

    # This function tells Flask-Login how to load a user object from the session ID
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    

