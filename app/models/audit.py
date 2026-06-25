from app.extensions import db
from datetime import datetime

class AuditLog(db.Model):
    __tablename__ = 'audit_log'
    id = db.Column(db.Integer, primary_key=True)

    # Any action Taken : Book is Issued / Fine Waived / Taken / Book Deleted
    action = db.Column(db.String(100), nullable=False)
    # Transaction made / Member Added / Removed
    entity_type = db.Column(db.String(50))      

    # Transaction id/ Member id storing      
    entity_id = db.Column(db.Integer)

    # Human readable format
    description = db.Column(db.Text, nullable=False) 

    # Used SET NULL as to denote that do nothing if the user is deleted from the DB. Helps to keep track of the log 
    actor_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (

        # Quickly find all audit logs related to a specific book or member
        db.Index('idx_audit_entity', 'entity_type', 'entity_id'),
    )


class ReadingGoal(db.Model):
    __tablename__ = 'reading_goals'
    id = db.Column(db.Integer, primary_key=True)

    # If a member is deleted, their reading goals can safely be destroyed
    member_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    target_books = db.Column(db.Integer, nullable=False)
    books_read = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        # A member can only set ONE reading goal per year
        db.UniqueConstraint('member_id', 'year', name='uq_member_year'),
    )