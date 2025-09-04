import pytest
from fastapi.testclient import TestClient
from app.main import app
import os

# creating a test client instance, this allows for testing without making server live
client = TestClient(app)

def test_login_successful():
    """
    Tests the GET /expenses/me to return all my expenses.
    It expects a 200 status code and a List of expenses in the response body.
    """

    token = get_auth_token()
    
    header = {"Authorization":f"Bearer {token}"}
    

    response = client.get("/expenses/me", headers=header)
    assert response.status_code == 200


    
    
    
    
def get_auth_token():
    if os.path.exists('bearer_test_token.txt'):
        with open('bearer_token.txt', 'r') as file:
            token = file.readline()
            return token
    else:
        payload = {
        "username": "patson", 
        "password": "password"
    }
    response = client.post("/login", json=payload)
    
    response_data = response.json()
    token = response_data.get("access_token")
    try:
        with open("bearer_test_token.txt", "w") as f:
            f.write(token)
    except Exception as e:
        print(f"Failed to save token to file: {e}")
        
    return token
        