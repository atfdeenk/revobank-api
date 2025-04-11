from app import db
from datetime import datetime, UTC

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # deposit, withdraw, transfer
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    recipient_account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=True)  # For transfers
    description = db.Column(db.String(200))
    reference_number = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(20), default='completed')  # completed, pending, failed

    # Valid transaction types
    TRANSACTION_TYPES = ['deposit', 'withdraw', 'transfer']
    
    # Valid transaction statuses
    STATUS_COMPLETED = 'completed'
    STATUS_PENDING_APPROVAL = 'pending_approval'
    STATUS_FAILED = 'failed'
    STATUS_CANCELLED = 'cancelled'
    
    STATUSES = [
        STATUS_COMPLETED,
        STATUS_PENDING_APPROVAL,
        STATUS_FAILED,
        STATUS_CANCELLED
    ]
    
    # High-value transaction threshold
    HIGH_VALUE_THRESHOLD = 50000000  # 50 million
    
    @staticmethod
    def requires_approval(amount):
        """Check if transaction requires approval based on amount"""
        return amount > Transaction.HIGH_VALUE_THRESHOLD
    
    @staticmethod
    def generate_reference_number():
        """Generate a unique reference number for the transaction"""
        import random
        import string
        prefix = datetime.now().strftime('%Y%m%d')
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return f'TRX{prefix}{suffix}'

    def to_dict(self):
        data = {
            'id': self.id,
            'reference_number': self.reference_number,
            'type': self.type,
            'amount': self.amount,
            'timestamp': self.timestamp.isoformat(),
            'description': self.description,
            'status': self.status,
            'account_id': self.account_id
        }
        if self.type == 'transfer' and self.recipient_account_id:
            data['recipient_account_id'] = self.recipient_account_id
        return data
