import pytest
from app.models.account import Account
from app.models.transaction import Transaction

def test_deposit(client, init_database):
    # Login as customer
    login_response = client.post('/users/login', json={
        'username': 'testuser',  # customer role
        'password': 'password123'
    })
    assert login_response.status_code == 200
    token = login_response.json['access_token']

    # Get savings account for deposit
    accounts_response = client.get('/accounts', headers={'Authorization': f'Bearer {token}'})
    assert accounts_response.status_code == 200
    savings_account = next(acc for acc in accounts_response.json['accounts'] 
                         if acc['account_number'].startswith('38'))

    # Make deposit
    response = client.post('/transactions/deposit', 
        json={
            'account_id': savings_account['id'],
            'amount': 50000.0,
            'description': 'Test deposit'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 201
    assert response.json['transaction']['amount'] == 50000.0
    assert response.json['transaction']['type'] == 'deposit'

def test_withdraw(client, init_database):
    # Login as customer
    login_response = client.post('/users/login', json={
        'username': 'testuser',  # customer role
        'password': 'password123'
    })
    assert login_response.status_code == 200
    token = login_response.json['access_token']

    # Get checking account for withdrawal
    accounts_response = client.get('/accounts', headers={'Authorization': f'Bearer {token}'})
    assert accounts_response.status_code == 200
    checking_account = next(acc for acc in accounts_response.json['accounts'] 
                          if acc['account_number'].startswith('39'))

    # Make withdrawal
    response = client.post('/transactions/withdraw',
        json={
            'account_id': checking_account['id'],
            'amount': 5000.0,
            'description': 'Test withdrawal'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 201
    assert response.json['transaction']['amount'] == 5000.0
    assert response.json['transaction']['type'] == 'withdraw'

def test_transfer(client, init_database):
    # Login as customer
    login_response = client.post('/users/login', json={
        'username': 'testuser',  # customer role
        'password': 'password123'
    })
    assert login_response.status_code == 200
    token = login_response.json['access_token']

    # Get both accounts for transfer
    accounts_response = client.get('/accounts', headers={'Authorization': f'Bearer {token}'})
    assert accounts_response.status_code == 200
    savings_account = next(acc for acc in accounts_response.json['accounts'] 
                         if acc['account_number'].startswith('38'))
    checking_account = next(acc for acc in accounts_response.json['accounts'] 
                          if acc['account_number'].startswith('39'))

    # Make transfer from savings to checking
    response = client.post('/transactions/transfer',
        json={
            'from_account_id': savings_account['id'],
            'to_account_id': checking_account['id'],
            'amount': 5000.0,
            'description': 'Test transfer'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 201
    assert response.json['transaction']['amount'] == 5000.0
    assert response.json['transaction']['type'] == 'transfer'
    assert response.json['transaction']['status'] == Transaction.STATUS_COMPLETED  # Small amount, no approval needed

    # Test high-value transfer that needs approval
    response = client.post('/transactions/transfer',
        json={
            'from_account_id': savings_account['id'],
            'to_account_id': checking_account['id'],
            'amount': 60000000.0,  # 60M, above threshold
            'description': 'High value transfer'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 202  # Accepted but pending
    assert response.json['transaction']['status'] == Transaction.STATUS_PENDING_APPROVAL
    
    # Login as admin to approve the transfer
    admin_login = client.post('/users/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    admin_token = admin_login.json['access_token']
    
    # Approve the transfer
    high_value_txn_id = response.json['transaction']['id']
    approval_response = client.post(f'/transactions/admin/approve/{high_value_txn_id}',
        headers={'Authorization': f'Bearer {admin_token}'}
    )
    assert approval_response.status_code == 200
    assert approval_response.json['transaction']['status'] == Transaction.STATUS_COMPLETED
