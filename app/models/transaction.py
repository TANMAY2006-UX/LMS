from app.extensions import db
from datetime import datetime, date

class FinePolicy(db.Model):
    __tablename__ = 'fine_policies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    # Fines for STUDENT / FACULTY / STAFF
    applies_to_tier = db.Column(db.String(20), nullable=False)
    grace_days = db.Column(db.Integer, default=0)
    rate_per_day = db.Column(db.Numeric(6, 2), nullable=False)
    max_fine_cap = db.Column(db.Numeric(8, 2))
    exclude_weekends = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)

    __table_args__ = (
        db.CheckConstraint('rate_per_day > 0', name='chk_rate_positive'),

        # Creating the Unique partial Key for Indentification of the Active policies...
        db.Index('uq_active_policy_per_tier', 'applies_to_tier', unique=True, postgresql_where=db.text('is_active = true')),
    )

class Transaction(db.Model): 
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)

    # If Somebody has taken the book then we should not able to delete the book
    copy_id = db.Column(db.Integer, db.ForeignKey('book_copies.id', ondelete='RESTRICT'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    issued_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=False)

    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.Date, nullable=False)

    returned_at = db.Column(db.DateTime)
    returned_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    status = db.Column(db.String(20), default='active')
    notes = db.Column(db.Text)

    # One Transaction can have multiple fine events  
    fines = db.relationship('Fine', backref='transaction', lazy=True, cascade="all, delete-orphan")

    # Relationships
    member = db.relationship('User', foreign_keys=[member_id], backref=db.backref('borrow_transactions', lazy=True))
    issuer = db.relationship('User', foreign_keys=[issued_by])
    receiver = db.relationship('User', foreign_keys=[returned_by])
    copy = db.relationship('BookCopy', backref=db.backref('transactions', lazy=True))

    # Transaction rules and constraints with indexing:
    __table_args = (
        # Status of the book
        db.CheckConstraint("status IN ('active', 'overdue', 'returned')", name='chk_txn_status'),

        # Consistancy in the DB
        db.CheckConstraint(
            "(returned_at IS NULL AND status IN ('active', 'overdue')) OR (returned_at IS NOT NULL AND status = 'returned')",
            name='chk_returned_consistency'
        ),

        # In case of Active/Overdue the individual copy should not affect the DB. Like one book per user only constraint for clean DB
        db.Index('uq_active_txn_per_copy', 'copy_id', unique=True, postgresql_where=db.text("status IN ('active', 'overdue')")),

        # Performance Indexes for dashboards
        db.Index('idx_txn_member_status', 'member_id', 'status'),
        db.Index('idx_txn_status_due', 'status', 'due_date', postgresql_where=db.text("status IN ('active', 'overdue')"))
    )

class Fine(db.Model):
    __tablename__ = 'fines'
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id', ondelete='CASCADE'), nullable=False)
    amount = db.Column(db.Numeric(8, 2), nullable=False)
    days_overdue = db.Column(db.Integer)
    calculated_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Extra Features for Fines.

    paid_at = db.Column(db.DateTime)
    waived_at = db.Column(db.DateTime)
    waived_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    waiver_reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')

    # Constraints for Checking th fine amounts smoothly.
    __table_args__ = (
        db.CheckConstraint("status IN ('pending', 'paid', 'waived')", name='chk_fine_status'),
        db.CheckConstraint("amount > 0", name='chk_fine_amount_positive'),
        # Cannot be paid AND waived at the same time
        db.CheckConstraint("NOT (paid_at IS NOT NULL AND waived_at IS NOT NULL)", name='chk_fine_resolution_exclusive'),
    )