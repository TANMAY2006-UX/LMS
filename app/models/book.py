from sqlalchemy import Nullable
from sqlalchemy.util import unique_list
from app.extensions import db
from datetime import datetime

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)

    books= db.relationship('Book', backref='category', lazy=True)


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    cover_url = db.Column(db.String(500))
    publisher = db.Column(db.String(150))
    published_year = db.Column(db.Integer)

    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    total_copies = db.Column(db.Integer, default=0)
    available_copies = db.Column(db.Integer, default=0)

    # Who added the Book Trail
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    # Strict DB Protections
    __table_args__ = (
        db.CheckConstraint('available_copies >= 0', name='chk_cavail_non_nogative'),
        db.CheckConstraint('total_copies >= 0', name='chk_total_non_negative'),
        db.CheckConstraint('available_copies <= total_copies', name='chk_avail_lte_total'),
        db.CheckConstraint('length(isbn) IN (10, 13)', name='chk_isbn_length'),
        db.CheckConstraint('published_year >= 1000 AND published_year <= 2050', name='chk_published_year'),
    )

    # One-to-Many: If a book is deleted, cascade and delete all its physical copies
    copies = db.relationship('BookCopy', backref='book', lazy=True, cascade="all, delete-orphan")


class BookCopy(db.Model):
    __tablename__ = 'book_copies'
    id = db.Column(db.Integer, primary_key=True)

    # ON DELETE CASCADE ensures orphaned copies don't crash the database
    book_id = db.Column(db.Integer, db.ForeignKey('books.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(20), default='available')
    added_date = db.Column(db.Date, default=datetime.utcnow)
    notes = db.Column(db.Text)
    # Check the Status of Book
    __table_args__ = (
        db.CheckConstraint("status IN ('available', 'issued', 'reserved', 'withdrawn')", name='chk_copy_status'),
        # Creating the composite key for faster retrival (log n)
        db.Index('idx_copies_book_status', 'book_id', 'status'),
    )