import csv
from io import StringIO
from flask import Blueprint, render_template, request, flash, redirect, url_for, Response
from flask_login import login_required
from app.extensions import db
from app.models.transaction import FinePolicy, Transaction
from app.models.user import User
from app.models.book import Book, BookCopy
from app.services.notification_service import NotificationService
from app.services.analytics_service import AnalyticsService
from app.utils import role_required
from datetime import date

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard', methods=['GET'])
@login_required
@role_required('admin')
def analytics_dashboard():
    """Chart.js Analytics Dashboard & Email Preview"""
    chart_data = AnalyticsService.get_dashboard_chart_data()
    
    # Fetch exactly who will get emailed
    overdue_txns = Transaction.query.filter_by(status='overdue').all()
    preview_list = []
    for txn in overdue_txns:
        member = User.query.get(txn.member_id)
        book = Book.query.get(BookCopy.query.get(txn.copy_id).book_id)
        preview_list.append({'name': member.name, 'email': member.email, 'book': book.title, 'due': txn.due_date})
        
    return render_template('admin/dashboard.html', chart_data=chart_data, preview_list=preview_list)

@admin_bp.route('/policies', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def manage_policies():
    """Fine Policy Management UI"""
    if request.method == 'POST':
        policy_id = request.form.get('policy_id')
        policy = FinePolicy.query.get(policy_id)
        if policy:
            policy.rate_per_day = float(request.form.get('rate_per_day'))
            policy.grace_days = int(request.form.get('grace_days'))
            policy.max_fine_cap = float(request.form.get('max_fine_cap'))
            db.session.commit()
            flash(f"Policy '{policy.name}' updated successfully.", "success")
        return redirect(url_for('admin.manage_policies'))
        
    policies = FinePolicy.query.all()
    return render_template('admin/policies.html', policies=policies)

@admin_bp.route('/batch/reminders', methods=['POST'])
@login_required
@role_required('admin', 'librarian')
def batch_reminders():
    """Batch operation to send emails to all users with overdue books."""
    overdue_txns = Transaction.query.filter_by(status='overdue').all()
    count = 0
    
    for txn in overdue_txns:
        member = User.query.get(txn.member_id)
        copy = BookCopy.query.get(txn.copy_id)
        book = Book.query.get(copy.book_id)
        
        result = NotificationService.send_overdue_reminder(member, book, txn)
        if result['success']:
            count += 1
            
    flash(f"Successfully sent {count} overdue reminder emails.", "success")
    return redirect(url_for('main.dashboard'))

@admin_bp.route('/export/overdue-csv', methods=['GET'])
@login_required
@role_required('admin')
def export_overdue_csv():
    """Generates a CSV report of all overdue books."""
    overdue_txns = Transaction.query.filter_by(status='overdue').all()
    
    # In-memory file buffer
    si = StringIO()
    cw = csv.writer(si)
    
    # Headers
    cw.writerow(['Transaction ID', 'Member Name', 'Member Email', 'Book Title', 'Copy ID', 'Due Date', 'Days Overdue'])
    
    for txn in overdue_txns:
        member = User.query.get(txn.member_id)
        copy = BookCopy.query.get(txn.copy_id)
        book = Book.query.get(copy.book_id)
        days_late = (date.today() - txn.due_date).days
        
        cw.writerow([txn.id, member.name, member.email, book.title, copy.id, txn.due_date, days_late])
        
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=overdue_report.csv"}
    )