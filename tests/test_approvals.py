import pytest
from datetime import datetime

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def is_valid_expense_syntax(item):
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
            
            
def test_get_approvals():
    """
    Tests the GET /approvals/me to return all my approvals.
    It expects a 200 status code and a List of expenses in the response body.
    """

    token = get_auth_token()
    
    header = {"Authorization":f"Bearer {token}"}
    
    response = client.get("/expenses/me", headers=header)
    assert response.status_code == 200
    
    data = response.json()
    
    assert isinstance(data, list)
    
    # checking if all data conforms to the data format of an Expense
    for item in data:
        is_valid_expense_syntax(item)

def test_get_approvals_explicitly():
    """
    Tests the GET /approvals/me to return a single expenses.
    It expects a 200 status code and a an expense in the response body.
    """

    token = get_auth_token()

    header = {"Authorization":f"Bearer {token}"}
    

    response = client.get("/expenses/approvals/me/EID07", headers=header)
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    
    is_valid_expense_syntax(data)
    
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

