from app import db
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.services.book_service import BookService
from app.services.analytics_service import AnalyticsService
from app.models.book import Book
from app.models.book import Category

# app.utils was created earlier with role_required
try:
    from app.utils import role_required
except ImportError:
    # Fallback just in case utils wasn't fully set up yet
    def role_required(*roles):
        def decorator(f):
            return f
        return decorator

# Create the blueprint for all book-related URLs
books_bp = Blueprint('books', __name__, url_prefix='/books')

@books_bp.route('/', methods=['GET'])
@login_required
def index():
    """Displays the main book inventory grid."""
    search_query = request.args.get('q', '')
    
    if search_query:
        # If there's a search term, filter the books
        search_pattern = f"%{search_query}%"
        books = Book.query.outerjoin(Category).filter(
            db.or_(
                Book.title.ilike(search_pattern),
                Book.author.ilike(search_pattern),
                Book.isbn.ilike(search_pattern),
                Category.name.ilike(search_pattern)
            )
        ).order_by(Book.title).all()
    else:
        # Default: load all books
        books = BookService.get_all_books()
        
    # THE HTMX MAGIC:
    # If the request came from HTMX, we ONLY send back the HTML for the book grid.
    # We DO NOT send the sidebar, header, or footer again!
    if 'HX-Request' in request.headers:
        return render_template('books/partials/book_grid.html', books=books)

    # If it's a normal full page load, send the whole page
    return render_template('books/index.html', books=books)

@books_bp.route('/api/search', methods=['GET'])
@login_required
@role_required('admin', 'librarian')
def search_books_api():
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify([])
        
    search_pattern = f"%{query}%"
    books = Book.query.filter(
        db.or_(
            Book.title.ilike(search_pattern),
            Book.author.ilike(search_pattern),
            Book.isbn.ilike(search_pattern)
        ),
        Book.available_copies > 0
    ).limit(10).all()
    
    results = [{'id': b.id, 'title': b.title, 'author': b.author, 'isbn': b.isbn, 'available': b.available_copies} for b in books]
    return jsonify(results)

@books_bp.route('/<int:book_id>', methods=['GET'])
@login_required
def book_detail(book_id):
    """Displays details for a specific book and lists its physical copies."""
    from app.models.book import Book
    from app.models.transaction import Transaction
    from app.models.reservation import Reservation
    from app.models.user import User
    from app.services.analytics_service import AnalyticsService
    
    book = Book.query.get_or_404(book_id)
    
    # 1. FOR LIBRARIANS: Fetch who currently has the issued copies
    active_txns = {}
    if current_user.role in ['admin', 'librarian']:
        # Get all active/overdue transactions for copies of this book
        copy_ids = [c.id for c in book.copies]
        if copy_ids:
            txns = Transaction.query.filter(
                Transaction.copy_id.in_(copy_ids),
                Transaction.status.in_(['active', 'overdue'])
            ).all()
            
            for txn in txns:
                member = User.query.get(txn.member_id)
                active_txns[txn.copy_id] = {
                    'member_name': member.name,
                    'due_date': txn.due_date,
                    'status': txn.status
                }

    # 2. FOR MEMBERS: Check if they are already on the waitlist
    user_reservation = None
    if current_user.role == 'member':
        user_reservation = Reservation.query.filter_by(
            member_id=current_user.id,
            book_id=book.id
        ).filter(Reservation.status.in_(['waiting', 'notified'])).first()
    
    # Fetch the Hybrid Co-Borrowing Recommendations
    recommended_books = AnalyticsService.get_coborrowing_recommendations(book_id)
    
    return render_template('books/detail.html', 
                           book=book, 
                           recommended_books=recommended_books,
                           active_txns=active_txns,
                           user_reservation=user_reservation)

@books_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'librarian')
def add_book():
    """Renders the HTML form to add a new book and handles saving it."""
    if request.method == 'POST':
        # 1. Grab all the data typed into the HTML form
        form_data = {
            'isbn': request.form.get('isbn'),
            'title': request.form.get('title'),
            'category_id': request.form.get('category_id'),
            'author': request.form.get('author'),
            'publisher': request.form.get('publisher'),
            'published_year': request.form.get('published_year'),
            'cover_url': request.form.get('cover_url'),
            'initial_copies': request.form.get('initial_copies', 1),
            'description': request.form.get('description')
        }
        
        # 2. Hand it to the Service (Kitchen) to save to Postgres
        result = BookService.create_book(form_data, current_user.id)
        
        # 3. Inform the user of the result
        if result['success']:
            flash(f"Successfully added '{form_data['title']}' to the library!", 'success')
            # Redirect back to a fresh form so they can quickly scan the next book
            return redirect(url_for('books.add_book'))
        else:
            flash(result['error'], 'error')
            
    categories = Category.query.all()
    return render_template('books/form.html', categories=categories)

@books_bp.route('/api/fetch-isbn', methods=['GET'])
@login_required
@role_required('admin', 'librarian')
def fetch_isbn():
    """
    This is an API route! The frontend will call this secretly in the background
    when the librarian types an ISBN, without reloading the page.
    """
    # Gets the ISBN from the URL
    isbn = request.args.get('isbn')
    
    if not isbn:
        return jsonify({"success": False, "error": "No ISBN provided"}), 400
        
    # BookService
    result = BookService.fetch_from_openlibrary(isbn)
    
    # Returns JSON data to the browser
    return jsonify(result)