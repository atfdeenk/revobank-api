# RevoBank API Test Documentation

## Base URL
```
http://localhost:8000
```

## Rate Limits

| Endpoint | Rate Limit |
|----------|-------------|
| User Registration | 20 per minute |
| Login | 30 per minute, 300 per hour |
| Get Profile | 60 per minute |
| Update Profile | 40 per minute |
| Account Operations | 30 per minute |
| Transactions | 20 per minute |

## Load Testing

Load testing is performed using Locust. To run the tests:

```bash
locust -f tests/locust/locustfile.py --host=http://127.0.0.1:8000
```

The load tests cover:
- User registration and login
- Account creation and management
- Profile operations
- Balance checks
- Transaction operations
- Token refresh

Recommended test parameters:
- Number of users: 20-30
- Spawn rate: 1-2 users/second
- Run time: 5-10 minutes

## 1. User Management Tests

### 1.1 Create User
```http
POST /users
Content-Type: application/json

{
    "username": "testuser",
    "password": "password123",
    "name": "Test User",
    "email": "test@example.com"
}
```

**Test Cases:**
- ✅ Success (201 Created)
- ❌ Missing fields (400 Bad Request)
- ❌ Duplicate username (400 Bad Request)
- ❌ Duplicate email (400 Bad Request)
- ❌ Invalid email format (400 Bad Request)

### 1.2 User Login
```http
POST /users/login
Content-Type: application/json

{
    "username": "testuser",
    "password": "password123"
}
```

**Test Cases:**
- ✅ Success (200 OK with JWT token)
- ❌ Wrong password (401 Unauthorized)
- ❌ Non-existent user (401 Unauthorized)
- ❌ Missing fields (400 Bad Request)

### 1.3 Get Profile
```http
GET /users/me
Authorization: Bearer <token>
```

**Test Cases:**
- ✅ Success (200 OK with user details)
  ```json
  {
    "id": 1,
    "username": "testuser",
    "name": "Test User",
    "email": "test@example.com",
    "created_at": "2025-03-24T15:41:16+00:00",
    "updated_at": "2025-03-24T15:41:16+00:00"
  }
  ```
- ❌ No token (401 Unauthorized)
- ❌ Invalid token (401 Unauthorized)
- ❌ Expired token (401 Unauthorized)

### 1.4 Update Profile
```http
PUT /users/me
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "Updated Name",
    "email": "newemail@example.com"
}
```

**Test Cases:**
- ✅ Success (200 OK)
- ✅ Update password
- ❌ Update to existing email (400 Bad Request)
- ❌ Invalid email format (400 Bad Request)
- ❌ No token (401 Unauthorized)

## 2. Account Management Tests

### 2.1 Get Account Types
```http
GET /accounts/types
```

**Test Cases:**
- ✅ Success (200 OK with list of account types)
  ```json
  {
    "account_types": {
      "savings": {
        "prefix": "38",
        "minimum_balance": 100000.0,
        "description": "Basic savings account with standard interest rate"
      },
      "checking": {
        "prefix": "39",
        "minimum_balance": 500000.0,
        "description": "Everyday checking account for regular transactions"
      },
      "business": {
        "prefix": "37",
        "minimum_balance": 1000000.0,
        "description": "Business account with higher transaction limits"
      },
      "student": {
        "prefix": "36",
        "minimum_balance": 10000.0,
        "description": "Student account with no monthly fees"
      }
    }
  }
  ```

### 2.2 Create Account
```http
POST /accounts
Authorization: Bearer <token>
Content-Type: application/json

{
    "account_type": "savings",
    "initial_deposit": 100000.0
}
```

**Test Cases:**
- ✅ Success (201 Created)
  ```json
  {
    "message": "Account created successfully",
    "account": {
      "id": 1,
      "account_number": "3812345678901234",
      "account_type": "savings",
      "balance": 100000.0,
      "currency": "IDR",
      "status": "active",
      "created_at": "2025-03-24T15:41:16+00:00",
      "updated_at": "2025-03-24T15:41:16+00:00",
      "minimum_balance": 100000.0,
      "description": "Basic savings account with standard interest rate"
    }
  }
  ```
