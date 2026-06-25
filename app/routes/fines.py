from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.transaction import Fine, Transaction
from app.models.user import User
from app.extensions import db
from datetime import datetime

# Import VIP Bouncer
try:
    from app.utils import role_required
except ImportError:
    def role_required(*roles):
        def decorator(f):
            return f
        return decorator

fines_bp = Blueprint('fines', __name__, url_prefix='/fines')

@fines_bp.route('/', methods=['GET'])
@login_required
@role_required('admin', 'librarian')
def index():
    """Displays all pending fines for librarians to process."""
    pending_fines = Fine.query.filter_by(status='pending').order_by(Fine.calculated_at.desc()).all()
    
    # We construct a safe list of dictionaries to pass to the template
    # to avoid SQLAlchemy relationship lookup errors in the HTML.
    fines_data = []
    for fine in pending_fines:
        txn = Transaction.query.get(fine.transaction_id)
        member = User.query.get(txn.member_id)
        fines_data.append({
            'id': fine.id,
            'transaction_id': txn.id,
            'copy_id': txn.copy_id,
            'member_name': member.name,
            'member_tier': member.tier,
            'days_overdue': fine.days_overdue,
            'amount': fine.amount
        })
        
    return render_template('fines/index.html', fines=fines_data)

@fines_bp.route('/<int:fine_id>/pay', methods=['POST'])
@login_required
@role_required('admin', 'librarian')
def pay_fine(fine_id):
    """Processes a cash payment for a fine."""
    fine = Fine.query.get_or_404(fine_id)
    
    if fine.status != 'pending':
        flash("This fine has already been processed.", "error")
        return redirect(url_for('fines.index'))
        
    try:
        fine.status = 'paid'
        fine.paid_at = datetime.utcnow()
        # For our MVP, we assume the librarian collected the physical cash.
        db.session.commit()
        flash(f"Fine #{fine.id} successfully marked as PAID.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error processing payment: {str(e)}", "error")
        
    return redirect(url_for('fines.index'))

@fines_bp.route('/<int:fine_id>/waive', methods=['POST'])
@login_required
@role_required('admin', 'librarian')
def waive_fine(fine_id):
    """Waives a fine, requiring a mandatory reason for the audit log."""
    fine = Fine.query.get_or_404(fine_id)
    reason = request.form.get('waiver_reason')
    
    if fine.status != 'pending':
        flash("This fine has already been processed.", "error")
        return redirect(url_for('fines.index'))
        
    # The Librarian is FORCED to provide a valid reason
    if not reason or len(reason.strip()) < 5:
        flash("A valid reason (at least 5 characters) is mandatory to waive a fine.", "error")
        return redirect(url_for('fines.index'))
        
    try:
        fine.status = 'waived'
        fine.waived_at = datetime.utcnow()
        fine.waived_by = current_user.id
        fine.waiver_reason = reason.strip()
        
        # NOTE: We will hook up the AuditLog here during Phase 2!
        
        db.session.commit()
        flash(f"Fine #{fine.id} successfully WAIVED.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error waiving fine: {str(e)}", "error")
        
    return redirect(url_for('fines.index'))