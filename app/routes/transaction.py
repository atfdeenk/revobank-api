from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.transaction import Transaction
from app.models.account import Account
from app.models.role import Role
from app.utils.decorators import require_permissions, require_role
from app import db, limiter
from datetime import datetime, UTC

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/admin/all', methods=['GET'])
@jwt_required()
@require_permissions(Role.PERMISSIONS['transaction']['view_all'])
@limiter.limit("30 per minute")
def get_all_transactions():
    """Get all transactions (admin only) with optimized querying"""
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    # Validate pagination parameters
    if page < 1:
        return jsonify({'error': 'Page must be greater than 0'}), 400
    if not 1 <= limit <= 100:
        return jsonify({'error': 'Limit must be between 1 and 100'}), 400

    # Build optimized query with eager loading
    query = Transaction.query.options(
        db.joinedload(Transaction.source_account),
        db.joinedload(Transaction.recipient_account)
    )
    
    # Apply filters if provided with validation
    if account_id := request.args.get('account_id'):
        try:
            account_id = int(account_id)
            query = query.filter(Transaction.account_id == account_id)
        except ValueError:
            return jsonify({'error': 'Invalid account ID format'}), 400
            
    if type_ := request.args.get('type'):
        if type_ not in ['deposit', 'withdraw', 'transfer']:
            return jsonify({'error': 'Invalid transaction type'}), 400
        query = query.filter(Transaction.type == type_)
        
    if start_date := request.args.get('start_date'):
        try:
            start_date = datetime.fromisoformat(start_date)
            query = query.filter(Transaction.timestamp >= start_date)
        except ValueError:
            return jsonify({'error': 'Invalid start_date format. Use ISO format'}), 400
            
    if end_date := request.args.get('end_date'):
        try:
            end_date = datetime.fromisoformat(end_date)
            query = query.filter(Transaction.timestamp <= end_date)
        except ValueError:
            return jsonify({'error': 'Invalid end_date format. Use ISO format'}), 400
            
    if status := request.args.get('status'):
        if status not in Transaction.STATUS_CHOICES:
            return jsonify({'error': 'Invalid status'}), 400
        query = query.filter(Transaction.status == status)

    # Get paginated results
    pagination = query.order_by(Transaction.timestamp.desc()).paginate(
        page=page, per_page=limit, error_out=False)

    return jsonify({
        'transactions': [{
            'id': t.id,
            'type': t.type,
            'amount': t.amount,
            'description': t.description,
            'reference_number': t.reference_number,
            'account_id': t.account_id,
            'recipient_account_id': t.recipient_account_id,
            'timestamp': t.timestamp,
            'status': t.status
        } for t in pagination.items],
        'pagination': {
            'total_items': pagination.total,
            'total_pages': pagination.pages,
            'current_page': page,
            'limit': limit,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev,
            'next_page': page + 1 if pagination.has_next else None,
            'prev_page': page - 1 if pagination.has_prev else None
        }
    })

