# Project Duplication Guide

This document outlines the process of duplicating and deploying the RevoBank API project to a new location while maintaining all functionality, including the transaction system and account relationships.

## Prerequisites

- Python 3.11.11
- uv package manager
- Docker (for containerization)
- rsync (for Unix-like systems)
- GitHub account
- Koyeb account (for deployment)
- Source project: `revobank-api`
- Target directory: `milestone-3-atfdeenk`

## Step-by-Step Duplication Process

### 1. Prepare Target Directory

Ensure the target directory exists and is ready:
```bash
# Check target directory contents
ls -la /path/to/milestone-3-atfdeenk
```

### 2. Copy Project Files

Use rsync to copy files while preserving attributes and excluding unnecessary files:
```bash
rsync -av \
  --exclude='.git' \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='.pytest_cache' \
  --exclude='*.pyc' \
  /path/to/revobank-api/ \
  /path/to/milestone-3-atfdeenk/
```

Files and directories copied:
- Source code (`app/`)
- Tests (`tests/`)
- Documentation (`docs/`)
- Configuration files
- GitHub Actions workflow
- API documentation

### 3. Set Up Virtual Environment

Create and activate a new virtual environment using uv:
```bash
cd /path/to/milestone-3-atfdeenk
uv venv
source .venv/bin/activate
```

### 4. Database Migration

Initialize and apply database migrations:
```bash
# Initialize migrations directory (first time only)
flask db init

# Apply existing migrations
flask db upgrade
```

To create new migrations:
```bash
# After making model changes
flask db migrate -m "Description of changes"

# Apply the new migration
flask db upgrade
```
```

### 4. Deploy to Production

1. Create a new GitHub repository

2. Initialize git and push to GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

3. Deploy to Koyeb:
   - Log in to Koyeb dashboard
   - Create new app
   - Connect your GitHub repository
   - Choose Docker deployment method
   - Configure environment variables:
     ```
     JWT_SECRET_KEY=your-secure-key
     PORT=8000
     DATABASE_URL=your-database-url (optional)
     ```
   - Deploy the application

4. Verify deployment:
   - Check the health endpoint: `https://your-app-url/health`
   - Test API endpoints using Postman or similar tool

### 5. Testing Docker Locally

Before deploying, you can test the Docker setup locally:
```bash
# Build the image
docker build -t your-app-name .

# Run the container
docker run -p 8000:8000 your-app-name
```

Verify the application is running by accessing:
- http://localhost:8000/health
```

### 4. Install Dependencies

Install project dependencies using uv:
```bash
uv pip install -r requirements.txt
```

Key dependencies:
- Flask 3.0.2
- SQLAlchemy 2.0.28
- Flask-JWT-Extended 4.6.0
- pytest 7.4.4

### 5. Verify Installation

Run the test suite to ensure everything works:
```bash
python -m pytest tests/ -v
```

Expected test results:
- Deposit functionality ✅
- Withdrawal with minimum balance ✅
- Transfer between accounts ✅

## Project Structure

The duplicated project maintains the following structure:
```
milestone-3-atfdeenk/
├── app/
│   ├── models/
│   │   ├── account.py      # Account model with relationships
│   │   ├── transaction.py  # Transaction model
│   │   └── user.py
│   └── routes/
│       ├── account.py
│       ├── transaction.py  # Transaction endpoints
│       └── user.py
├── docs/
│   ├── diagrams/          # Activity diagrams
│   └── README.md
├── tests/
│   ├── conftest.py
│   └── test_transactions.py
├── .github/workflows/     # CI/CD configuration
├── requirements.txt       # Project dependencies
└── README.md             # Project documentation
```

## Key Features Preserved

### 1. Transaction System
- Deposit endpoint with validation
- Withdrawal with minimum balance checks
- Inter-account transfers
- Unique reference numbers

### 2. Database Relationships
- Bidirectional account-transaction relationships
- Source and recipient transaction tracking
- Account balance management

### 3. Security
- JWT authentication
- Account ownership validation
- Transaction rollbacks

## Troubleshooting

1. **Virtual Environment Issues**
   ```bash
   # If venv creation fails
   rm -rf .venv
   uv venv -p 3.11
   ```

2. **Database Issues**
   ```bash
   # Reset database if needed
   rm instance/revobank.db
   # Database will be recreated when running tests
   ```

3. **Permission Issues**
   ```bash
   # Fix file permissions if needed
   chmod -R u+rw .
   ```

## Next Steps

1. Update any environment-specific configurations
2. Set up new GitHub repository if needed
3. Configure deployment settings
4. Update API documentation with new endpoints

## References

- [Original Project Documentation](../README.md)
- [Activity Diagrams](diagrams/)
- [API Test Documentation](../API_TEST_DOCUMENTATION.md)
