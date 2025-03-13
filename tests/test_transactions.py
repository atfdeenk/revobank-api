import pytest
from app.models.account import Account
from app.models.transaction import Transaction

def test_deposit(client, init_database):
    # Login first
    login_response = client.post('/users/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    assert login_response.status_code == 200
    token = login_response.json['token']

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
    # Login first
    login_response = client.post('/users/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    assert login_response.status_code == 200
    token = login_response.json['token']

    # Get checking account for withdrawal
    accounts_response = client.get('/accounts', headers={'Authorization': f'Bearer {token}'})
    assert accounts_response.status_code == 200
    checking_account = next(acc for acc in accounts_response.json['accounts'] 
                          if acc['account_number'].startswith('39'))

    # Make withdrawal
    response = client.post('/transactions/withdraw',
        json={
            'account_id': checking_account['id'],
            'amount': 20000.0,
            'description': 'Test withdrawal'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 201
    assert response.json['transaction']['amount'] == 20000.0
    assert response.json['transaction']['type'] == 'withdraw'

def test_transfer(client, init_database):
    # Login first
    login_response = client.post('/users/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    assert login_response.status_code == 200
    token = login_response.json['token']

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
            'source_account_id': savings_account['id'],
            'recipient_account_id': checking_account['id'],
            'amount': 30000.0,
            'description': 'Test transfer'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 201
    assert response.json['transaction']['amount'] == 30000.0
    assert response.json['transaction']['type'] == 'transfer'