@transaction_bp.route('/admin/approve/<int:transaction_id>', methods=['POST'])
@jwt_required()
@require_permissions(Role.PERMISSIONS['transaction']['approve'])
@limiter.limit("30 per minute")
def approve_transaction(transaction_id):
    """Approve a pending transaction (admin/teller only)"""
    transaction = Transaction.query.get_or_404(transaction_id)
    
    if transaction.status != 'pending_approval':
        return jsonify({'error': 'Transaction is not pending approval'}), 400

    # Get source and destination accounts
    source_account = Account.query.get_or_404(transaction.account_id)
    if transaction.recipient_account_id:
        dest_account = Account.query.get_or_404(transaction.recipient_account_id)

    try:
        # For transfers, update both accounts
        if transaction.type == 'transfer':
            source_account.balance -= transaction.amount
            dest_account.balance += transaction.amount
        # For withdrawals, just update source account
        elif transaction.type == 'withdraw':
            source_account.balance -= transaction.amount
        # For deposits, just update destination account
        elif transaction.type == 'deposit':
            source_account.balance += transaction.amount

        transaction.status = 'completed'
        db.session.commit()

        return jsonify({
            'message': 'Transaction approved successfully',
            'transaction': {
                'id': transaction.id,
                'type': transaction.type,
                'amount': transaction.amount,
                'status': transaction.status,
                'reference_number': transaction.reference_number
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@transaction_bp.route('/', methods=['GET'])
@jwt_required()
@require_permissions(Role.PERMISSIONS['transaction']['view_own'])
@limiter.limit("30 per minute")
def get_transactions():
    """Get all transactions for the user's accounts with pagination support
    
    Query Parameters:
        page (int): Page number (default: 1)
        limit (int): Items per page (default: 20, max: 100)
        account_id (int, optional): Filter by account ID
        type (str, optional): Filter by transaction type (deposit, withdraw, transfer)
        start_date (str, optional): Filter by start date (ISO format)
        end_date (str, optional): Filter by end date (ISO format)
        
    Returns:
        JSON response with:
        - List of transactions for the current page
        - Pagination metadata (total_items, total_pages, current_page, etc.)
    """
    user_id = get_jwt_identity()
    account_id = request.args.get('account_id')
    transaction_type = request.args.get('type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    # Validate pagination parameters
    if page < 1:
        return jsonify({'error': 'Page number must be greater than 0'}), 400
    if limit < 1 or limit > 100:
        return jsonify({'error': 'Limit must be between 1 and 100'}), 400
    
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
    
    # Combine queries using union
    all_transactions_query = sent_query.union(received_query).order_by(Transaction.timestamp.desc())
    
    # Apply pagination
    paginated_transactions = all_transactions_query.paginate(page=page, per_page=limit, error_out=False)
    
    return jsonify({
        'transactions': [t.to_dict() for t in paginated_transactions.items],
        'pagination': {
            'total_items': paginated_transactions.total,
            'total_pages': paginated_transactions.pages,
            'current_page': page,
            'limit': limit,
            'has_next': paginated_transactions.has_next,
            'has_prev': paginated_transactions.has_prev,
            'next_page': paginated_transactions.next_num if paginated_transactions.has_next else None,
            'prev_page': paginated_transactions.prev_num if paginated_transactions.has_prev else None
        }
    })

@transaction_bp.route('/<int:transaction_id>', methods=['GET'])
@jwt_required()
@require_permissions(Role.PERMISSIONS['transaction']['view_own'])
def get_transaction(transaction_id):
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
@require_permissions(Role.PERMISSIONS['transaction']['create'])
@limiter.limit("20 per minute")
def deposit():
    """Deposit money into an account with ACID guarantees"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    if not data or 'account_id' not in data or 'amount' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate amount
    try:
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid amount'}), 400
    
    # Verify account ownership and status
    account = Account.query.filter_by(id=data['account_id'], user_id=user_id).first_or_404()
    if account.status != 'active':
        return jsonify({'error': f'Account is {account.status}'}), 400
    
    try:
        # Start a transaction block
        db.session.begin_nested()
        
        # Lock the account for update
        account = db.session.get(Account, account.id, with_for_update=True)
        
        # Create transaction record
        transaction = Transaction(
            type='deposit',
            amount=amount,
            account_id=account.id,
            description=data.get('description', 'Deposit'),
            reference_number=Transaction.generate_reference_number(),
            status='completed'
        )
        
        # Update balance
        account.balance += amount
        
        # Save changes
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
@limiter.limit("20 per minute")
def withdraw():
    """Withdraw money from an account with ACID guarantees"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    if not data or 'account_id' not in data or 'amount' not in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Validate amount
    try:
        amount = float(data['amount'])
        if amount <= 0:
            return jsonify({'error': 'Amount must be positive'}), 400
    except ValueError:
        return jsonify({'error': 'Invalid amount'}), 400
    
    # Verify account ownership and status
    account = Account.query.filter_by(id=data['account_id'], user_id=user_id).first_or_404()
    if account.status != 'active':
        return jsonify({'error': f'Account is {account.status}'}), 400
    
    try:
        # Start a transaction block
        db.session.begin_nested()
        
        # Lock the account for update
        account = db.session.get(Account, account.id, with_for_update=True)
        
        # Check sufficient balance
        if account.balance - amount < account.minimum_balance:
            return jsonify({
                'error': 'Insufficient funds',
                'current_balance': account.balance,
                'minimum_balance': account.minimum_balance
            }), 400
        
        # Create transaction record
        transaction = Transaction(
            type='withdraw',
            amount=amount,
            account_id=account.id,
            description=data.get('description', 'Withdrawal'),
            reference_number=Transaction.generate_reference_number(),
            status='completed'
        )
        
        # Update balance
        account.balance -= amount
        
        # Save changes
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
@limiter.limit("20 per minute")
def transfer():
    """Transfer money between accounts with ACID guarantees
    
    Requires:
    - from_account_id: source account ID
    - to_account_id: destination account ID
    - amount: amount to transfer
    - description (optional): transaction description
    
    This function uses SQLAlchemy's session management to ensure:
    - Atomicity: Both debit and credit operations succeed or fail together
    - Consistency: Account balances and constraints are maintained
    - Isolation: Concurrent transfers don't interfere
    - Durability: Committed transactions persist
    """
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
    from_account_id = data['from_account_id']
    source_account = Account.query.filter_by(id=from_account_id, user_id=user_id).first_or_404()
    
    # Verify recipient account exists
    to_account_id = data['to_account_id']
    recipient_account = Account.query.filter_by(id=to_account_id).first_or_404()
    
    # Validate account statuses
    if source_account.status != 'active':
        return jsonify({'error': f'Source account is {source_account.status}'}), 400
    if recipient_account.status != 'active':
        return jsonify({'error': f'Recipient account is {recipient_account.status}'}), 400
    
    # Check sufficient balance (only for immediate transfers)
    requires_approval = Transaction.requires_approval(amount)
    if not requires_approval and source_account.balance - amount < source_account.minimum_balance:
        return jsonify({
            'error': 'Insufficient funds',
            'current_balance': source_account.balance,
            'minimum_balance': source_account.minimum_balance
        }), 400
    
    try:
        # Start a transaction block
        db.session.begin_nested()
        try:
            # Create the transaction record
            transaction = Transaction(
                type='transfer',
                amount=amount,
                account_id=from_account_id,
                recipient_account_id=to_account_id,
                description=data.get('description', f'Transfer to account {recipient_account.account_number}'),
                reference_number=Transaction.generate_reference_number(),
                status=Transaction.STATUS_PENDING_APPROVAL if requires_approval else Transaction.STATUS_COMPLETED
            )
            db.session.add(transaction)
            
            # Update account balances
            if not requires_approval:
                # Lock the accounts for update to prevent race conditions
                from_account = db.session.get(Account, from_account_id, with_for_update=True)
                to_account = db.session.get(Account, to_account_id, with_for_update=True)
                
                from_account.balance -= amount
                to_account.balance += amount
                
                # Verify constraints after update
                if from_account.balance < from_account.minimum_balance:
                    raise ValueError(f'Transfer would put account below minimum balance of {from_account.minimum_balance}')
            
            db.session.commit()
            
            if requires_approval:
                return jsonify({
                    'message': 'Transfer pending approval',
                    'transaction': transaction.to_dict()
                }), 202
            else:
                return jsonify({
                    'message': 'Transfer successful',
                    'transaction': transaction.to_dict()
                }), 201
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
        if not Transaction.requires_approval(amount):
            source_account.balance -= amount
            recipient_account.balance += amount
        
        db.session.add(transaction)
        db.session.commit()
        
        if Transaction.requires_approval(amount):
            return jsonify({
                'message': 'Transfer pending approval',
                'transaction': transaction.to_dict()
            }), 202
        else:
            return jsonify({
                'message': 'Transfer successful',
                'transaction': transaction.to_dict()
            }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500