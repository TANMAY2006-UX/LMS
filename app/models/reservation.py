from app.extensions import db
from datetime import datetime

class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)

    # Which book is set to reserve / Book_id / Member identification / At what sequence
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete='CASCADE'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    
    # First reserve first get.
    queued_at = db.Column(db.DateTime, default=datetime.utcnow)

    status = db.Column(db.String(20), default='waiting')
    notified_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    
    # Incremented each time the user gets bumped to the back of the queue
    fairness_score = db.Column(db.Integer, default=0)

    __table_args__ = (
        db.CheckConstraint("status IN ('waiting', 'notified', 'collected', 'expired', 'removed')", name='chk_reservation_status'),
        
        # You cannot have an expiry date if you have NOT been notified yet
        db.CheckConstraint(
            "(status IN ('waiting', 'removed') AND expires_at IS NULL) OR (status IN ('notified', 'collected', 'expired'))",
            name='chk_expires_only_when_notified'
        ),
        
        # A member can only be in the queue ONCE for a specific book
        db.Index('uq_active_reservation_per_member_book', 'member_id', 'book_id', unique=True, postgresql_where=db.text("status IN ('waiting', 'notified')")),
        
        # Finding the next person in line, ordered by fairness and then time
        # This feature Little concerned for this/ Will look into this
        db.Index('idx_reservations_book_queue', 'book_id', db.text('fairness_score DESC'), 'queued_at', postgresql_where=db.text("status = 'waiting'"))
    )