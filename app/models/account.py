from app import db
from datetime import datetime
import random

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_number = db.Column(db.String(16), unique=True, nullable=False)
    account_type = db.Column(db.String(20), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='IDR')
    status = db.Column(db.String(10), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Outgoing transactions (where this account is the source)
    transactions = db.relationship('Transaction',
                                  foreign_keys='Transaction.account_id',
                                  backref='source_account',
                                  lazy=True)
    
    # Incoming transactions (where this account is the recipient)
    received_transactions = db.relationship('Transaction',
                                          foreign_keys='Transaction.recipient_account_id',
                                          backref='recipient_account',
                                          lazy=True)

    ACCOUNT_TYPES = {
        'savings': {
            'prefix': '38',  # BNI Savings prefix
            'min_balance': 100000.0,
            'description': 'Basic savings account with standard interest rate'
        },
        'checking': {
            'prefix': '39',  # BNI Checking prefix
            'min_balance': 500000.0,
            'description': 'Everyday checking account for regular transactions'
        },
        'business': {
            'prefix': '37',  # BNI Business prefix
            'min_balance': 1000000.0,
            'description': 'Business account with higher transaction limits'
        },
        'student': {
            'prefix': '36',  # BNI Student prefix
            'min_balance': 10000.0,
            'description': 'Student account with no monthly fees'
        }
    }

    @staticmethod
    def generate_account_number(account_type):
        if account_type not in Account.ACCOUNT_TYPES:
            raise ValueError(f'Invalid account type. Must be one of: {list(Account.ACCOUNT_TYPES.keys())}')
            
        prefix = Account.ACCOUNT_TYPES[account_type]['prefix']
        # Generate 14 random digits (16 total - 2 prefix)
        random_digits = ''.join([str(random.randint(0, 9)) for _ in range(14)])
        return f'{prefix}{random_digits}'

    @property
    def minimum_balance(self):
        return self.ACCOUNT_TYPES[self.account_type]['min_balance']

    @property
    def account_description(self):
        return self.ACCOUNT_TYPES[self.account_type]['description']

    def to_dict(self):
        return {
            'id': self.id,
            'account_number': self.account_number,
            'account_type': self.account_type,
            'balance': self.balance,
            'currency': self.currency,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'minimum_balance': self.minimum_balance,
            'description': self.account_description
        }
