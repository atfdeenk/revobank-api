import pytest
from app import create_app, db
from app.models.user import User
from app.models.account import Account

@pytest.fixture
def app():
    app = create_app('testing')
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def init_database(app):
    with app.app_context():
        db.create_all()
        
        # Create test user
        user = User(
            username='testuser',
            name='Test User',
            email='test@example.com'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        # Create test account
        account = Account(
            account_type='savings',
            balance=100000.0,
            user_id=user.id
        )
        db.session.add(account)
        db.session.commit()

        yield db  # this is where the testing happens

        db.drop_all()
