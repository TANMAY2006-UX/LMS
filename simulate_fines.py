from app import create_app
from app.extensions import db
from app.models.transaction import Transaction, Fine
from app.models.book import BookCopy
from app.models.user import User
from datetime import datetime, timedelta

app = create_app()

def generate_fake_fine():
    """Artificially creates a 10-day overdue transaction and a ₹50 pending fine."""
    with app.app_context():
        # Get the first member, first copy, and first admin
        member = User.query.filter_by(role='member').first()
        copy = BookCopy.query.first()
        admin = User.query.filter_by(role='admin').first()

        if not member or not copy or not admin:
            print("Missing member, copy, or admin in DB. Please add them first.")
            return

        # 1. Create a fake overdue transaction (due 10 days ago)
        txn = Transaction(
            copy_id=copy.id,
            member_id=member.id,
            issued_by=admin.id,
            due_date=datetime.utcnow().date() - timedelta(days=10),
            status='overdue'
        )
        db.session.add(txn)
        db.session.flush() # Get the new txn ID

        # 2. Create the associated pending fine
        fine = Fine(
            transaction_id=txn.id,
            amount=50.00,
            days_overdue=10,
            status='pending'
        )
        db.session.add(fine)
        db.session.commit()

        print(f"✅ Created a fake ₹50 fine for {member.name}! Go refresh your Fines Dashboard.")

if __name__ == '__main__':
    generate_fake_fine()