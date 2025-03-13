# RevoBank API Documentation

## Activity Diagrams

The `diagrams` folder contains PlantUML activity diagrams that illustrate the main flows of our banking operations:

1. `deposit_activity.puml`: Shows the deposit flow
   - JWT authentication
   - Account ownership and status validation
   - Atomic balance updates with rollback safety
   - Unique reference number generation (TRX{YYYYMMDD}{8_random_chars})
   - Transaction status tracking (completed, pending, failed)

2. `withdrawal_activity.puml`: Shows the withdrawal flow
   - JWT authentication
   - Account ownership and status validation
   - Minimum balance enforcement per account type:
     - Checking: 500,000 IDR (prefix: 39)
     - Savings: 100,000 IDR (prefix: 38)
     - Business: 1,000,000 IDR (prefix: 37)
     - Student: 10,000 IDR (prefix: 36)
   - Overdraft prevention with detailed error messages

3. `transfer_activity.puml`: Shows the transfer flow
   - JWT authentication
   - Source and recipient account validation
   - Balance checks with minimum balance enforcement
   - Atomic transaction updates with bidirectional tracking
   - Transaction history for both accounts
   - Rich filtering options (by type, date, status)

### Viewing the Diagrams

To view these diagrams, you need a PlantUML viewer. You can:

1. Use VS Code with the PlantUML extension
2. Use the online PlantUML server: http://www.plantuml.com/plantuml/uml/
3. Use the PlantUML CLI tool

### Key Features Illustrated

1. Authentication & Authorization
   - JWT token validation
   - Account ownership verification

2. Account Management
   - Account status validation
   - Minimum balance enforcement
   - Balance updates

3. Transaction Safety
   - Atomic operations with database transaction rollbacks
   - Unique reference numbers (TRX{YYYYMMDD}{8_random_chars})
   - Bidirectional transaction relationships:
     - Account → Source transactions (outgoing)
     - Account → Received transactions (incoming)
     - Transaction → Source account
     - Transaction → Recipient account (for transfers)

4. Error Handling
   - Invalid authentication
   - Insufficient funds
   - Account not found
   - Inactive accounts
