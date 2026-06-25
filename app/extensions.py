from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_apscheduler import APScheduler

# Initialize extensions globally, but unattached to any specific app yet.
# This prevents circular imports and allows for easy unit testing.
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
scheduler = APScheduler()

# Tell Flask-Login which route to redirect users to if they aren't authenticated
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'