# RevoBank API

A secure banking API with Role-Based Access Control (RBAC) and high-value transaction approval workflow.

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

### Authentication & Authorization
- JWT-based authentication with access and refresh tokens
- Role-Based Access Control (RBAC) with three roles:
  - Customer: Basic transaction operations
  - Teller: Transaction approval and customer service
  - Admin: Full system access
- Permission-based endpoint protection

### Security Features
- Rate Limiting & Throttling:
  - Authentication endpoints:
    - User creation: 5 requests per minute
    - Login: 10 requests per minute, 100 per hour
    - Token refresh: 30 requests per minute
  - Transaction endpoints:
    - Deposit/Withdraw/Transfer: 20 requests per minute
    - Transaction approval: 30 requests per minute
  - Default limits: 200 requests per day, 50 per hour
- SQL Injection Prevention:
  - Parameterized queries using SQLAlchemy ORM
  - Input validation and sanitization
  - No raw SQL strings
- Authentication Security:
  - Secure password hashing with bcrypt
  - JWT with short expiration (15 minutes)
  - HTTPS-only cookies
  - CSRF protection
- Input Validation:
  - Username: Minimum 3 characters, stripped of whitespace
  - Email: Format validation and lowercase normalization
  - Account IDs: Integer validation
  - Transaction amounts: Positive number validation
  - Dates: ISO format validation
  - Status: Enum validation

### Transaction Management
- Basic operations: deposit, withdraw, transfer
- High-value transaction workflow:
  - Transactions above 50M require admin/teller approval
  - Status tracking (completed, pending_approval, failed, cancelled)
  - Automatic balance updates after approval
- Transaction history with pagination and filtering

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
- Rich transaction history with filtering and pagination:
  - By account ID (sent and received transactions)
  - By transaction type (deposit, withdraw, transfer)
  - By date range (ISO format dates)
  - By status (completed, pending, failed)
  - Paginated results with configurable page size
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

Set up your environment variables in `.env`. A template is provided in `.env.example`:

```env
# Database configuration
DATABASE_URL=sqlite:///revobank.db  # Production database URL
DATABASE_TEST_URL=sqlite:///:memory:  # Test database URL

# JWT configuration
JWT_SECRET_KEY=your-secret-key-here  # Required: JWT signing key
JWT_ACCESS_TOKEN_EXPIRES=3600  # Token expiry in seconds

# Flask configuration
FLASK_APP=app  # Flask application module
FLASK_ENV=development  # Environment (development/production)
FLASK_DEBUG=False  # Debug mode

# Server configuration
PORT=8000  # Server port
GUNICORN_WORKERS=2  # Number of Gunicorn workers

# Rate limiting
RATELIMIT_DEFAULT=100/hour  # Default rate limit
RATELIMIT_STORAGE_URL=memory://  # Rate limit storage

# Security thresholds
MINIMUM_BALANCE=100000.0  # Minimum balance requirement
HIGH_VALUE_THRESHOLD=50000000.0  # High-value transaction threshold
MAX_FAILED_LOGIN_ATTEMPTS=5  # Max failed logins before lockout
ACCOUNT_LOCKOUT_DURATION=900  # Lockout duration in seconds
```

Copy `.env.example` to `.env` and set appropriate values for your environment.

### Running Tests

Run the test suite:

```bash
python -m pytest tests/ -v
```

## API Documentation

### Authentication

#### Create User
```http
POST /users
Content-Type: application/json

{
    "username": "string, min 3 chars",
    "password": "string, required",
    "name": "string, required",
    "email": "string, valid email format"
}

Response (201 Created):
{
    "message": "User created successfully",
    "user": {
        "id": "integer",
        "username": "string",
        "name": "string",
        "email": "string"
    }
}

Possible Errors:
- 400: Invalid username format (min 3 chars)
- 400: Invalid email format
- 400: Username already exists
- 400: Email already exists
```

#### Login
```http
POST /users/login
Content-Type: application/json

{
    "username": "string",
    "password": "string"
}

Response (200 OK):
{
    "access_token": "string",
    "refresh_token": "string",
    "token_type": "Bearer",
    "expires_in": 900,
    "user": {
        "id": "integer",
        "username": "string",
        "name": "string",
        "email": "string"
    }
}
```

### Transactions

#### Create Deposit
```http
POST /transactions/deposit
Authorization: Bearer {token}
Content-Type: application/json

{
    "account_id": "integer",
    "amount": "float",
    "description": "string (optional)"
}

Response (201 Created):
{
    "message": "Deposit successful",
    "transaction": {
        "id": "integer",
        "type": "deposit",
        "amount": "float",
        "status": "completed",
        ...
    }
}
```

#### Create Transfer
```http
POST /transactions/transfer
Authorization: Bearer {token}
Content-Type: application/json

{
    "from_account_id": "integer",
    "to_account_id": "integer",
    "amount": "float",
    "description": "string (optional)"
}

Response (201 Created or 202 Accepted):
{
    "message": "Transfer successful" | "Transfer pending approval",
    "transaction": {
        "id": "integer",
        "type": "transfer",
        "amount": "float",
        "status": "completed" | "pending_approval",
        ...
    }
}
```

#### Approve Transaction (Admin/Teller)
```http
POST /transactions/admin/approve/{transaction_id}
Authorization: Bearer {token}

Response (200 OK):
{
    "message": "Transaction approved successfully",
    "transaction": {
        "id": "integer",
        "type": "string",
        "amount": "float",
        "status": "completed",
        ...
    }
}
```

#### View All Transactions (Admin/Teller)
```http
GET /transactions/admin/all?page=1&limit=20
Authorization: Bearer {token}

Features:
- Optimized query performance with indexes
- Eager loading of related data
- Efficient pagination
- Flexible filtering

Optional Query Parameters:
- account_id: Integer, filter by account (indexed)
- type: One of [deposit, withdraw, transfer] (indexed)
- status: One of [completed, pending_approval, failed] (indexed)
- start_date: ISO format (YYYY-MM-DD) (indexed)
- end_date: ISO format (YYYY-MM-DD)
- page: Integer > 0, default 1
- limit: Integer 1-100, default 20

Possible Errors:
- 400: Invalid account ID format
- 400: Invalid transaction type
- 400: Invalid status
- 400: Invalid date format
- 400: Invalid page/limit values

Response (200 OK):
{
    "transactions": [...],
    "pagination": {
        "total_items": "integer",
        "total_pages": "integer",
        "current_page": "integer",
        "limit": "integer",
        "has_next": "boolean",
        "has_prev": "boolean"
    }
}
```

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
    "from_account_id": "integer, required",
    "to_account_id": "integer, required",
    "amount": "positive number, required",
    "description": "string, optional"
}

Features:
- ACID compliant transaction
- Row-level locking for concurrent safety
- Automatic rollback on failure
- Balance constraints enforced
- High-value approval workflow

Possible Errors:
- 400: Invalid account ID format
- 400: Amount must be positive
- 400: Insufficient funds
- 400: Account not found
- 400: Account is inactive
- 400: Balance would fall below minimum
- 202: Transaction pending approval (amount > 50M)
- 409: Concurrent transaction conflict

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
GET /transactions?account_id=1&page=1&limit=20
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
    ],
    "pagination": {
        "total_items": 45,
        "total_pages": 3,
        "current_page": 1,
        "limit": 20,
        "has_next": true,
        "has_prev": false,
        "next_page": 2,
        "prev_page": null
    }
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
