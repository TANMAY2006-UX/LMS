from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.extensions import db
from app.models.user import User
from app.models.book import Book
from app.models.transaction import Transaction, Fine
from app.models.audit import AuditLog
from app.services.goal_service import GoalService

# Create a blueprint for our core application pages
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required  
def dashboard():
    # Intelligent Routing: Send members to their personal portal!
    if current_user.role == 'member':
        return redirect(url_for('main.my_dashboard'))
        
    # Make the Stat Cards 100% REAL!
    total_fines_query = db.session.query(db.func.sum(Fine.amount)).filter(Fine.status == 'pending').scalar()
    
    revenue_query = db.session.query(db.func.sum(Fine.amount)).filter(Fine.status == 'paid').scalar()
    
    stats = {
        'total_books': Book.query.count(),
        'active_members': User.query.filter_by(role='member', is_active=True).count(),
        'overdue_books': Transaction.query.filter_by(status='overdue').count(),
        'pending_fines': float(total_fines_query) if total_fines_query else 0.00,  # New: Money the library is owed
        'total_fines_paid': float(revenue_query) if revenue_query else 0.00      # New: Money the library has collected
    }
    
    # Fetch the 15 most recent activities for the timeline
    recent_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(15).all()
    
    return render_template('dashboard.html', stats=stats, recent_logs=recent_logs)


@main_bp.route('/my-dashboard', methods=['GET', 'POST'])
@login_required
def my_dashboard():
    """The personal portal for Students and Faculty."""
    if current_user.role != 'member':
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        target = request.form.get('target_books')
        if target and target.isdigit() and int(target) > 0:
            GoalService.set_goal(current_user.id, int(target))
            flash('Your yearly reading goal has been updated!', 'success')
        return redirect(url_for('main.my_dashboard'))

    goal = GoalService.get_or_create_goal(current_user.id)
    progress_pct = int((goal.books_read / goal.target_books) * 100) if goal.target_books > 0 else 0
    progress_pct = min(progress_pct, 100) 
    
    active_txns = Transaction.query.filter_by(member_id=current_user.id).filter(
        Transaction.status.in_(['active', 'overdue'])
    ).all()
    
    pending_fines = Fine.query.join(Transaction).filter(
        Transaction.member_id == current_user.id,
        Fine.status == 'pending'
    ).all()

    return render_template('my_dashboard.html', goal=goal, progress_pct=progress_pct, active_txns=active_txns, pending_fines=pending_fines)