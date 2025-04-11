from app import create_app, db
from app.models.role import Role
import os
import tempfile

class TestConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/revobank.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'test-secret-key'
    DEBUG = True

app = create_app()
app.config.from_object(TestConfig)

def init_db():
    with app.app_context():
        # Drop all tables
        try:
            db.drop_all()
            print("All tables dropped")
        except Exception as e:
            print(f"Error dropping tables: {e}")
        
        # Create tables
        try:
            db.create_all()
            print("Tables created")
        except Exception as e:
            print(f"Error creating tables: {e}")
            return
        
        try:
            # Create roles with their permissions
            admin_role = Role(name=Role.ADMIN, permissions=[
                'create_user', 'view_user', 'edit_user', 'delete_user',
                'create_account', 'view_account', 'edit_account', 'delete_account',
                'create_transaction', 'view_transaction', 'edit_transaction', 'delete_transaction'
            ])
            
            teller_role = Role(name=Role.TELLER, permissions=[
                'view_user', 'create_account', 'view_account',
                'create_transaction', 'view_transaction'
            ])
            
            customer_role = Role(name=Role.CUSTOMER, permissions=[
                'view_own_user', 'edit_own_user',
                'view_own_account', 'view_own_transaction',
                'create_own_transaction'
            ])
            
            # Add roles to database
            db.session.add(admin_role)
            db.session.add(teller_role)
            db.session.add(customer_role)
            
            # Commit changes
            db.session.commit()
            print("Database initialized with roles")
        except Exception as e:
            print(f"Error initializing roles: {e}")
            db.session.rollback()

if __name__ == '__main__':
    # Create /tmp if it doesn't exist
    if not os.path.exists('/tmp'):
        os.makedirs('/tmp')
    
    # Remove the old database file
    db_path = '/tmp/revobank.db'
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"Removed old database: {db_path}")
    except Exception as e:
        print(f"Error removing old database: {e}")
    
    init_db()
