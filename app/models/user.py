from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, UTC
from .role import Role

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    accounts = db.relationship('Account', backref='owner', lazy=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    role = db.relationship('Role', backref=db.backref('users', lazy=True))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_permission(self, permission):
        """Check if user has a specific permission"""
        return permission in (self.role.permissions or [])

    def has_role(self, role_name):
        """Check if user has a specific role"""
        return self.role.name == role_name

    @property
    def is_admin(self):
        """Check if user is an admin"""
        return self.has_role(Role.ADMIN)

    @property
    def is_teller(self):
        """Check if user is a teller"""
        return self.has_role(Role.TELLER)
