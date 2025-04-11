from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.user import User
from app import db

def require_permissions(*required_permissions):
    """
    Decorator to check if user has required permissions
    Usage: @require_permissions('account:view_all', 'transaction:approve')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = db.session.get(User, user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Check if user has all required permissions
            missing_permissions = [
                perm for perm in required_permissions 
                if not user.has_permission(perm)
            ]
            
            if missing_permissions:
                return jsonify({
                    'error': 'Insufficient permissions',
                    'missing_permissions': missing_permissions
                }), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def require_role(role_name):
    """
    Decorator to check if user has required role
    Usage: @require_role('admin')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = db.session.get(User, user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if not user.has_role(role_name):
                return jsonify({
                    'error': 'Insufficient role',
                    'required_role': role_name
                }), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator
