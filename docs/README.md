# RevoBank API Documentation

## Activity Diagrams

The `diagrams` folder contains PlantUML activity diagrams that illustrate the main flows of our banking operations:

1. `deposit_activity.puml`: Shows the deposit flow
   - JWT authentication
   - Account validation
   - Balance update
   - Transaction recording

2. `withdrawal_activity.puml`: Shows the withdrawal flow
   - JWT authentication
   - Account validation
   - Minimum balance checks (500k for checking, 100k for savings)
   - Transaction recording

3. `transfer_activity.puml`: Shows the transfer flow
   - JWT authentication
   - Source and recipient account validation
   - Balance checks
   - Atomic transaction updates

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
   - Atomic operations
   - Unique reference numbers
   - Transaction records for both parties in transfers

4. Error Handling
   - Invalid authentication
   - Insufficient funds
   - Account not found
   - Inactive accounts
