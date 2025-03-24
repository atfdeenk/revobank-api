import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

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
    
    try:
        db.init_app(app)
        jwt.init_app(app)
        migrate.init_app(app, db)
        
        # Test database connection
        with app.app_context():
            db.engine.connect()
    except Exception as e:
        app.logger.error(f'Failed to initialize database: {str(e)}')
        raise
    
    # Error handlers
    @app.errorhandler(SQLAlchemy.SQLAlchemyError)
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