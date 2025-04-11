from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.account import Account
from app.models.user import User
from app import db

account_bp = Blueprint('account', __name__)

@account_bp.route('/types', methods=['GET'])
def get_account_types():
    """Get all available account types and their details"""
    return jsonify({
        'account_types': {
            type_name: {
                'minimum_balance': details['min_balance'],
                'description': details['description']
            }
            for type_name, details in Account.ACCOUNT_TYPES.items()
        }
    })

@account_bp.route('', methods=['GET'])
@jwt_required()
def get_accounts():
    """Get all accounts for the authenticated user"""
    user_id = get_jwt_identity()
    
    # Get query parameters for filtering
    account_type = request.args.get('type')
    status = request.args.get('status', 'active')
    
    # Build query
    # Build base query with user_id filter
    query = Account.query.filter(Account.user_id == user_id)
    
    # Validate and apply account type filter
    if account_type:
        if account_type not in Account.ACCOUNT_TYPES:
            return jsonify({
                'error': 'Invalid account type',
                'available_types': list(Account.ACCOUNT_TYPES.keys())
            }), 400
        query = query.filter(Account.account_type == account_type)
    
    # Validate and apply status filter
    if status:
        if status not in ['active', 'inactive', 'frozen']:
            return jsonify({
                'error': 'Invalid status. Must be one of: active, inactive, frozen'
            }), 400
        query = query.filter(Account.status == status)
    
    accounts = query.all()
    return jsonify({
        'accounts': [account.to_dict() for account in accounts]
    })

@account_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_account(id):
    """Get a specific account by ID"""
    user_id = get_jwt_identity()
    account = Account.query.filter_by(id=id, user_id=user_id).first_or_404()
    return jsonify(account.to_dict())

@account_bp.route('', methods=['POST'])
@jwt_required()
def create_account():
    """Create a new bank account"""
    user_id = get_jwt_identity()
    data = request.get_json()

    # Validate request data
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    account_type = data.get('account_type')
    if not account_type:
        return jsonify({
            'error': 'Account type is required',
            'available_types': list(Account.ACCOUNT_TYPES.keys())
        }), 400

    if account_type not in Account.ACCOUNT_TYPES:
        return jsonify({
            'error': 'Invalid account type',
            'available_types': list(Account.ACCOUNT_TYPES.keys())
        }), 400

    # Check initial deposit
    initial_balance = float(data.get('initial_deposit', 0))
    min_balance = Account.ACCOUNT_TYPES[account_type]['min_balance']
    
    if initial_balance < min_balance:
        return jsonify({
            'error': f'Initial deposit must be at least {min_balance} IDR for {account_type} account'
        }), 400

    try:
        # Generate unique account number
        account_number = Account.generate_account_number(account_type)
        
        # Create account
        account = Account(
            account_number=account_number,
            account_type=account_type,
            balance=initial_balance,
            user_id=user_id
        )
        
        db.session.add(account)
        db.session.commit()
        
        return jsonify({
            'message': 'Account created successfully',
            'account': account.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating account: {str(e)}")
        return jsonify({'error': f'Failed to create account: {str(e)}'}), 500

@account_bp.route('/<int:id>', methods=['PUT', 'DELETE'])
@jwt_required()
def manage_account(id):
    """Update or delete a specific account"""
    user_id = get_jwt_identity()
    account = Account.query.filter_by(id=id, user_id=user_id).first_or_404()
    
    if request.method == 'DELETE':
        if account.balance > 0:
            return jsonify({
                'error': 'Cannot delete account with positive balance'
            }), 400
            
        try:
            db.session.delete(account)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to delete account'}), 500
    
    # Handle PUT request
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    # Only allow updating status
    if 'status' in data:
        if data['status'] not in ['active', 'inactive', 'frozen']:
            return jsonify({
                'error': 'Invalid status. Must be one of: active, inactive, frozen'
            }), 400
            
        try:
            account.status = data['status']
            db.session.commit()
            return jsonify({
                'message': 'Account updated successfully',
                'account': account.to_dict()
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to update account'}), 500
            
    return jsonify({
        'error': 'Only status can be updated'
    }), 400