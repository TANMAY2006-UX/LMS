from app.extensions import db
from app.models.user import User

class MemberService:
    """
    Handles business logic for library members (Users).
    """

    @staticmethod
    def get_all_members():
        """Fetches all users who have the 'member' role."""
        return User.query.filter_by(role='member').order_by(User.joined_date.desc()).all()

    @staticmethod
    def create_member(data: dict):
        """Creates a new library member securely."""
        # 1. Validate if email already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return {"success": False, "error": "An account with this email already exists."}

        # 2. Create the user object
        try:
            new_member = User(
                name=data['name'],
                email=data['email'],
                role='member',               # Hardcoded to 'member' for security 
                tier=data.get('tier', 'student') # Defaults to 'student'
            )
            
            # Use the secure hashing function from our User model
            new_member.set_password(data['password'])
            
            db.session.add(new_member)
            db.session.commit()
            
            return {"success": True, "member": new_member}
            
        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": f"Database error: {str(e)}"}