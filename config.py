import os
from datetime import timedelta

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:////tmp/revobank.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Test database
    TEST_DATABASE_URI = os.getenv('DATABASE_TEST_URL', 'sqlite:///:memory:')
    
    # JWT configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
    # JWT token expiration (1 hour in seconds)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', '3600'))
    
    # Flask configuration
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Rate limiting
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '100/hour')
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')
    
    # Security settings
    MINIMUM_BALANCE = float(os.getenv('MINIMUM_BALANCE', '100000.0'))
    HIGH_VALUE_THRESHOLD = float(os.getenv('HIGH_VALUE_THRESHOLD', '50000000.0'))
    MAX_FAILED_LOGIN_ATTEMPTS = int(os.getenv('MAX_FAILED_LOGIN_ATTEMPTS', '5'))
    ACCOUNT_LOCKOUT_DURATION = int(os.getenv('ACCOUNT_LOCKOUT_DURATION', '900'))  # 15 minutes
    
    # Server configuration
    workers = int(os.getenv('GUNICORN_WORKERS', '2'))
    bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"