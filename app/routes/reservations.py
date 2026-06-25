from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.services.reservation_service import ReservationService
from app.models.reservation import Reservation
from app.models.book import Book
from app.models.user import User

try:
    from app.utils import role_required
except ImportError:
    def role_required(*roles):
        def decorator(f):
            return f
        return decorator

reservations_bp = Blueprint('reservations', __name__, url_prefix='/reservations')

@reservations_bp.route('/', methods=['GET'])
@login_required
@role_required('admin', 'librarian')
def index():
    """Librarian Dashboard: View the current waitlist for all books."""
    # Fetch all active waitlist entries, ordered by pure FIFO (First-In, First-Out)
    active_reservations = Reservation.query.filter(
        Reservation.status.in_(['waiting', 'notified'])
    ).order_by(Reservation.queued_at.asc()).all()
    
    # Bundle the data for the template
    queue_data = []
    for res in active_reservations:
        book = Book.query.get(res.book_id)
        member = User.query.get(res.member_id)
        queue_data.append({
            'id': res.id,
            'book_title': book.title,
            'member_name': member.name,
            'member_tier': member.tier,
            'status': res.status,
            'queued_at': res.queued_at
        })
        
    # We also need lists for the manual "Add to Queue" form
    members = User.query.filter_by(role='member', is_active=True).all()
    # Only show books that actually exist
    books = Book.query.all()
    
    return render_template('reservations/index.html', queue=queue_data, members=members, books=books)

@reservations_bp.route('/add', methods=['POST'])
@login_required
@role_required('admin', 'librarian')
def add_to_queue():
    """Allows a librarian to manually add a student to the waitlist."""
    member_id = request.form.get('member_id')
    book_id = request.form.get('book_id')
    
    if not member_id or not book_id:
        flash("Please select both a member and a book.", "error")
        return redirect(url_for('reservations.index'))

    result = ReservationService.reserve_book(int(member_id), int(book_id))
    
    if result['success']:
        flash("Successfully added to the waitlist!", "success")
    else:
        flash(result['error'], "error")
        
    return redirect(url_for('reservations.index'))

@reservations_bp.route('/join/<int:book_id>', methods=['POST'])
@login_required
def member_join_waitlist(book_id):
    """Allows a logged-in student/faculty to join the waitlist for a book."""
    if current_user.role != 'member':
        flash("Only members can join the waitlist directly.", "error")
        return redirect(url_for('books.book_detail', book_id=book_id))
        
    result = ReservationService.reserve_book(current_user.id, book_id)
    
    if result['success']:
        flash("You have successfully joined the waitlist for this book!", "success")
    else:
        flash(result['error'], "error")
        
    return redirect(url_for('books.book_detail', book_id=book_id))