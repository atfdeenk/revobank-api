# RevoBank API

A secure and robust RESTful banking API that enables account management, transactions, and user operations with comprehensive security features. Built with Flask and SQLAlchemy, it provides a reliable platform for banking operations with proper transaction management and data integrity.

## Production Deployment

The API is deployed and running at:
```
https://gothic-vallie-revobank-api-6e0a31f1.koyeb.app
```

Health Check:
```
https://gothic-vallie-revobank-api-6e0a31f1.koyeb.app/health
```

## Overview

RevoBank API is designed to handle core banking operations with a focus on:

- Secure user authentication and authorization
- Multiple account types with different requirements
- Safe transaction processing with ACID properties
- Comprehensive activity tracking and history
- Rich API documentation and testing

## Features

### Account Management

- Support for multiple account types with prefixes:
  - Savings (38): 100,000 IDR minimum balance
  - Checking (39): 500,000 IDR minimum balance
  - Business (37): 1,000,000 IDR minimum balance
  - Student (36): 10,000 IDR minimum balance
- Account status tracking (active, inactive, closed)
- Detailed account history with filtering

### Transaction System

1. **Deposits**

   - Endpoint: `POST /transactions/deposit`
   - Account ownership and status validation
   - Atomic balance updates with rollback safety
   - Unique reference number generation (TRX{YYYYMMDD}{8_random_chars})
   - Transaction status tracking (completed, pending, failed)

2. **Withdrawals**

   - Endpoint: `POST /transactions/withdraw`
   - Minimum balance enforcement per account type
   - Overdraft prevention with detailed error messages
   - Account status validation (active accounts only)
   - Balance verification before transaction

3. **Transfers**
   - Endpoint: `POST /transactions/transfer`
   - Inter-account transfers with bidirectional tracking
   - Source and recipient account validation
   - Atomic balance updates with transaction safety
   - Detailed transaction history for both accounts

### Security Features

- JWT-based authentication
- Account ownership validation
- Transaction rollbacks for failed operations
- Secure password handling

### Data Management

- Timestamp tracking for all models:
  - User: `created_at`, `updated_at`
  - Account: `created_at`, `updated_at`
  - Transaction: `timestamp`

- Bidirectional account-transaction relationships:
  - Account → Source transactions (outgoing via foreign_key='Transaction.account_id')
  - Account → Received transactions (incoming via foreign_key='Transaction.recipient_account_id')
  - Transaction → Source account (for all transaction types)
  - Transaction → Recipient account (for transfers)
- Rich transaction history with filtering:
  - By account ID (sent and received transactions)
  - By transaction type (deposit, withdraw, transfer)
  - By date range (ISO format dates)
  - By status (completed, pending, failed)
- Unique reference numbers: TRX{YYYYMMDD}{8_random_chars}
- Transaction status tracking:
  - completed: Successfully processed
  - pending: In progress
  - failed: Transaction failed with rollback
- Comprehensive error handling:
  - Insufficient funds with current and minimum balance
  - Account ownership and status validation
  - Transaction validation and constraints

## Technical Stack

- **Framework**: Flask 3.0.2
- **Database**: SQLAlchemy 2.0.28
- **Authentication**: Flask-JWT-Extended 4.6.0
- **Migration**: Flask-Migrate 4.1.0
- **Testing**: pytest 7.4.4
- **Documentation**: PlantUML activity diagrams

## Getting Started

### Prerequisites

- Python 3.11.11
- Virtual environment tool (uv recommended)
- Docker (for containerization)

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/atfdeenk/revobank-api.git
   cd revobank-api
   ```

2. Create and activate virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

4. Initialize and apply database migrations:
   ```bash
   flask db upgrade
   ```

5. Run the application:
   ```bash
   python run.py
   ```

### Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t revobank-api .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 revobank-api
   ```

### Production Deployment (Koyeb)

1. Push your code to GitHub

2. In Koyeb dashboard:
   - Create new app
   - Select your GitHub repository
   - Choose Docker deployment method
   - Set environment variables:
     - `JWT_SECRET_KEY`: Your secure JWT key
     - `DATABASE_URL`: Your database URL (optional)
     - `PORT`: 8000

3. The app will be deployed and accessible at your Koyeb URL
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

#### Register User

