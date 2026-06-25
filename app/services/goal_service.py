from app.extensions import db
from app.models.audit import ReadingGoal
from datetime import datetime

class GoalService:
    """
    Handles Member Reading Goals.
    """

    @staticmethod
    def get_or_create_goal(member_id: int, year: int = None):
        """Fetches the goal for the current year, or creates a default one if it doesn't exist."""
        if not year:
            year = datetime.utcnow().year
            
        goal = ReadingGoal.query.filter_by(member_id=member_id, year=year).first()
        if not goal:
            # Default goal is 10 books per year
            goal = ReadingGoal(member_id=member_id, year=year, target_books=10, books_read=0)
            db.session.add(goal)
            db.session.commit()
            
        return goal

    @staticmethod
    def set_goal(member_id: int, target_books: int, year: int = None):
        """Allows a member to update their target for the year."""
        if not year:
            year = datetime.utcnow().year
            
        goal = GoalService.get_or_create_goal(member_id, year)
        goal.target_books = target_books
        db.session.commit()
        return {"success": True, "goal": goal}

    @staticmethod
    def increment_read_count(member_id: int, year: int = None):
        """Called automatically when a member returns a book!"""
        if not year:
            year = datetime.utcnow().year
            
        goal = GoalService.get_or_create_goal(member_id, year)
        goal.books_read += 1
        db.session.commit()