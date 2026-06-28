from app.extensions import db
from app.models.transaction import Transaction
from app.models.book import Book, BookCopy
from sqlalchemy import func

class AnalyticsService:
    """
    Handles data crunching, recommendations, and reporting.
    Separated from basic CRUD services to keep the architecture clean.
    """

    @staticmethod
    def get_coborrowing_recommendations(target_book_id: int, limit: int = 4):
        """
        Hybrid Recommendation Engine:
        1. Collaborative Filtering (People who borrowed this also borrowed...)
        2. Content Boost (+50% score if it's in the same category)
        3. Cold-Start Fallback (Most popular in the same category)
        """
        target_book = Book.query.get(target_book_id)
        if not target_book:
            return []

        # Step 1: Find all member IDs who have ever borrowed the target book
        borrowers_subquery = db.session.query(Transaction.member_id).join(
            BookCopy, Transaction.copy_id == BookCopy.id
        ).filter(
            BookCopy.book_id == target_book_id
        ).subquery()

        # Step 2: Get co-borrowed books and their raw borrow counts
        co_borrowed = db.session.query(
            Book, func.count(Transaction.id).label('borrow_count')
        ).join(
            BookCopy, Book.id == BookCopy.book_id
        ).join(
            Transaction, Transaction.copy_id == BookCopy.id
        ).filter(
            Transaction.member_id.in_(borrowers_subquery),
            Book.id != target_book_id  # Exclude the target book itself
        ).group_by(
            Book.id
        ).all()

        # Step 3: Apply the Hybrid Scoring Algorithm (Category Boost)
        scored_books = []
        for book, borrow_count in co_borrowed:
            # 50% score boost if the recommended book is in the same genre!
            score = borrow_count * 1.5 if book.category_id == target_book.category_id else borrow_count
            scored_books.append((score, book))

        # Sort by highest score descending
        scored_books.sort(key=lambda x: x[0], reverse=True)
        recommended_books = [book for score, book in scored_books[:limit]]

        # Step 4: The "Cold Start" Fallback Strategy
        # If the book is brand new, no one has co-borrowed it yet. 
        # We must pad the recommendations with the overall most popular books in the SAME genre.
        if len(recommended_books) < limit:
            exclude_ids = [target_book_id] + [b.id for b in recommended_books]
            needed = limit - len(recommended_books)

            fallback_books = db.session.query(
                Book, func.count(Transaction.id).label('pop_count')
            ).outerjoin(
                BookCopy, Book.id == BookCopy.book_id
            ).outerjoin(
                Transaction, Transaction.copy_id == BookCopy.id
            ).filter(
                Book.category_id == target_book.category_id,
                Book.id.notin_(exclude_ids)
            ).group_by(Book.id).order_by(
                func.count(Transaction.id).desc()
            ).limit(needed).all()

            recommended_books.extend([b for b, count in fallback_books])

        return recommended_books

    @staticmethod
    def get_borrowing_velocity_flag(member_id: int) -> bool:
        """
        Calculates if a member is borrowing > 3x their monthly average in one week.
        Returns True if velocity is anomalously high.
        """
        from datetime import datetime, timedelta
        
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)

        # Total borrows in last 30 days
        past_month_borrows = db.session.query(func.count(Transaction.id)).filter(
            Transaction.member_id == member_id,
            Transaction.issued_at >= thirty_days_ago
        ).scalar() or 0

        # Total borrows in last 7 days
        past_week_borrows = db.session.query(func.count(Transaction.id)).filter(
            Transaction.member_id == member_id,
            Transaction.issued_at >= seven_days_ago
        ).scalar() or 0

        # Average weekly borrows over the last month
        avg_weekly = past_month_borrows / 4.0 if past_month_borrows > 0 else 0.0
        
        # Flag if they borrowed 3x their average this week (and have actually borrowed > 2 books)
        if avg_weekly > 0 and past_week_borrows >= (avg_weekly * 3) and past_week_borrows > 2:
            return True
            
        return False

    @staticmethod
    def get_dashboard_chart_data():
        """Aggregates data for Chart.js admin dashboard."""
        from app.models.book import Category
        from app.models.user import User
        from datetime import datetime, timedelta
        
        # 1. Borrowing by Category (Pie Chart)
        category_stats = db.session.query(
            Category.name, func.count(Transaction.id)
        ).select_from(Transaction).join(
            BookCopy, Transaction.copy_id == BookCopy.id
        ).join(
            Book, BookCopy.book_id == Book.id
        ).join(
            Category, Book.category_id == Category.id
        ).group_by(Category.name).all()

        # 2. Borrowing by User Tier (Bar Chart)
        tier_stats = db.session.query(
            User.tier, func.count(Transaction.id)
        ).select_from(Transaction).join(
            User, Transaction.member_id == User.id
        ).filter(User.tier.isnot(None)).group_by(User.tier).all()

        # 3. Borrowing Timeline (Last 7 Days)
        timeline = []
        counts = []
        today = datetime.utcnow().date()
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            timeline.append(day.strftime('%a'))
            
            # Count transactions for that day
            day_count = db.session.query(func.count(Transaction.id)).filter(
                func.date(Transaction.issued_at) == day
            ).scalar() or 0
            counts.append(day_count)

        return {
            "categories": {
                "labels": [stat[0] for stat in category_stats],
                "data": [stat[1] for stat in category_stats]
            },
            "tiers": {
                "labels": [str(stat[0]).title() for stat in tier_stats],
                "data": [stat[1] for stat in tier_stats]
            },
            "timeline": {
                "labels": timeline,
                "data": counts
            }
        }