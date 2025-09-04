import pytest
from fastapi.testclient import TestClient
from app.main import app
import os

from datetime import datetime
# creating a test client instance, this allows for testing without making server live
client = TestClient(app)

# testing get expenses along with return types
def test_get_expenses():
    """
    Tests the GET /expenses/me to return all my expenses.
    It expects a 200 status code and a List of expenses in the response body.
    """

    token = get_auth_token()
    
    header = {"Authorization":f"Bearer {token}"}
    

    response = client.get("/expenses/me", headers=header)
    assert response.status_code == 200
    
    data = response.json()
    
    assert isinstance(data, list)

    for item in data:
        # Check that each item is a dictionary
        assert isinstance(item, dict), f"Expected a dictionary, but found {type(item)}"
        
        required_fields = ["expense_id", "title", "description", "amount", "creator_id", "status", "created_at"]
        for field in required_fields:
            assert field in item, f"Missing required field: '{field}'"
            
        
        assert isinstance(item["expense_id"], str)
        assert isinstance(item["title"], str)
        assert isinstance(item["description"], str)
        assert isinstance(item["amount"], (int, float))
        assert isinstance(item["creator_id"], str)
        assert isinstance(item["status"], str)
    
    # Validate date-time fields
        try:
            datetime.fromisoformat(item["created_at"])
        except ValueError:
            pytest.fail(f"Invalid format for 'created_at' date: {item['created_at']}")
            
        for date_field in ["approved_at", "rejected_at"]:
            if item.get(date_field) is not None:
                try:
                    datetime.fromisoformat(item[date_field])
                except ValueError:
                    pytest.fail(f"Invalid format for '{date_field}' date: {item[date_field]}")

        # Validate optional fields
        for optional_field in ["approver_id", "rejection_reason"]:
            if optional_field in item:
                assert isinstance(item[optional_field], (str, type(None)))
    

def test_get_expenses_explicitly():
    """
    Tests the GET /expenses/me to return all my expenses.
    It expects a 200 status code and a List of expenses in the response body.
    """

    token = get_auth_token()

    header = {"Authorization":f"Bearer {token}"}
    

    response = client.get("/expenses/me/EID07", headers=header)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    
    required_fields = ["expense_id", "title", "description", "amount", "creator_id", "status", "created_at"]
    
    for field in required_fields:
        assert field in data, f"Missing required field: '{field}'"
    
    assert isinstance(data["expense_id"], str)
    assert isinstance(data["title"], str)
    assert isinstance(data["description"], str)
    assert isinstance(data["amount"], (int, float))
    assert isinstance(data["creator_id"], str)
    assert isinstance(data["status"], str)
    
    try:
        datetime.fromisoformat(data["created_at"])
    except ValueError:
        pytest.fail(f"Invalid format for 'created_at' date: {data['created_at']}")
        
    for date_field in ["approved_at", "rejected_at"]:
        if data.get(date_field) is not None:
            try:
                datetime.fromisoformat(data[date_field])
            except ValueError:
                pytest.fail(f"Invalid format for '{date_field}' date: {data[date_field]}")

    # Validate optional fields
    for optional_field in ["approver_id", "rejection_reason"]:
        if optional_field in data:
            assert isinstance(data[optional_field], (str, type(None)))
            
            
def get_auth_token():
   
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
        