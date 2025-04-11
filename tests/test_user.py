import pytest
from app.models.user import User
from app.models.role import Role
from app import db
from flask_jwt_extended import create_access_token
from datetime import datetime, timezone

@pytest.fixture(autouse=True)
def setup_database(app):
    """Set up a clean database before each test"""
    with app.app_context():
        db.create_all()
        
        # Create default roles
        customer_role = Role(name=Role.CUSTOMER)
        admin_role = Role(name=Role.ADMIN)
        teller_role = Role(name=Role.TELLER)
        
        db.session.add(customer_role)
        db.session.add(admin_role)
        db.session.add(teller_role)
        db.session.commit()
        
        yield
        db.session.remove()
        db.drop_all()

def test_register(client):
    """Test user registration"""
    response = client.post('/users', json={
        'username': 'testuser',
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'Test123!'
    })
    assert response.status_code == 201
    assert b'User registered successfully' in response.data
    
    # Verify user exists
    user = User.query.filter_by(email='test@example.com').first()
    assert user is not None
    assert user.name == 'Test User'
    assert user.check_password('Test123!')

def test_register_invalid_data(client):
    """Test registration with invalid data"""
    # Missing fields
    response = client.post('/users', json={
        'email': 'test@example.com'
    })
    assert response.status_code == 400
    assert 'Missing required fields' in response.json['error']

    # Invalid email
    response = client.post('/users', json={
        'username': 'testuser',
        'name': 'Test User',
        'email': 'invalid-email',
        'password': 'Test123!'
    })
    assert response.status_code == 400
    assert 'Invalid email format' in response.json['error']

    # Short username
    response = client.post('/users', json={
        'username': 'te',
        'name': 'Test User',
        'email': 'test2@example.com',
        'password': 'Test123!'
    })
    assert response.status_code == 400
    assert 'Username must be at least 3 characters' in response.json['error']

    # Weak password
    response = client.post('/users', json={
        'username': 'testuser2',
        'name': 'Test User',
        'email': 'test2@example.com',
        'password': '123'
    })
    assert response.status_code == 400
    assert 'Password must be at least 8 characters long' in response.json['error']

def test_login(client):
    """Test user login"""
    # Create a test user
    customer_role = Role.query.filter_by(name=Role.CUSTOMER).first()
    user = User(
        username='testuser',
        name='Test User',
        email='test@example.com',
        role=customer_role
    )
    user.set_password('Test123!')
    db.session.add(user)
    db.session.commit()
    
    # Test valid login
    response = client.post('/users/login', json={
        'username': 'testuser',
        'password': 'Test123!'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json
    assert 'refresh_token' in response.json
    
    # Test invalid password
    response = client.post('/users/login', json={
        'username': 'testuser',
        'password': 'wrong'
    })
    assert response.status_code == 401
    
    # Test non-existent user
    response = client.post('/users/login', json={
        'username': 'nonexistent',
        'password': 'Test123!'
    })
    assert response.status_code == 401

def test_profile(client):
    """Test profile endpoints"""
    # Create test user
    customer_role = Role.query.filter_by(name=Role.CUSTOMER).first()
    user = User(
        username='testuser',
        name='Test User',
        email='test@example.com',
        role=customer_role
    )
    user.set_password('Test123!')
    db.session.add(user)
    db.session.commit()
    
    # Create access token with claims
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
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Test get profile
    response = client.get('/users/me', headers=headers)
    assert response.status_code == 200
    assert response.json['email'] == 'test@example.com'
    
    # Test update profile
    response = client.put('/users/me', headers=headers, json={
        'name': 'Updated Name',
        'email': 'updated@example.com'
    })
    assert response.status_code == 200
    
    # Verify updates
    user = db.session.get(User, user.id)
    assert user.name == 'Updated Name'
    assert user.email == 'updated@example.com'

def test_refresh_token(client):
    """Test token refresh"""
    # Create test user
    customer_role = Role.query.filter_by(name=Role.CUSTOMER).first()
    user = User(
        username='testuser',
        name='Test User',
        email='test@example.com',
        role=customer_role
    )
    user.set_password('Test123!')
    db.session.add(user)
    db.session.commit()
    
    # Login to get tokens
    response = client.post('/users/login', json={
        'username': 'testuser',
        'password': 'Test123!'
    })
    refresh_token = response.json['refresh_token']
    
    # Test token refresh
    response = client.post('/users/refresh', headers={
        'Authorization': f'Bearer {refresh_token}'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_logout(client):
    """Test logout"""
    # Create test user
    customer_role = Role.query.filter_by(name=Role.CUSTOMER).first()
    user = User(
        username='testuser',
        name='Test User',
        email='test@example.com',
        role=customer_role
    )
    user.set_password('Test123!')
    db.session.add(user)
    db.session.commit()
    
    response = client.post('/users/login', json={
        'username': 'testuser',
        'password': 'Test123!'
    })
    access_token = response.json['access_token']
    
    # Test logout
    response = client.post('/users/logout', headers={
        'Authorization': f'Bearer {access_token}'
    })
    assert response.status_code == 200
    
    # Verify token is blacklisted
    response = client.get('/users/me', headers={
        'Authorization': f'Bearer {access_token}'
    })
    assert response.status_code == 401