- ❌ Invalid account type (400 Bad Request)
- ❌ Initial deposit below minimum (400 Bad Request)
- ❌ No token (401 Unauthorized)

### 2.3 Get All Accounts
```http
GET /accounts
Authorization: Bearer <token>
Query Parameters:
    ?type=savings
    &status=active
```

**Test Cases:**
- ✅ Success (200 OK with list of accounts)
- ✅ Filter by account type
- ✅ Filter by status
- ✅ No accounts (200 OK with empty list)
- ❌ Invalid account type (400 Bad Request)
- ❌ No token (401 Unauthorized)

### 2.4 Get Single Account
```http
GET /accounts/:id
Authorization: Bearer <token>
```

**Test Cases:**
- ✅ Success (200 OK with account details)
- ❌ Non-existent account (404 Not Found)
- ❌ Account belongs to another user (403 Forbidden)
- ❌ No token (401 Unauthorized)

### 2.5 Update Account Status
```http
PUT /accounts/:id
Authorization: Bearer <token>
Content-Type: application/json

{
    "status": "inactive"
}
```

**Test Cases:**
- ✅ Success (200 OK)
- ❌ Invalid status (400 Bad Request)
- ❌ Account belongs to another user (403 Forbidden)
- ❌ No token (401 Unauthorized)

### 2.6 Delete Account
```http
DELETE /accounts/:id
Authorization: Bearer <token>
```

**Test Cases:**
- ✅ Success (204 No Content)
- ❌ Account has positive balance (400 Bad Request)
- ❌ Account belongs to another user (403 Forbidden)
- ❌ No token (401 Unauthorized)

## 3. Transaction Management Tests

### 3.1 Deposit Money
```http
POST /transactions/deposit
Authorization: Bearer <token>
Content-Type: application/json

{
    "account_id": 1,
    "amount": 100000.0,
    "description": "Initial deposit"
}
```

**Test Cases:**
- ✅ Success (201 Created)
  ```json
  {
    "message": "Deposit successful",
    "transaction": {
      "id": "t123",
      "type": "transfer",
      "amount": 100000.0,
      "from_account": {
        "id": 1,
        "balance": 900000.0
      },
      "to_account": {
        "id": 2,
        "balance": 1100000.0
      },
      "description": "Transaction description",
      "status": "completed",
      "created_at": "2025-04-11T16:08:51+00:00"
    }
  }
  ```
- ❌ Insufficient balance (400 Bad Request)
  ```json
  {
    "error": "Insufficient funds",
    "required": 50000.0,
    "available": 10000.0
  }
  ```
- ❌ Invalid amount (400 Bad Request)
- ❌ Invalid transaction type (400 Bad Request)
- ❌ Missing required fields (400 Bad Request)
- ❌ Account not found (404 Not Found)
- ❌ Account not active (400 Bad Request)
- ❌ Account belongs to another user (403 Forbidden)

Notes:
- All transactions use ACID guarantees
- Row-level locking prevents race conditions
- Automatic rollback on failure
- Transaction history is maintained

### 3.2 Get All Transactions
    }
  }
  ```
- ❌ Insufficient balance (400 Bad Request)
- ❌ Source account not active (400 Bad Request)
- ❌ Recipient account not active (400 Bad Request)
- ❌ Source account not found (404 Not Found)
- ❌ Recipient account not found (404 Not Found)

### 3.4 Get All Transactions
```http
GET /transactions
Authorization: Bearer <token>
Query Parameters:
    ?page=1                    # Optional: Page number (default: 1)
    &limit=20                  # Optional: Items per page (default: 20, max: 100)
    &account_id=1              # Optional: Filter by account
    &type=transfer             # Optional: deposit, withdraw, transfer
    &start_date=2025-03-01     # Optional: ISO format
    &end_date=2025-03-14       # Optional: ISO format
