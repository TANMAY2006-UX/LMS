from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.services.reservation_service import ReservationService
from app.models.reservation import Reservation
from app.models.book import Book
from app.models.user import User
from datetime import datetime, timedelta
from app.extensions import db

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
    
    # First pass: count total people in queue per book
    book_totals = {}
    for res in active_reservations:
        book_totals[res.book_id] = book_totals.get(res.book_id, 0) + 1

    # Calculate position per book
    book_queues = {}
    for res in active_reservations:
        if res.book_id not in book_queues:
            book_queues[res.book_id] = 1
        else:
            book_queues[res.book_id] += 1
            
        book = Book.query.get(res.book_id)
        member = User.query.get(res.member_id)
        
        # Position label logic
        pos = book_queues[res.book_id]
        total = book_totals[res.book_id]
        
        if res.status == 'notified':
            pos_label = "Next Eligible Member"
        elif pos == 1:
            pos_label = "First in line"
        else:
            pos_label = f"Position {pos} of {total}"

        queue_data.append({
            'id': res.id,
            'book_title': book.title,
            'member_name': member.name,
            'member_tier': member.tier,
            'status': res.status,
            'queued_at': res.queued_at,
            'position': pos,
            'position_label': pos_label,
            'notes': res.notes
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

@reservations_bp.route('/<int:reservation_id>/remove', methods=['POST'])
@login_required
@role_required('admin', 'librarian')
def remove_from_queue(reservation_id):
    """Remove a user from the queue permanently."""
    res = Reservation.query.get(reservation_id)
    if res:
        res.status = 'removed'
        res.notes = (res.notes or '') + f"\nRemoved by {current_user.name} on {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}."
        db.session.commit()
        flash("User removed from the waitlist.", "success")
    return redirect(url_for('reservations.index'))

@reservations_bp.route('/<int:reservation_id>/skip', methods=['POST'])
@login_required
@role_required('admin', 'librarian')
def skip_user(reservation_id):
    """Skip a user (move them down in priority)."""
    res = Reservation.query.get(reservation_id)
    if res:
        # Lower fairness score to push them back
        res.fairness_score -= 10
        if res.status == 'notified':
            res.status = 'waiting'
        res.notes = (res.notes or '') + f"\nSkipped by {current_user.name} on {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}."
        db.session.commit()
        flash("User skipped in the waitlist.", "info")
    return redirect(url_for('reservations.index'))

@reservations_bp.route('/<int:reservation_id>/promote', methods=['POST'])
@login_required
@role_required('admin', 'librarian')
def promote_user(reservation_id):
    """Manually promote and notify a specific user."""
    res = Reservation.query.get(reservation_id)
    if res and res.status == 'waiting':
        res.status = 'notified'
        res.notified_at = datetime.utcnow()
        res.expires_at = datetime.utcnow() + timedelta(hours=48)
        res.notes = (res.notes or '') + f"\nManually promoted by {current_user.name} on {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}."
        # In a real app, send email here via NotificationService
        db.session.commit()
        flash("User manually promoted and notified.", "success")
    return redirect(url_for('reservations.index'))