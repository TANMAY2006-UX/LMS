import os
from flask import Flask
from app.config import Config
from app.extensions import db, migrate, login_manager, mail, scheduler
from app.routes.auth import auth_bp
from app.routes.main import main_bp
from app.routes.books import books_bp
from app.routes.members import members_bp
from app.routes.transactions import transactions_bp
from app.routes.fines import fines_bp
from app.routes.reservations import reservations_bp
from app.routes.qr import qr_bp
from app import models
from app.routes.admin import admin_bp

def create_app(config_class=Config):
    """The Application Factory pattern."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Bind the extensions to this specific app instance
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    
    # Initialize the scheduler, but don't start it during tests or DB migrations
    scheduler.init_app(app)
    import app.tasks.scheduler as _
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        # Prevents the scheduler from running twice in Flask debug mode
        scheduler.start()


    # Register the Blueprints (Routes)

    app.register_blueprint(auth_bp)

    app.register_blueprint(main_bp)

    app.register_blueprint(books_bp)

    app.register_blueprint(members_bp)

    app.register_blueprint(transactions_bp)

    app.register_blueprint(fines_bp)

    app.register_blueprint(reservations_bp)

    app.register_blueprint(qr_bp)

    app.register_blueprint(admin_bp)
    
    return app