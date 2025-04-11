from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt,
    set_access_cookies, set_refresh_cookies
)
from datetime import datetime, timezone, timedelta
from app.models.user import User
from app.models.role import Role
from app import db, limiter

user_bp = Blueprint('user', __name__)

# In-memory token blacklist (for testing)
# In production, use Redis or a database table
token_blacklist = set()

@user_bp.route('', methods=['POST'])
@limiter.limit("20 per minute")
def create_user():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    required_fields = ['username', 'password', 'name', 'email']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields', 'required': required_fields}), 400

    # Validate username format
    username = data['username'].strip()
    if not username or len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 400
        
    # Validate email format
    email = data['email'].strip().lower()
    if not email or '@' not in email:
        return jsonify({'error': 'Invalid email format'}), 400
        
    # Validate password
    password = data['password']
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
    # Check for existing username/email using parameterized queries
    if User.query.filter(User.username == username).first():
        return jsonify({'error': 'Username already exists'}), 400
    if User.query.filter(User.email == email).first():
        return jsonify({'error': 'Email already exists'}), 400

    try:
        # Get customer role
        customer_role = Role.query.filter_by(name=Role.CUSTOMER).first()
        if not customer_role:
            return jsonify({'error': 'System configuration error: customer role not found'}), 500
            
        user = User(
            username=data['username'],
            name=data['name'],
            email=data['email'],
            role=customer_role
        )
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create user'}), 500

@user_bp.route('/login', methods=['POST'])
@limiter.limit("30 per minute, 300 per hour")
def login():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required'}), 400

    username = data['username'].strip()
    user = User.query.filter(User.username == username).first()
    if user and user.check_password(data['password']):
        # Create tokens with additional claims
        additional_claims = {
            'username': user.username,
            'email': user.email,
            'iat': datetime.now(timezone.utc)
        }
        
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims=additional_claims,
            fresh=True
        )
        refresh_token = create_refresh_token(
            identity=str(user.id),
            additional_claims=additional_claims
        )
        
        response = jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': int(timedelta(minutes=15).total_seconds()),  # 15 minutes
            'user': {
                'id': user.id,
                'username': user.username,
                'name': user.name,
                'email': user.email
            }
        })
        
        # Set secure cookie headers
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Pragma'] = 'no-cache'
        
        return response
    return jsonify({'error': 'Invalid credentials'}), 401

@user_bp.route('/me', methods=['GET'])
@jwt_required()
@limiter.limit("60 per minute")
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'name': user.name,
        'email': user.email
    })

@user_bp.route('/me', methods=['PUT'])
@jwt_required()
@limiter.limit("40 per minute")
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        # Only allow updating name and email
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            email = data['email'].strip().lower()
            if not email or '@' not in email:
                return jsonify({'error': 'Invalid email format'}), 400
            if User.query.filter(User.id != user_id, User.email == email).first():
                return jsonify({'error': 'Email already exists'}), 400
            user.email = data['email']
        if 'password' in data:
            user.set_password(data['password'])

        db.session.commit()
        return jsonify({'message': 'Profile updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update profile'}), 500

@user_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@limiter.limit("30 per minute")
def refresh():
    """Refresh access token using refresh token"""
    identity = get_jwt_identity()
    claims = get_jwt()
    
    # Create new access token with original claims
    additional_claims = {
        'username': claims.get('username'),
        'email': claims.get('email'),
        'iat': datetime.now(timezone.utc)
    }
    
    access_token = create_access_token(
        identity=identity,
        additional_claims=additional_claims,
        fresh=False  # Refreshed tokens are not fresh
    )
    
    response = jsonify({
        'access_token': access_token,
        'token_type': 'Bearer',
        'expires_in': int(timedelta(minutes=15).total_seconds())  # 15 minutes
    })
    
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Pragma'] = 'no-cache'
    
    return response

@user_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user and revoke current token"""
    jti = get_jwt()['jti']  # Get JWT ID from token
    token_blacklist.add(jti)
    return jsonify({'message': 'Successfully logged out'})