```http
POST /users
Content-Type: application/json

{
    "username": "johndoe",
    "password": "securepass123",
    "email": "john@example.com",
    "name": "John Doe"
}

Response (201 Created):
{
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "name": "John Doe"
    }
}
```

#### Login

```http
POST /users/login
Content-Type: application/json

{
    "username": "johndoe",
    "password": "securepass123"
}

Response (200 OK):
{
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer"
}
```

### Account Operations

#### Create Account

```http
POST /accounts
Authorization: Bearer <token>
Content-Type: application/json

{
    "account_type": "savings",
    "initial_deposit": 100000.0
}

Response (201 Created):
{
    "message": "Account created successfully",
    "account": {
        "id": 1,
        "account_number": "3812345678901234",
        "type": "savings",
        "balance": 100000.0,
        "minimum_balance": 100000.0
    }
}
```

#### List Accounts

```http
GET /accounts
Authorization: Bearer <token>

Response (200 OK):
{
    "accounts": [
        {
            "id": 1,
            "account_number": "3812345678901234",
            "type": "savings",
            "balance": 100000.0,
            "minimum_balance": 100000.0
        }
    ]
}
```

### Transaction Operations

#### Deposit

```http
POST /transactions/deposit
Authorization: Bearer <token>
Content-Type: application/json

{
    "account_id": 1,
    "amount": 50000.0
}

Response (200 OK):
{
    "message": "Deposit successful",
    "transaction": {
        "id": "TRX202503140001",
        "type": "deposit",
        "amount": 50000.0,
        "balance": 150000.0
    }
}
```

#### Withdraw

```http
POST /transactions/withdraw
Authorization: Bearer <token>
Content-Type: application/json

{
    "account_id": 1,
    "amount": 25000.0
}

Response (200 OK):
{
    "message": "Withdrawal successful",
    "transaction": {
        "id": "TRX202503140002",
        "type": "withdraw",
        "amount": 25000.0,
        "balance": 125000.0
    }
}
```

#### Transfer

```http
POST /transactions/transfer
Authorization: Bearer <token>
Content-Type: application/json

{
    "from_account_id": 1,
    "to_account_id": 2,
    "amount": 30000.0,
    "description": "Transfer to account 1234567890"
}

Response (201 Created):
{
    "message": "Transfer successful",
    "transaction": {
        "id": 3,
        "reference_number": "TRX202503140003",
        "type": "transfer",
        "amount": 30000.0,
        "description": "Transfer to account 1234567890",
        "account_id": 1,
        "recipient_account_id": 2,
        "status": "completed",
        "timestamp": "2025-03-14T04:40:00Z"
    }
}
```

#### Transaction History

```http
GET /transactions?account_id=1
Authorization: Bearer <token>

Response (200 OK):
{
    "transactions": [
        {
            "id": 1,
            "reference_number": "TRX202503140001",
            "type": "deposit",
            "amount": 50000.0,
            "description": "Deposit",
            "account_id": 1,
            "recipient_account_id": null,
            "timestamp": "2025-03-14T04:30:00Z"
        },
        {
            "id": 2,
            "reference_number": "TRX202503140002",
            "type": "withdraw",
            "amount": 25000.0,
            "description": "Withdrawal",
            "account_id": 1,
            "recipient_account_id": null,
            "timestamp": "2025-03-14T04:35:00Z"
        }
    ]
}
```

For detailed flow diagrams, see the [docs/diagrams](docs/diagrams) directory.

## Database Schema

### Account Model

- Relationships:
  - `transactions`: Outgoing transactions (foreign_key='Transaction.account_id')
  - `received_transactions`: Incoming transactions (foreign_key='Transaction.recipient_account_id')
- Key fields:
  - `account_number` (16 digits with type-specific prefix)
  - `type` (savings/checking/business/student)
  - `balance` (current balance)
  - `minimum_balance` (type-specific requirement)
  - `status` (active/inactive/closed)

### Transaction Model

- Relationships:
  - `source_account`: Source account (required)
  - `recipient_account`: Recipient account (for transfers)
- Key fields:
  - `reference_number` (TRX{YYYYMMDD}{8_random_chars})
  - `amount` (transaction amount)
  - `type` (deposit/withdraw/transfer)
  - `status` (completed/pending/failed)
  - `description` (transaction details)
  - `timestamp` (UTC timestamp)

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
