# Database Schema Documentation

## Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    User {
        int id PK
        string username UK
        string password_hash
        string name
        string email UK
        datetime created_at
        datetime updated_at
    }
    Account {
        int id PK
        string account_number UK
        string account_type
        float balance
        string currency
        string status
        float minimum_balance
        string description
        int user_id FK
        datetime created_at
        datetime updated_at
    }
    Transaction {
        int id PK
        float amount
        string type
        datetime timestamp
        int account_id FK
        int recipient_account_id FK
        string description
        string reference_number UK
        string status
    }

    User ||--o{ Account : "has"
    Account ||--o{ Transaction : "sends"
    Account ||--o{ Transaction : "receives"
