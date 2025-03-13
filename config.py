class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///revobank.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'your-secret-key'  # Change in production