# RevoBank API

A secure and robust banking API built with Flask and SQLAlchemy, featuring comprehensive transaction management, account relationships, and JWT authentication.

## Features

### Account Management
- Support for multiple account types (Checking, Savings)
- Minimum balance requirements:
  - Checking accounts: 500,000
  - Savings accounts: 100,000
- Account status tracking
- Detailed account history

### Transaction System
1. **Deposits**
   - Endpoint: `POST /transactions/deposit`
   - Account validation
   - Atomic balance updates
   - Transaction receipt generation

2. **Withdrawals**
   - Endpoint: `POST /transactions/withdraw`
   - Minimum balance enforcement
   - Overdraft prevention
   - Account status validation

3. **Transfers**
   - Endpoint: `POST /transactions/transfer`
   - Inter-account transfers
   - Source and recipient validation
   - Atomic balance updates for both accounts

### Security Features
- JWT-based authentication
- Account ownership validation
- Transaction rollbacks for failed operations
- Secure password handling

### Data Management
- Bidirectional account-transaction relationships
- Rich transaction history with filtering
- Unique reference numbers (TRX + timestamp + random)
- Comprehensive error handling

## Technical Stack

- **Framework**: Flask 3.0.2
- **Database**: SQLAlchemy 2.0.28
- **Authentication**: Flask-JWT-Extended 4.6.0
- **Testing**: pytest 7.4.4
- **Documentation**: PlantUML activity diagrams

## Getting Started

### Prerequisites
- Python 3.11
- Virtual environment tool (uv recommended)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/atfdeenk/revobank-api.git
   cd revobank-api
   ```

2. Create and activate virtual environment:
   ```bash
   uv venv -p 3.11
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

### Configuration

Set up your environment variables in `.env`:
```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret
```

### Running Tests

Run the test suite:
```bash
python -m pytest tests/ -v
```

## API Documentation

### Authentication
```http
POST /auth/register
POST /auth/login
```

### Account Operations
```http
POST /accounts/create
GET /accounts/list
GET /accounts/<id>
```

### Transaction Operations
```http
POST /transactions/deposit
POST /transactions/withdraw
POST /transactions/transfer
GET /transactions/history
```

For detailed flow diagrams, see the [docs/diagrams](docs/diagrams) directory.

## Database Schema

### Account Model
- Relationships:
  - `transactions`: Outgoing transactions
  - `received_transactions`: Incoming transactions
- Key fields:
  - `account_number`
  - `type` (checking/savings)
  - `balance`
  - `minimum_balance`

### Transaction Model
- Relationships:
  - `source_account`: Source account
  - `recipient_account`: Recipient account (for transfers)
- Key fields:
  - `reference_number`
  - `amount`
  - `type`
  - `status`

## Contributing

1. Fork the repository
2. Create your feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask and SQLAlchemy communities
- RevoU FSSE October 2024 program