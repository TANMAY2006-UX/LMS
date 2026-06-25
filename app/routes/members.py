from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from app.services.member_service import MemberService

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
        
        # Send to the service layer
        result = MemberService.create_member(form_data)
        
        if result['success']:
            flash(f"Successfully created account for {form_data['name']}!", 'success')
        else:
            flash(result['error'], 'error')
            
        return redirect(url_for('members.index'))

    # If GET request, just fetch the list and show the page
    members = MemberService.get_all_members()
    return render_template('members/index.html', members=members)