from app.extensions import db
from app.models.reservation import Reservation
from app.models.book import Book, BookCopy
from app.models.user import User
from app.models.transaction import Transaction
from datetime import datetime, timedelta
from app.services.notification_service import NotificationService

class ReservationService:
    """
    Handles waitlist logic for books that are out of stock.
    """

    @staticmethod
    def reserve_book(member_id: int, book_id: int) -> dict:
        """Places a member on the waitlist for a specific book."""
        
        member = User.query.get(member_id)
        book = Book.query.get(book_id)

        if not member or not member.is_active or member.role != 'member':
            return {"success": False, "error": "Invalid or inactive member account."}

        if not book:
            return {"success": False, "error": "Book not found."}

        # 1. Rule: You cannot reserve a book that is sitting on the shelf!
        if book.available_copies > 0:
            return {"success": False, "error": "This book is currently available on the shelf! Go to the desk to issue it."}

        # 2. Rule: Prevent duplicate reservations (violates DB constraints)
        existing_res = Reservation.query.filter(
            Reservation.member_id == member_id,
            Reservation.book_id == book_id,
            Reservation.status.in_(['waiting', 'notified'])
        ).first()

        if existing_res:
            return {"success": False, "error": "You are already on the waitlist for this book."}

        # 3. Rule: Prevent reserving a book they already have checked out
        already_has = db.session.query(Transaction).join(BookCopy).filter(
            Transaction.member_id == member_id,
            BookCopy.book_id == book_id,
            Transaction.status.in_(['active', 'overdue'])
        ).first()
        
        if already_has:
            return {"success": False, "error": "You already have an active borrowed copy of this book."}

        # Execute Mutation
        try:
            new_res = Reservation(
                book_id=book_id,
                member_id=member_id,
                status='waiting'
            )
            db.session.add(new_res)
            db.session.commit()
            return {"success": True, "reservation": new_res}
            
        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": f"Database error: {str(e)}"}

    @staticmethod
    def notify_next_in_queue(book_id: int):
        """Finds the next person in the waitlist, marks them notified, and sends an email."""
        # Find next waiting reservation, ordered by fairness score and time
        next_res = db.session.execute(
            db.select(Reservation)
            .where(Reservation.book_id == book_id, Reservation.status == 'waiting')
            .order_by(Reservation.fairness_score.desc(), Reservation.queued_at.asc())
            .with_for_update(skip_locked=True)
            .limit(1)
        ).scalar_one_or_none()

        if next_res:
            # 1. Update the database state
            next_res.status = 'notified'
            next_res.notified_at = datetime.utcnow()
            next_res.expires_at = datetime.utcnow() + timedelta(hours=48)

            # 2. Fetch details for the email
            member = User.query.get(next_res.member_id)
            book = Book.query.get(book_id)

            # 3. Send the automated email!
            NotificationService.send_reservation_ready(member, book)
            
            db.session.commit()
            return True
            
        return False   