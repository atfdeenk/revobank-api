import os
from datetime import timedelta
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, get_jwt
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from sqlalchemy.exc import SQLAlchemyError
from config import Config

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",  # Use memory storage for development
    default_limits=["200 per day", "50 per hour"]  # Default limits
)

def create_app(config_name='default'):
    app = Flask(__name__)
    
    if config_name == 'testing':
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['JWT_SECRET_KEY'] = 'test-key'
    else:
        app.config.from_object(Config)
        # Override with environment variables if they exist
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', app.config['SQLALCHEMY_DATABASE_URI'])
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', app.config['JWT_SECRET_KEY'])
    
    # JWT Configuration for Banking Security
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)  # Access token expires in 15 minutes
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)    # Refresh token expires in 7 days
    app.config['JWT_ERROR_MESSAGE_KEY'] = 'error'
    app.config['JWT_COOKIE_SECURE'] = True  # Only send cookies over HTTPS
    app.config['JWT_COOKIE_CSRF_PROTECT'] = True  # Enable CSRF protection
    
    try:
        db.init_app(app)
        migrate.init_app(app, db)
        jwt.init_app(app)
        limiter.init_app(app)
        
        # Add token blacklist check
        @jwt.token_in_blocklist_loader
        def check_if_token_is_revoked(jwt_header, jwt_payload: dict) -> bool:
            from app.routes.user import token_blacklist
            jti = jwt_payload['jti']
            return jti in token_blacklist
        
        # JWT error handlers
        @jwt.expired_token_loader
        def expired_token_callback(jwt_header, jwt_payload):
            return jsonify({'error': 'Token has expired'}), 401

        @jwt.invalid_token_loader
        def invalid_token_callback(error):
            return jsonify({'error': 'Invalid token'}), 401

        @jwt.unauthorized_loader
        def missing_token_callback(error):
            return jsonify({'error': 'Authorization token is missing'}), 401

        @jwt.needs_fresh_token_loader
        def token_not_fresh_callback(jwt_header, jwt_payload):
            return jsonify({'error': 'Fresh token required'}), 401

        @jwt.revoked_token_loader
        def revoked_token_callback(jwt_header, jwt_payload):
            return jsonify({'error': 'Token has been revoked'}), 401
        
        # Test database connection
        with app.app_context():
            db.engine.connect()
    except Exception as e:
        app.logger.error(f'Failed to initialize database: {str(e)}')
        raise
    
    # Error handlers
    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(error):
        app.logger.error(f'Database error occurred: {str(error)}')
        return jsonify({'error': 'A database error occurred'}), 500

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy', 'message': 'Service is running'}), 200
    
    from app.routes import user_bp, account_bp, transaction_bp
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(account_bp, url_prefix='/accounts')
    app.register_blueprint(transaction_bp, url_prefix='/transactions')
    
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            # If tables already exist, continue
            app.logger.info(f'Database initialization: {str(e)}')
    
    return app