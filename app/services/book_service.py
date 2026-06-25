import requests
import re
from app.extensions import db
from app.models.book import Category, Book, BookCopy

class BookService:
    """
    Handles all business logic for Categories, Books, and Copies.
    Structured to align with Frappe Framework controller patterns.
    """

    @staticmethod
    def get_all_books():
        """Fetches all books to display on the inventory page."""
        return Book.query.order_by(Book.created_at.desc()).all()

    @staticmethod
    def create_category(name: str, slug: str, description: str = None):
        """Creates a new book category."""
        # Frappe pattern: Validate first
        existing = Category.query.filter_by(slug=slug).first()
        if existing:
            return {"success": False, "error": "Category with this slug already exists."}

        # Frappe pattern: Execute mutation
        category = Category(name=name, slug=slug, description=description)
        db.session.add(category)
        db.session.commit()
        return {"success": True, "category": category}

    @staticmethod
    def fetch_from_openlibrary(isbn: str):
        """
        Fetches book metadata from the free OpenLibrary API.
        This saves the librarian from typing out titles and authors manually!
        """
        # Clean the ISBN (remove hyphens and spaces)
        clean_isbn = isbn.replace("-", "").replace(" ", "")
        
        if len(clean_isbn) not in [10, 13]:
            return {"success": False, "error": "Invalid ISBN format. Must be 10 or 13 digits."}

        # Call the OpenLibrary API
        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{clean_isbn}&jscmd=data&format=json"
        
        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            key = f"ISBN:{clean_isbn}"
            if key not in data:
                return {"success": False, "error": "Book not found in OpenLibrary database."}
                
            book_data = data[key]
            
            # Safely extract the published year using Regex
            # This prevents crashes if the API returns "July 2008" instead of just "2008"
            published_year = None
            raw_date = book_data.get('publish_date', '')
            if raw_date:
                match = re.search(r'\d{4}', raw_date)
                if match:
                    published_year = int(match.group())
            
            # ULTRA-SAFE EXTRACTION: Handling messy OpenLibrary data
            authors = book_data.get('authors', [])
            author_name = "Unknown"
            if authors and isinstance(authors, list) and isinstance(authors[0], dict):
                author_name = authors[0].get('name', 'Unknown')
                
            publishers = book_data.get('publishers', [])
            publisher_name = ""
            if publishers and isinstance(publishers, list) and isinstance(publishers[0], dict):
                publisher_name = publishers[0].get('name', '')
                
            cover_data = book_data.get('cover')
            cover_url = ""
            if isinstance(cover_data, dict):
                # If 'large' is missing, fallback to 'medium' or 'small'
                cover_url = cover_data.get('large') or cover_data.get('medium') or cover_data.get('small') or ""

            subjects = book_data.get('subjects', [])
            suggested_category = ""
            if subjects and isinstance(subjects, list):
                # Grab the name of the very first subject they provide
                suggested_category = subjects[0].get('name', '')

            # Safely extract description (OpenLibrary sometimes uses a string, sometimes a dict)
            raw_desc = book_data.get('description', '')
            description = raw_desc.get('value', '') if isinstance(raw_desc, dict) else raw_desc
            if not isinstance(description, str):
                description = ''
            
            # Extract the useful fields
            return {
                "success": True,
                "data": {
                    "title": book_data.get('title', ''),
                    "author": book_data.get('authors', [{'name': 'Unknown'}])[0]['name'],
                    "publisher": book_data.get('publishers', [{'name': ''}])[0]['name'],
                    "published_year": published_year,
                    "cover_url": book_data.get('cover', {}).get('large', ''),
                    "description": description,
                    "suggested_category": suggested_category
                }
            }
        except requests.RequestException:
            return {"success": False, "error": "Failed to connect to OpenLibrary API."}

    @staticmethod
    def create_book(data: dict, user_id: int):
        """Saves a new book AND its physical copies into the PostgreSQL database."""
        try:
            # 1. Create a default category if none exists (for MVP speed)
            cat_id = data.get('category_id')
            if not cat_id:
                category = Category.query.filter_by(slug='uncategorized').first()
                if not category:
                    category = Category(name='Uncategorized', slug='uncategorized')
                    db.session.add(category)
                    db.session.flush()
                cat_id = category.id

            # 2. Prevent duplicate ISBNs
            existing_book = Book.query.filter_by(isbn=data['isbn']).first()
            if existing_book:
                return {"success": False, "error": "A book with this ISBN already exists!"}

            # 3. Create the Master Book Record
            book = Book(
                isbn=data['isbn'],
                title=data['title'],
                category_id=cat_id,
                author=data['author'],
                description=data.get('description', ''),
                publisher=data.get('publisher', ''),
                # Handle empty strings from the form safely
                published_year=int(data['published_year']) if data.get('published_year') else None,
                cover_url=data.get('cover_url', ''),
                total_copies=int(data['initial_copies']),
                available_copies=int(data['initial_copies']),
                created_by=user_id
            )
            db.session.add(book)
            db.session.flush() # Get the new book's ID

            # 4. Magically generate the Physical Book Copies!
            # If the librarian says they bought 3 copies, we create 3 separate rows.
            for _ in range(int(data['initial_copies'])):
                copy = BookCopy(book_id=book.id, status='available')
                db.session.add(copy)

            # 5. Commit everything to PostgreSQL securely
            db.session.commit()
            return {"success": True, "book": book}

        except Exception as e:
            db.session.rollback()
            return {"success": False, "error": f"Database error: {str(e)}"}