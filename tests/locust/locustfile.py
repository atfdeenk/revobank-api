from locust import HttpUser, task, between
import json
import random

class BankAPIUser(HttpUser):
    # Wait between 1 to 5 seconds between tasks
    wait_time = between(1, 5)
    
    def on_start(self):
        """Setup before tests - register and login a user"""
        # Initialize headers
        self.headers = None
        self.token = None
        self.account_id = None
        
        # Register a new user with random username
        self.username = f"testuser_{random.randint(1000, 9999)}"
        self.password = "Test123!"
        self.email = f"{self.username}@example.com"
        
        # Register user
        response = self.client.post(
            "/users",
            json={
                "username": self.username,
                "password": self.password,
                "name": "Test User",
                "email": self.email
            }
        )
        
        # Login to get tokens
        if response.status_code in [201, 400]:  # 400 means user might already exist
            response = self.client.post("/users/login", json={
                "username": self.username,
                "password": self.password
            })
            if response.status_code == 200:
                data = json.loads(response.text)
                self.access_token = data["access_token"]
                self.refresh_token = data["refresh_token"]
                self.headers = {"Authorization": f"Bearer {self.access_token}"}
                self.refresh_headers = {"Authorization": f"Bearer {self.refresh_token}"}
                
                # Create account after successful login
                response = self.client.post(
                    "/accounts",
                    json={
                        "account_type": "savings",
                        "initial_deposit": 1000000
                    },
                    headers=self.headers
                )
                if response.status_code == 201:
                    data = json.loads(response.text)
                    self.account_id = data.get('id')
    
    @task(3)
    def get_profile(self):
        """Get user profile - weight: 3"""
        if self.headers:
            self.client.get("/users/me", headers=self.headers)
    
    @task(2)
    def update_profile(self):
        """Update user profile - weight: 2"""
        if self.headers:
            user_id = random.randint(1000, 9999)
            self.client.put("/users/me", 
                headers=self.headers,
                json={
                    "name": f"Updated User {user_id}",
                    "email": f"updated{user_id}@example.com"
                }
            )
    
    @task(2)
    def get_balance(self):
        """Check account balance - weight: 2"""
        if self.headers and self.account_id:
            # Get account details
            response = self.client.get(f"/accounts/{self.account_id}", headers=self.headers)
            if response.status_code == 200:
                # Get transactions
                self.client.get(f"/accounts/{self.account_id}/transactions", headers=self.headers)
    
    @task(1)
    def make_transfer(self):
        """Make a transfer - weight: 1"""
        if self.headers and self.account_id:
            # Create a recipient account if needed
            response = self.client.post(
                "/accounts",
                json={
                    "account_type": "savings",
                    "initial_deposit": 1000000
                },
                headers=self.headers
            )
            if response.status_code == 201:
                recipient_data = json.loads(response.text)
                recipient_account = recipient_data['account']['id']
                amount = random.randint(10000, 50000)
                
                # Make transfer
                transfer_response = self.client.post(
                    "/transactions", 
                    json={
                        "from_account_id": self.account_id,
                        "to_account_id": recipient_account,
                        "amount": amount,
                        "transaction_type": "transfer",
                        "description": "Load test transfer"
                    }, 
                    headers=self.headers
                )
                
                if transfer_response.status_code == 201:
                    # Get transaction details
                    transaction_data = json.loads(transfer_response.text)
                    transaction_id = transaction_data['transaction']['id']
                    self.client.get(f"/transactions/{transaction_id}", headers=self.headers)
    
    @task(1)
    def refresh_token(self):
        """Refresh access token - weight: 1"""
        if self.refresh_headers:
            response = self.client.post("/users/refresh", headers=self.refresh_headers)
            if response.status_code == 200:
                data = json.loads(response.text)
                self.access_token = data["access_token"]
                self.headers = {"Authorization": f"Bearer {self.access_token}"}
