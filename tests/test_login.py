import pytest
from fastapi.testclient import TestClient
from app.main import app

# creating a test client instance, this allows for testing without making server live
client = TestClient(app)

def test_login_successful():
    """
    Tests the POST /login endpoint with a valid username and password.
    It expects a 200 status code and a 'token' in the response body.
    """
    payload = {
        "username": "patson", 
        "password": "password"
    }

    response = client.post("/login", json=payload)
    assert response.status_code == 200

    assert "access_token" in response.json()
    
def test_login_missing_payload():
    """
    Tests the POST /login endpoint with an incomplete payload
    It expects a 422 status code Unprocessable Content
    """
    payload = {
        "username": "patson"
    }

    response = client.post("/login", json=payload)
    assert response.status_code == 422
    
def test_login_unsuccessful():
    """
    Tests the POST /login endpoint with incorrect credentials.
    It expects a 401 Unauthorized status code.
    """
    payload = {
        "username": "wronguser",
        "password": "wrongpassword"
    }
    response = client.post("/login", json=payload)
    assert response.status_code == 401
    assert "detail" in response.json()
    assert response.json()["detail"] == "Incorrect username or password"
    
    
def test_unauthorized_access():
    """
    Tests the GET /expenses/me endpoint with unauthorized access.
    It expects a 403 Not Authenticated status code.
    
    """
    
    response = client.get("/expenses/me",)
    assert response.status_code == 403
    assert "detail" in response.json()
    assert response.json()["detail"] == "Not authenticated"
    
def test_wrong_bearer_token():
    """
    Tests the GET /expenses/me endpoint with incorrect bearer token.
    It expects a 401 Unauthorized status code.
    
    """
    header = {"Authorization": "Bearer xyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJwYXRzb24iLCJleHAiOjE3NTY5ODU4Nzd9.gWE_W01uNlYlU2o08v08fuClbgBI5iPCr0iamdc8zNo"}
    
    response = client.get("/expenses/me", headers= header)
    assert response.status_code == 401
    assert "detail" in response.json()
    assert response.json()["detail"].startswith("Invalid token, please re-authenticate:")