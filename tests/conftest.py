import pytest
from datetime import datetime, UTC
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
        savings_account = Account(
            account_type='savings',
            account_number='38' + '0' * 14,  # Savings prefix
            balance=1000000.0,  # Well above 100k minimum
            user_id=user.id,
            status='active'
        )
        checking_account = Account(
            account_type='checking',
            account_number='39' + '0' * 14,  # Checking prefix
            balance=2000000.0,  # Well above 500k minimum
            user_id=user.id,
            status='active'
        )
        db.session.add(savings_account)
        db.session.add(checking_account)
        db.session.commit()

        # Create sample transactions with proper relationships
        timestamp = datetime.now(UTC)
        
        # Initial deposit to savings account
        deposit = Transaction(
            reference_number=f'TRX{int(timestamp.timestamp())}001',
            amount=50000.0,
            type='deposit',
            status='completed',
            description='Initial deposit',
            account_id=savings_account.id,
            timestamp=timestamp
        )
        db.session.add(deposit)
        db.session.commit()
        
        # Transfer from savings to checking
        transfer = Transaction(
            reference_number=f'TRX{int(timestamp.timestamp())}002',
            amount=20000.0,
            type='transfer',
            status='completed',
            description='Test transfer',
            account_id=savings_account.id,
            recipient_account_id=checking_account.id,
            timestamp=timestamp
        )
        db.session.add(transfer)
        db.session.commit()


        yield db  # this is where the testing happens

        db.drop_all()
