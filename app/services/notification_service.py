from flask_mail import Message
from flask import current_app
from app.extensions import mail
from app.models.user import User
from app.models.book import Book
from app.models.transaction import Transaction

class NotificationService:
    """Handles all email communications for the library."""

    @staticmethod
    def send_email(subject: str, recipients: list, text_body: str, html_body: str = None):
        """Core email sender function."""
        try:
            msg = Message(
                subject=subject,
                sender=current_app.config.get('MAIL_USERNAME', 'noreply@libra.com'),
                recipients=recipients
            )
            msg.body = text_body
            if html_body:
                msg.html = html_body
            mail.send(msg)
            return {"success": True}
        except Exception as e:
            print(f"[MAIL ERROR] Failed to send email to {recipients}: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def send_overdue_reminder(user: User, book: Book, transaction: Transaction):
        """Sends an overdue reminder to a member."""
        subject = f"Action Required: Library Book '{book.title}' is Overdue"
        text = f"Dear {user.name},\n\nThis is a friendly reminder that your borrowed copy of '{book.title}' was due on {transaction.due_date.strftime('%Y-%m-%d')}. Please return it to the library as soon as possible to avoid further fines.\n\nThank you,\nLibra Admin"
        return NotificationService.send_email(subject, [user.email], text)

    @staticmethod
    def send_reservation_ready(user: User, book: Book):
        """Notifies a member that their waitlisted book is ready."""
        subject = f"Your Waitlist Book is Ready: '{book.title}'"
        text = f"Dear {user.name},\n\nGood news! A copy of '{book.title}' has been returned and is now reserved for you. Please collect it from the front desk within the next 48 hours, or it will be passed to the next person in line.\n\nThank you,\nLibra Admin"
        return NotificationService.send_email(subject, [user.email], text)