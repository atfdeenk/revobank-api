import pytest
from datetime import datetime
from app import create_app, db
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction

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

        # Create test accounts with different types
        accounts = [
            Account(
                account_type='savings',
                account_number='38' + '0' * 14,  # Savings prefix
                balance=100000.0,
                user_id=user.id,
                status='active'
            ),
            Account(
                account_type='checking',
                account_number='39' + '0' * 14,  # Checking prefix
                balance=500000.0,
                user_id=user.id,
                status='active'
            )
        ]
        db.session.bulk_save_objects(accounts)
        db.session.commit()

        # Create sample transactions
        timestamp = datetime.utcnow()
        transactions = [
            Transaction(
                reference_number=f'TRX{int(timestamp.timestamp())}001',
                amount=50000.0,
                type='deposit',
                status='completed',
                description='Initial deposit',
                account_id=accounts[0].id,
                created_at=timestamp
            ),
            Transaction(
                reference_number=f'TRX{int(timestamp.timestamp())}002',
                amount=20000.0,
                type='transfer',
                status='completed',
                description='Test transfer',
                account_id=accounts[0].id,
                recipient_account_id=accounts[1].id,
                created_at=timestamp
            )
        ]
        db.session.bulk_save_objects(transactions)
        db.session.commit()

        yield db  # this is where the testing happens

        db.drop_all()
