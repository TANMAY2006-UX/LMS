from app.extensions import db, scheduler
from app.models.transaction import Transaction
from app.models.reservation import Reservation
from datetime import date, datetime

# Runs every day at 12:01 AM
@scheduler.task('cron', id='overdue_check_job', hour=0, minute=1)
def mark_overdue_books():
    """Marks active transactions past their due date as overdue."""
    # Arch Review 5.4: We MUST push the app context for background jobs to access the DB
    with scheduler.app.app_context():
        try:
            # Arch Review 1.1: skip_locked=True prevents deadlocks if a librarian is working at midnight!
            overdue_txns = db.session.execute(
                db.select(Transaction)
                .where(
                    Transaction.status == 'active',
                    Transaction.due_date < date.today()
                )
                .with_for_update(skip_locked=True)
            ).scalars().all()

            count = 0
            for txn in overdue_txns:
                if txn.status == 'active': # Double check after lock
                    txn.status = 'overdue'
                    count += 1
            
            db.session.commit()
            print(f"[APScheduler] Marked {count} books as overdue.")
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
            
            db.session.commit()
            print(f"[APScheduler] Expired {count} neglected reservations.")
        except Exception as e:
            db.session.rollback()
            print(f"[APScheduler] Error in reservation_expiry_job: {e}")