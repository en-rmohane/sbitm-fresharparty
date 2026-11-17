import os
from flask import Flask, render_template
from config import Config
from app.extensions import db, login_manager, csrf

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure instance and upload directories exist safely (guard against read-only serverless filesystems)
    try:
        if not app.config.get('IS_VERCEL'):
            os.makedirs(os.path.join(app.root_path, '..', 'instance'), exist_ok=True)
        os.makedirs(app.config['SIGNATURE_FOLDER'], exist_ok=True)
        os.makedirs(app.config['SELFIE_FOLDER'], exist_ok=True)
    except OSError:
        pass

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from app.departments.routes import departments_bp
    from app.auth.routes import auth_bp
    from app.coordinator.routes import coordinator_bp
    from app.approvals.routes import approvals_bp
    from app.admin.routes import admin_bp
    from app.reports.routes import reports_bp

    app.register_blueprint(departments_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(coordinator_bp, url_prefix='/coordinator')
    app.register_blueprint(approvals_bp, url_prefix='/approvals')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(reports_bp, url_prefix='/reports')

    # Global context processor
    @app.context_processor
    def inject_globals():
        from app.models import Event
        event = Event.query.filter_by(is_active=True).first() or Event.query.first()
        return {'event': event}

    # Custom Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', error_code=404, error_message="The sacred page you seek was not found."), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('base.html', error_code=403, error_message="Access Restricted: Dignitary Authorization Required."), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('base.html', error_code=500, error_message="An internal server error occurred."), 500

    # Auto-initialize database tables and seed sample data
    with app.app_context():
        db.create_all()
        from app.seed import seed_database
        seed_database(app)

    return app

