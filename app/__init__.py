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
    
    # Register error handlers
    from flask import render_template
    
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.context_processor
    def inject_notifications():
        from flask_login import current_user
        from datetime import datetime, timedelta
        from app.models.transaction import Transaction
        
        banner = None
        if current_user.is_authenticated and current_user.role == 'member':
            soon = datetime.utcnow() + timedelta(days=2)
            due_soon_count = Transaction.query.filter_by(
                member_id=current_user.id, 
                status='active'
            ).filter(Transaction.due_date <= soon).count()
            
            if due_soon_count > 0:
                banner = {
                    'type': 'warning',
                    'message': f"You have {due_soon_count} book{'s' if due_soon_count > 1 else ''} due soon or overdue."
                }
        return dict(global_banner=banner)

    return app