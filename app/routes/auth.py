from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.models.user import User

""" Blueprint: It is used to make routes in the individual files.
    render_template: It is used for rendering the HTML template (we use tailwind CSS for styling)
    redirect: It is used to redirect the user to the other pages.
    url_for: It is used to generate the URL for the other pages.
    flash: It is used to display the flash messages.
    request: It is used to get the request from the user.
    """

# Create the authentication blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If they are already logged in, send them away from the login page
    if current_user.is_authenticated:
        return redirect('/') # We will update this to point to the dashboard later

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Look up the user in the database
        user = User.query.filter_by(email=email).first()

        # Check if the user exists AND the password matches the hash
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect('/') # Placeholder until we build dashboards
            
        flash('Invalid email or password.', 'error')

    # If it's a GET request (just visiting the page), show the HTML form
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))