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

    # Make deposit
    response = client.post('/transactions/deposit', 
        json={
            'account_id': 1,
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

    # Make withdrawal
    response = client.post('/transactions/withdraw',
        json={
            'account_id': 1,
            'amount': 20000.0,
            'description': 'Test withdrawal'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 201
    assert response.json['transaction']['amount'] == 20000.0
    assert response.json['transaction']['type'] == 'withdrawal'

def test_transfer(client, init_database):
    # Login first
    login_response = client.post('/users/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    assert login_response.status_code == 200
    token = login_response.json['token']

    # Create second account for transfer
    response = client.post('/accounts',
        json={
            'account_type': 'savings',
            'initial_deposit': 100000.0
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 201
    recipient_account_id = response.json['account']['id']

    # Make transfer
    response = client.post('/transactions/transfer',
        json={
            'source_account_id': 1,
            'recipient_account_id': recipient_account_id,
            'amount': 30000.0,
            'description': 'Test transfer'
        },
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 201
    assert response.json['transaction']['amount'] == 30000.0
    assert response.json['transaction']['type'] == 'transfer'
