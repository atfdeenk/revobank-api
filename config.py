import os
from datetime import timedelta

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///revobank.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Flask configuration
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Gunicorn configuration (used in production)
    workers = int(os.getenv('GUNICORN_WORKERS', '2'))
    bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"