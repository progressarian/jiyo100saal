"""
Jiyo100Saal Functional Aging Assessment
=======================================

Main Flask Application
"""

import utils.session
from flask import Flask, render_template, redirect, url_for
from config import get_config
from models.base import db
import os

def create_app(config_name: str = None) -> Flask:
    """
    Application factory pattern.
    
    Args:
        config_name: 'development', 'testing', or 'production'
    
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    config = get_config(config_name)
    app.config.from_object(config)
    
    # Initialize database
    db.init_app(config.DATABASE_URL, echo=config.SQLALCHEMY_ECHO)
    
    # Register blueprints
    from routes.section0 import section0_bp
    app.register_blueprint(section0_bp)
    
    from routes.section1 import section1_bp
    app.register_blueprint(section1_bp)
    
    from routes.patients import patients_bp
    app.register_blueprint(patients_bp)
    
    from routes.assessments import assessments_bp
    app.register_blueprint(assessments_bp)
    
    from routes.pillar1 import bp as pillar1_bp
    app.register_blueprint(pillar1_bp)
    
    from routes.pillar2 import bp as pillar2_bp
    app.register_blueprint(pillar2_bp)
    
    from routes.pillar3 import bp as pillar3_bp
    app.register_blueprint(pillar3_bp)
    
    from routes.pillar4 import bp as pillar4_bp
    app.register_blueprint(pillar4_bp)
    
    from routes.pillar5 import bp as pillar5_bp
    app.register_blueprint(pillar5_bp)
    
    from routes.reports import bp as reports_bp
    app.register_blueprint(reports_bp)
    
    # Home route
    @app.route('/')
    def index():
        """Home page - redirect to patients list."""
        return redirect(url_for('patients.list_patients'))
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500
    
    return app


# Create app instance for running directly
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

@app.route('/init-db-secret-2026')
def init_database():
    """Temporary route to initialize database"""
    try:
        with app.app_context():
            db.create_all()
        return "✅ Database initialized successfully! You can now use the app.", 200
    except Exception as e:
        return f"❌ Error: {str(e)}", 500
