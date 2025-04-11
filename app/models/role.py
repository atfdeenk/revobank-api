from app import db

class Role(db.Model):
    """Role model for RBAC"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    permissions = db.Column(db.JSON, nullable=False, default=list)  # List of permission strings

    # Define standard roles and their permissions
    CUSTOMER = 'customer'
    ADMIN = 'admin'
    TELLER = 'teller'

    # Define permissions
    PERMISSIONS = {
        'account': {
            'view_own': 'account:view_own',
            'view_all': 'account:view_all',
            'create': 'account:create',
            'update': 'account:update',
            'delete': 'account:delete'
        },
        'transaction': {
            'view_own': 'transaction:view_own',
            'view_all': 'transaction:view_all',
            'create': 'transaction:create',
            'approve': 'transaction:approve'
        },
        'user': {
            'view_own': 'user:view_own',
            'view_all': 'user:view_all',
            'create': 'user:create',
            'update': 'user:update',
            'delete': 'user:delete'
        }
    }

    # Define default permissions for each role
    DEFAULT_PERMISSIONS = {
        CUSTOMER: [
            PERMISSIONS['account']['view_own'],
            PERMISSIONS['transaction']['view_own'],
            PERMISSIONS['transaction']['create'],
            PERMISSIONS['user']['view_own'],
            PERMISSIONS['user']['update']
        ],
        ADMIN: [
            PERMISSIONS['account']['view_all'],
            PERMISSIONS['account']['create'],
            PERMISSIONS['account']['update'],
            PERMISSIONS['account']['delete'],
            PERMISSIONS['transaction']['view_all'],
            PERMISSIONS['transaction']['approve'],
            PERMISSIONS['user']['view_all'],
            PERMISSIONS['user']['create'],
            PERMISSIONS['user']['update'],
            PERMISSIONS['user']['delete']
        ],
        TELLER: [
            PERMISSIONS['account']['view_all'],
            PERMISSIONS['account']['create'],
            PERMISSIONS['transaction']['view_all'],
            PERMISSIONS['transaction']['create'],
            PERMISSIONS['transaction']['approve']
        ]
    }

    def __init__(self, name, description=None, permissions=None):
        self.name = name
        self.description = description
        self.permissions = permissions or self.DEFAULT_PERMISSIONS.get(name, [])
