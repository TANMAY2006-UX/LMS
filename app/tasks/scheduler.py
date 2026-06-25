from app.extensions import db, scheduler
from app.models.transaction import Transaction
from app.models.reservation import Reservation
from datetime import date, datetime
from app.services.notification_service import NotificationService
from app.models.user import User
from app.models.book import Book, BookCopy

# Runs every day at 12:01 AM
@scheduler.task('cron', id='overdue_check_job', hour=0, minute=1)
def mark_overdue_books():
    with scheduler.app.app_context():
        try:
            overdue_txns = db.session.execute(
                db.select(Transaction)
                .where(Transaction.status == 'active', Transaction.due_date < date.today())
                .with_for_update(skip_locked=True)
            ).scalars().all()

            count = 0
            for txn in overdue_txns:
                if txn.status == 'active': 
                    txn.status = 'overdue'
                    count += 1
                    # --- NEW: Trigger Automated Email ---
                    member = User.query.get(txn.member_id)
                    copy = BookCopy.query.get(txn.copy_id)
                    book = Book.query.get(copy.book_id)
                    NotificationService.send_overdue_reminder(member, book, txn)
            
            db.session.commit()
            print(f"[APScheduler] Marked {count} books as overdue & sent emails.")
        except Exception as e:
            db.session.rollback()
            print(f"[APScheduler] Error in overdue_check_job: {e}")


# Runs every day at 12:05 AM
@scheduler.task('cron', id='reservation_expiry_job', hour=0, minute=5)
def expire_notified_reservations():
    """Expires reservations that were notified > 48 hours ago."""
    with scheduler.app.app_context():
        try:
            expired_res = db.session.execute(
                db.select(Reservation)
                .where(
                    Reservation.status == 'notified',
                    Reservation.expires_at < datetime.utcnow()
                )
                .with_for_update(skip_locked=True)
            ).scalars().all()

            count = 0
            for res in expired_res:
                if res.status == 'notified':
                    res.status = 'expired'
                    # Bump fairness score so they get priority next time they reserve!
                    res.fairness_score += 1 
                    count += 1

                    # Notify the next person in line for this same book!
                    from app.services.reservation_service import ReservationService
                    ReservationService.notify_next_in_queue(res.book_id)
            
            db.session.commit()
            print(f"[APScheduler] Expired {count} neglected reservations.")
        except Exception as e:
            db.session.rollback()
            print(f"[APScheduler] Error in reservation_expiry_job: {e}")