```

**Test Cases:**
- ✅ Success (200 OK with paginated list of transactions)
  ```json
  {
    "transactions": [
      {
        "id": 1,
        "reference_number": "TRX20250314ABC12345",
        "type": "transfer",
        "amount": 100000.0,
        "timestamp": "2025-03-14T03:30:21+07:00",
        "description": "Monthly rent",
        "status": "completed",
        "account_id": 1,
        "recipient_account_id": 2
      },
      {
        "id": 2,
        "reference_number": "TRX20250314DEF67890",
        "type": "withdraw",
        "amount": 50000.0,
        "timestamp": "2025-03-14T03:34:39+07:00",
        "description": "ATM withdrawal",
        "status": "completed",
        "account_id": 1
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
- ✅ Filter by account
- ✅ Filter by transaction type
- ✅ Filter by date range
- ✅ Pagination (page and limit)
- ✅ No transactions (200 OK with empty list)
- ❌ Invalid account ID (404 Not Found)
- ❌ Invalid transaction type (400 Bad Request)
- ❌ Invalid date format (400 Bad Request)
- ❌ Invalid page number (400 Bad Request)
- ❌ Invalid limit (400 Bad Request)

### 3.5 Get Single Transaction
```http
GET /transactions/:id
Authorization: Bearer <token>
```

**Test Cases:**
- ✅ Success (200 OK with transaction details)
- ✅ View received transfer
- ❌ Transaction not found (404 Not Found)
- ❌ Transaction belongs to another user (404 Not Found)
- ❌ No token (401 Unauthorized)

## Testing Flow
1. Create a user
2. Login to get token
3. Check available account types
4. Create accounts (test each type)
   - Verify auto-generated account numbers
   - Test minimum balance requirements
5. View all accounts with filters
6. Make deposits and withdrawals
7. Try to delete account with balance
8. Update account status
9. View transaction history
10. Test all error cases

## Testing Tips
1. Save the token after login
2. Use the token in the Authorization header for protected routes
3. Test each account type with different initial deposits
4. Verify account number format (16 digits with type-specific prefix)
5. Test account status transitions
6. Verify minimum balance requirements
7. Check currency handling (default: IDR)
8. Test both valid and invalid scenarios
9. Check response status codes and messages
10. Verify data persistence

## Example Testing Sequence

1. Create User:
```http
POST /users
{
    "username": "testuser",
    "password": "password123",
    "name": "Test User",
    "email": "test@example.com"
}
```

2. Login:
```http
POST /users/login
{
    "username": "testuser",
    "password": "password123"
}
```
Save the returned token for subsequent requests.

3. Check Account Types:
```http
GET /accounts/types
```
Note the minimum balance requirements for each type.

4. Create a Savings Account:
```http
POST /accounts
Authorization: Bearer <token>
{
    "account_type": "savings",
    "initial_deposit": 100000.0
}
```
Verify the auto-generated account number starts with "38".

5. Create a Student Account:
```http
POST /accounts
Authorization: Bearer <token>
{
    "account_type": "student",
    "initial_deposit": 10000.0
}
```
Verify the auto-generated account number starts with "36".

6. List All Accounts:
```http
GET /accounts
Authorization: Bearer <token>
```

7. Filter Savings Accounts:
```http
GET /accounts?type=savings
Authorization: Bearer <token>
```

8. Try Invalid Operations:
```http
# Try creating account with insufficient deposit
POST /accounts
Authorization: Bearer <token>
{
    "account_type": "business",
    "initial_deposit": 100000.0
}

# Try deleting account with balance
DELETE /accounts/1
Authorization: Bearer <token>
```

9. Update Account Status:
```http
PUT /accounts/1
Authorization: Bearer <token>
{
    "status": "inactive"
}
```
    "email": "test@example.com"
}
```

2. Login:
```http
POST /users/login
{
    "username": "testuser",
    "password": "password123"
}
```

3. Create Account:
```http
POST /accounts
Authorization: Bearer <token>
{
    "account_number": "1234567890",
    "balance": 1000.00
}
```

4. Make Deposit:
```http
POST /transactions
Authorization: Bearer <token>
{
    "account_id": 1,
    "type": "deposit",
    "amount": 500.00
}
```

5. Check Balance:
```http
GET /accounts/1
Authorization: Bearer <token>
```

6. View Transactions:
```http
GET /transactions?account_id=1
Authorization: Bearer <token>
```

7. Update Profile:
```http
PUT /users/me
Authorization: Bearer <token>
{
    "name": "Updated Name"
}
```
