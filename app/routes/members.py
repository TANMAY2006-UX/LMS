from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from app.services.member_service import MemberService
from app.services.analytics_service import AnalyticsService

# Import our VIP bouncer
try:
    from app.utils import role_required
except ImportError:
    def role_required(*roles):
        def decorator(f):
            return f
        return decorator

members_bp = Blueprint('members', __name__, url_prefix='/members')

@members_bp.route('/', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'librarian')
def index():
    """Displays the member list and handles adding new members."""
    if request.method == 'POST':
        # Grab data from the form
        form_data = {
            'name': request.form.get('name'),
            'email': request.form.get('email'),
            'tier': request.form.get('tier'),
            'password': request.form.get('password')
        }
        
        from flask_login import current_user
        if current_user.role == 'admin':
            form_data['role'] = request.form.get('role', 'member')
        else:
            form_data['role'] = 'member'
        
        # Send to the service layer
        result = MemberService.create_member(form_data)
        
        if result['success']:
            flash(f"Successfully created account for {form_data['name']}!", 'success')
        else:
            flash(result['error'], 'error')
            
        return redirect(url_for('members.index'))

    # If GET request, just fetch the list and show the page
    members = MemberService.get_all_members()

    # This creates a dictionary mapping member IDs to True/False for the velocity flag
    velocity_flags = {m.id: AnalyticsService.get_borrowing_velocity_flag(m.id) for m in members}
    
    velocity_flags = {m.id: AnalyticsService.get_borrowing_velocity_flag(m.id) for m in members}
    return render_template('members/index.html', members=members, velocity_flags=velocity_flags)

@members_bp.route('/api/search', methods=['GET'])
@login_required
@role_required('admin', 'librarian')
def search_members_api():
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify([])
        
    search_pattern = f"%{query}%"
    from app.models.user import User
    from app import db
    members = User.query.filter(
        db.or_(
            User.name.ilike(search_pattern),
            User.email.ilike(search_pattern)
        ),
        User.role == 'member',
        User.is_active == True
    ).limit(10).all()
    
    results = [{'id': m.id, 'name': m.name, 'email': m.email, 'tier': m.tier} for m in members]
    from flask import jsonify
    return jsonify(results)