from app.extensions import db
from app.models.user import User
from app.models.book import Book, BookCopy
from app.models.transaction import Transaction
from app.models.audit import AuditLog
from datetime import datetime, timedelta
from app.services.fine_service import FineService
from app.services.goal_service import GoalService
from app.models.transaction import Fine

class IssueService:
    """
    Handles the core business logic of issuing and returning books.
    """

    @staticmethod
    def validate_issue(member_id: int, book_id: int) -> dict:
        """ validate() — pure checks, no mutations."""
        member = User.query.get(member_id)
        if not member or member.role != 'member' or not member.is_active:
            return {"success": False, "error": "Invalid or inactive member account."}

        book = Book.query.get(book_id)
        if not book or book.available_copies <= 0:
            return {"success": False, "error": "No available copies for this book currently."}

        # Check if the member already has a copy of THIS specific book!
        already_has = db.session.query(Transaction).join(BookCopy).filter(
            Transaction.member_id == member_id,
            BookCopy.book_id == book_id,
            Transaction.status.in_(['active', 'overdue'])
        ).first()
        
        if already_has:
            return {"success": False, "error": f"Member already has an active borrowed copy of '{book.title}'."}

        # Check Waitlist Queue Logic: Block direct issue if others are waiting!
        from app.models.reservation import Reservation
        # Are there any active reservations for this book?
        active_reservations = Reservation.query.filter(
            Reservation.book_id == book_id,
            Reservation.status.in_(['waiting', 'notified'])
        ).order_by(Reservation.fairness_score.desc(), Reservation.queued_at.asc()).all()

        if active_reservations:
            # The FIRST person in line gets exclusive rights (either notified or just waiting)
            first_in_line = active_reservations[0]
            if first_in_line.member_id != member_id:
                return {"success": False, "error": f"Direct issue blocked. This book is reserved for a waitlisted member."}
            else:
                # If they are first in line, and their status is 'waiting' or 'notified', we let them have it!
                # We also need to mark the reservation as 'collected' in the execute phase.
                pass

        # Check borrow limit (Tier policies: Student=3, Faculty/Staff=5)
        active_txns = Transaction.query.filter_by(member_id=member_id, status='active').count()
        limit = 5 if member.tier in ['faculty', 'staff'] else 3
        
        if active_txns >= limit:
            return {"success": False, "error": f"Member has reached their active borrow limit of {limit} books."}

        return {"success": True, "member": member, "book": book}

    @staticmethod
    def execute_issue(member_id: int, book_id: int, librarian_id: int) -> dict:
        """ on_submit() — executes the database mutations safely."""
        
        # 1. Run Pure Validation
        val = IssueService.validate_issue(member_id, book_id)
        if not val["success"]:
            return val

        try:
            # 2. 'skip_locked=True' means if another librarian is currently issuing Copy #1, 
            # this query will instantly grab Copy #2 instead of waiting or crashing!
            copy = db.session.execute(
                db.select(BookCopy)
                .where(BookCopy.book_id == book_id, BookCopy.status == 'available')
                .with_for_update(skip_locked=True)
                .limit(1)
            ).scalar_one_or_none()

            if not copy:
                return {"success": False, "error": "Someone else just issued the last copy! Please refresh."}

            # 3. Lock the master Book row to decrement the counter safely
            book = db.session.execute(
                db.select(Book)
                .where(Book.id == book_id)
                .with_for_update()
            ).scalar_one()

            # 4. Mutate States
            copy.status = 'issued'
            book.available_copies -= 1

            # 5. Create the Transaction Lineage
            # Default borrow period is 14 days
            due_date = datetime.utcnow().date() + timedelta(days=14) 
            
            txn = Transaction(
                copy_id=copy.id,
                member_id=member_id,
                issued_by=librarian_id,
                due_date=due_date,
                status='active'
            )
            db.session.add(txn)
            db.session.flush() # Get the new txn ID without committing yet

            # 6. Create the Audit Log entry
            audit = AuditLog(
                action='BOOK_ISSUED',
                entity_type='transaction',
                entity_id=txn.id,
                description=f"Book '{book.title}' (Copy #{copy.id}) issued to {val['member'].name}.",
                actor_id=librarian_id
            )
            db.session.add(audit)
            
            # 6.5 Mark reservation as collected if it exists!
            from app.models.reservation import Reservation
            active_res = Reservation.query.filter(
                Reservation.member_id == member_id,
                Reservation.book_id == book_id,
                Reservation.status.in_(['waiting', 'notified'])
            ).first()
            if active_res:
                active_res.status = 'collected'
                active_res.notes = (active_res.notes or '') + f"\nCollected via Transaction #{txn.id} on {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}."

            # 7. Commit everything together safely
            db.session.commit()
            return {"success": True, "transaction": txn}

        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": f"A database collision occurred: {str(e)}"}

    @staticmethod
    def return_book(transaction_id: int, librarian_id: int, notes: str = None) -> dict:
        """Processes a book return safely, preventing race conditions."""
        try:
            # 1. Lock the transaction row so no scheduled jobs can touch it while we return it
            txn = db.session.execute(
                db.select(Transaction).where(Transaction.id == transaction_id).with_for_update()
            ).scalar_one_or_none()

            if not txn:
                return {"success": False, "error": "Transaction not found."}
            if txn.status == 'returned':
                return {"success": False, "error": "This book has already been returned!"}

            # 2. Update Transaction (OBSERVATION 6 FIX!)
            txn.status = 'returned'
            txn.returned_at = datetime.utcnow()
            txn.returned_by = librarian_id
            if notes:
                txn.notes = notes

            # 3. Lock and Free the Physical Copy
            copy = db.session.execute(
                db.select(BookCopy).where(BookCopy.id == txn.copy_id).with_for_update()
            ).scalar_one()
            copy.status = 'available'

            # 4. Lock and Increment the Master Book Counter
            book = db.session.execute(
                db.select(Book).where(Book.id == copy.book_id).with_for_update()
            ).scalar_one()
            book.available_copies += 1

            # 5. Audit Log
            audit = AuditLog(
                action='BOOK_RETURNED',
                entity_type='transaction',
                entity_id=txn.id,
                description=f"Copy #{copy.id} of '{book.title}' returned.",
                actor_id=librarian_id
            )
            db.session.add(audit)

            # Trigger automatic fine calculation
            FineService.calculate_fine(txn.id)

            # 6. UPDATE READING GOAL 
            db.session.commit() # Commit the return first for safety
            
            # Now trigger the side-effect to increase the progress bar
            GoalService.increment_read_count(txn.member_id)
            # Check if anyone is waiting for this book and notify them!
            from app.services.reservation_service import ReservationService
            ReservationService.notify_next_in_queue(book.id)

            return {"success": True, "transaction": txn}

        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": f"Database error: {str(e)}"}