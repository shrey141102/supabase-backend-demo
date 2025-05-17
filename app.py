from flask import Flask, jsonify, g, request
from datetime import datetime
from database import db, init_db, shutdown_session
from routes.identify import identify_bp
from config import PORT, DEBUG, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configure SQLAlchemy
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    
    # Initialize the app with SQLAlchemy
    db.init_app(app)
    
    # Initialize the database within the app context
    with app.app_context():
        try:
            init_db()
            app.logger.info("Database initialized successfully")
        except Exception as e:
            app.logger.error(f"Error initializing database: {str(e)}")
    
    # Register blueprints
    app.register_blueprint(identify_bp)
    
    # Add health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'ok'}), 200
    
    # Add a root endpoint for easier testing
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'service': 'Bitespeed Identity Reconciliation API',
            'status': 'running',
            'endpoints': {
                '/health': 'Health check',
                '/identify': 'Identity reconciliation (POST)'
            }
        }), 200
    
    # Register teardown function to clean up resources
    @app.teardown_appcontext
    def teardown_db(exception=None):
        shutdown_session(exception)
    
    # Add request hooks for logging
    @app.before_request
    def before_request():
        g.start_time = datetime.now()
    
    @app.after_request
    def after_request(response):
        diff = datetime.now() - g.start_time
        app.logger.info(f"Request processed in {diff.total_seconds():.4f}s: {request.method} {request.path}")
        return response
    
    return app

# This is for running locally
if __name__ == '__main__':
    # Create the Flask app
    app = create_app()
    
    # Run with Flask's built-in server
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)