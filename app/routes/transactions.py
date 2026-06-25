from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.services.issue_service import IssueService
from app.models.user import User
from app.models.book import Book
from app.models.transaction import Transaction

try:
    from app.utils import role_required
except ImportError:
    def role_required(*roles):
        def decorator(f):
            return f
        return decorator

transactions_bp = Blueprint('transactions', __name__, url_prefix='/transactions')

@transactions_bp.route('/issue', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'librarian')
def issue_book():
    """Renders the issue form and handles the issue logic."""
    if request.method == 'POST':
        member_id = request.form.get('member_id')
        book_id = request.form.get('book_id')
        
        if not member_id or not book_id:
            flash("Please select both a member and a book.", "error")
            return redirect(url_for('transactions.issue_book'))

        result = IssueService.execute_issue(
            member_id=int(member_id), 
            book_id=int(book_id), 
            librarian_id=current_user.id
        )
        
        if result['success']:
            flash(f"Book successfully issued! Transaction #{result['transaction'].id}", "success")
        else:
            flash(result['error'], "error")
            
        return redirect(url_for('transactions.issue_book'))

    # For a GET request, we need to pass lists of active members and available books to the dropdowns
    members = User.query.filter_by(role='member', is_active=True).all()
    books = Book.query.filter(Book.available_copies > 0).all()
    
    return render_template('transactions/issue.html', members=members, books=books)


@transactions_bp.route('/return', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'librarian')
def return_book():
    """Displays active transactions and handles returning a book."""
    if request.method == 'POST':
        transaction_id = request.form.get('transaction_id')
        notes = request.form.get('notes')
        
        if not transaction_id:
            flash("Invalid transaction selected.", "error")
            return redirect(url_for('transactions.return_book'))

        # Fetch transaction BEFORE returning it so we know if it was late
        txn = Transaction.query.get(transaction_id)
        was_overdue = False
        if txn and txn.status == 'overdue':
            was_overdue = True

        # Call our robust service layer to handle the return!
        result = IssueService.return_book(
            transaction_id=int(transaction_id), 
            librarian_id=current_user.id,
            notes=notes
        )
        
        if result['success']:
            # THE UX REDIRECT LOGIC
            if was_overdue:
                flash(f"Book returned late! Please settle the fine.", "warning")
                return redirect(url_for('fines.index'))
            else:
                flash(f"Book successfully returned! Inventory updated.", "success")
        else:
            flash(result['error'], "error")
            
        return redirect(url_for('transactions.return_book'))

    # Fetch all currently active or overdue transactions to display in the table
    active_transactions = Transaction.query.filter(
        Transaction.status.in_(['active', 'overdue'])
    ).order_by(Transaction.issued_at.desc()).all()
    
    return render_template('transactions/return.html', transactions=active_transactions)