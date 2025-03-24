from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    if config_name == 'testing':
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['JWT_SECRET_KEY'] = 'test-key'
    else:
        app.config.from_object(Config)
    
    db.init_app(app)
    jwt.init_app(app)
    
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