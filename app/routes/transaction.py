from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.transaction import Transaction
from app.models.account import Account
from app import db
from datetime import datetime

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('', methods=['GET'])
@jwt_required()
def get_transactions():
    """Get all transactions for the user's accounts"""
    user_id = get_jwt_identity()
    account_id = request.args.get('account_id')
    transaction_type = request.args.get('type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Get user's accounts
    accounts = Account.query.filter_by(user_id=user_id).all()
    account_ids = [account.id for account in accounts]
    
    # Build base query for both sent and received transactions
    sent_query = Transaction.query.filter(Transaction.account_id.in_(account_ids))
    received_query = Transaction.query.filter(Transaction.recipient_account_id.in_(account_ids))
    
    # Apply filters
    if account_id:
        account_id = int(account_id)
        if account_id not in account_ids:
            return jsonify({'error': 'Account not found'}), 404
        sent_query = sent_query.filter_by(account_id=account_id)
        received_query = received_query.filter_by(recipient_account_id=account_id)
    
    if transaction_type:
        if transaction_type not in Transaction.TRANSACTION_TYPES:
            return jsonify({
                'error': 'Invalid transaction type',
                'valid_types': Transaction.TRANSACTION_TYPES
            }), 400
        sent_query = sent_query.filter_by(type=transaction_type)
        received_query = received_query.filter_by(type=transaction_type)
    
    if start_date:
        try:
            start_date = datetime.fromisoformat(start_date)
            sent_query = sent_query.filter(Transaction.timestamp >= start_date)
            received_query = received_query.filter(Transaction.timestamp >= start_date)
        except ValueError:
            return jsonify({'error': 'Invalid start_date format. Use ISO format'}), 400
    
    if end_date:
        try:
            end_date = datetime.fromisoformat(end_date)
            sent_query = sent_query.filter(Transaction.timestamp <= end_date)
            received_query = received_query.filter(Transaction.timestamp <= end_date)
        except ValueError:
            return jsonify({'error': 'Invalid end_date format. Use ISO format'}), 400
    
    # Combine and sort transactions
    all_transactions = sent_query.all() + received_query.all()
    all_transactions.sort(key=lambda x: x.timestamp, reverse=True)
    
    return jsonify({
        'transactions': [t.to_dict() for t in all_transactions]
    })

@transaction_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_transaction(id):
    """Get a specific transaction"""
    user_id = get_jwt_identity()
    accounts = Account.query.filter_by(user_id=user_id).all()
    account_ids = [account.id for account in accounts]
    
    transaction = Transaction.query.filter_by(id=id).first_or_404()
    
    # Check if user has access to this transaction
    if transaction.account_id not in account_ids and \
       (transaction.recipient_account_id is None or transaction.recipient_account_id not in account_ids):
        return jsonify({'error': 'Transaction not found'}), 404
    
    return jsonify(transaction.to_dict())

@transaction_bp.route('/deposit', methods=['POST'])
@jwt_required()
def deposit():
    """Deposit money into an account"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate required fields
    required_fields = ['account_id', 'amount']
    if not all(field in data for field in required_fields):
        return jsonify({'error': f'Missing required fields: {required_fields}'}), 400
    
    # Validate amount
    try:
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid amount'}), 400
    
    # Verify account ownership
    account = Account.query.filter_by(id=data['account_id'], user_id=user_id).first_or_404()
    
    if account.status != 'active':
        return jsonify({'error': f'Account is {account.status}'}), 400
    
    try:
        # Create transaction
        transaction = Transaction(
            type='deposit',
            amount=amount,
            account_id=account.id,
            description=data.get('description', 'Deposit'),
            reference_number=Transaction.generate_reference_number()
        )
        
        # Update account balance
        account.balance += amount
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Deposit successful',
            'transaction': transaction.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@transaction_bp.route('/withdraw', methods=['POST'])
@jwt_required()
def withdraw():
    """Withdraw money from an account"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate required fields
    required_fields = ['account_id', 'amount']
    if not all(field in data for field in required_fields):
        return jsonify({'error': f'Missing required fields: {required_fields}'}), 400
    
    # Validate amount
    try:
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid amount'}), 400
    
    # Verify account ownership
    account = Account.query.filter_by(id=data['account_id'], user_id=user_id).first_or_404()
    
    if account.status != 'active':
        return jsonify({'error': f'Account is {account.status}'}), 400
    
    # Check sufficient balance
    if account.balance - amount < account.minimum_balance:
        return jsonify({
            'error': 'Insufficient funds',
            'current_balance': account.balance,
            'minimum_balance': account.minimum_balance
        }), 400
    
    try:
        # Create transaction
        transaction = Transaction(
            type='withdraw',
            amount=amount,
            account_id=account.id,
            description=data.get('description', 'Withdrawal'),
            reference_number=Transaction.generate_reference_number()
        )
        
        # Update account balance
        account.balance -= amount
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Withdrawal successful',
            'transaction': transaction.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@transaction_bp.route('/transfer', methods=['POST'])
@jwt_required()
def transfer():
    """Transfer money between accounts"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate required fields
    required_fields = ['from_account_id', 'to_account_id', 'amount']
    if not all(field in data for field in required_fields):
        return jsonify({'error': f'Missing required fields: {required_fields}'}), 400
    
    # Validate amount
    try:
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid amount'}), 400
    
    # Verify source account ownership
    source_account = Account.query.filter_by(id=data['from_account_id'], user_id=user_id).first_or_404()
    
    # Verify recipient account exists
    recipient_account = Account.query.filter_by(id=data['to_account_id']).first_or_404()
    
    # Validate account statuses
    if source_account.status != 'active':
        return jsonify({'error': f'Source account is {source_account.status}'}), 400
    if recipient_account.status != 'active':
        return jsonify({'error': f'Recipient account is {recipient_account.status}'}), 400
    
    # Check sufficient balance
    if source_account.balance - amount < source_account.minimum_balance:
        return jsonify({
            'error': 'Insufficient funds',
            'current_balance': source_account.balance,
            'minimum_balance': source_account.minimum_balance
        }), 400
    
    try:
        # Create transfer transaction
        transaction = Transaction(
            type='transfer',
            amount=amount,
            account_id=source_account.id,
            recipient_account_id=recipient_account.id,
            description=data.get('description', f'Transfer to account {recipient_account.account_number}'),
            reference_number=Transaction.generate_reference_number()
        )
        
        # Update account balances
        source_account.balance -= amount
        recipient_account.balance += amount
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Transfer successful',
            'transaction': transaction.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500