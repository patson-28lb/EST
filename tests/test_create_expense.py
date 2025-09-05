import pytest
from fastapi.testclient import TestClient
from app.main import app
import os

from datetime import datetime

client = TestClient(app)

# testing get and delete expenses along with return types
def test_create_delete_expense():
    """
    Tests the POST /expenses/ to create an expense.
    Tests the DELETE /expenses/ e_id to create an expense.
    It expects a 200 status code and the new expense with the status of draft.
    """
    # creating a new log in token for this test
    token = get_auth_token()
    
    header = {"Authorization":f"Bearer {token}"}

    # defining the payload for a new expense
    # new expense expects title, description and amount
    payload ={
        "title": "Test Item",
        "description": "This is a test item i created during a unit test",
        "amount": 10.45
    }

    response = client.post("/expenses/", headers=header, json=payload)
    assert response.status_code == 200
    
    data = response.json()
    
    assert isinstance(data, dict)
    
    required_fields = ["expense_id", "title", "description", "amount", "creator_id", "status", "created_at"]
    
    for field in required_fields:
        assert field in data, f"Missing required field: '{field}'"
    
    assert isinstance(data["expense_id"], str)
    
    # deleting the expense after creation 
    e_id = data["expense_id"]

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
            
    # after creating let us delete this expense
    response = client.delete(f"/expenses/delete/{e_id}", headers=header)        
    
    assert response.status_code == 200
    
    assert response.json().get('message') == f"the expense entry with the EID {e_id} has been deleted!" 
    
    
def test_submit_expense():
    """
    Tests the POST /expenses/ to create an expense.
    Tests the POST /expenses/ submit / e_id to create an expense.
    It expects a 200 status code and the new expense with the status of draft.
    """
    # creating a new log in token for this test
    token = get_auth_token()
    
    header = {"Authorization":f"Bearer {token}"}

    # defining the payload for a new expense
    # new expense expects title, description and amount
    payload ={
        "title": "Test Item",
        "description": "This is a test item i created during a unit test",
        "amount": 10.45
    }

    response = client.post("/expenses/", headers=header, json=payload)
    assert response.status_code == 200
    
    data = response.json()
    
    assert isinstance(data, dict)
    
    required_fields = ["expense_id", "title", "description", "amount", "creator_id", "status", "created_at"]
    
    for field in required_fields:
        assert field in data, f"Missing required field: '{field}'"
    
    assert isinstance(data["expense_id"], str)
    e_id = data["expense_id"]
    assert isinstance(data["status"], str)
    status = data["status"] 
    
    assert status == "draft", "draft status"

    # testimg if we can submit an expense
    response = client.post(f"/expenses/submit/{e_id}", headers=header)
    assert response.status_code == 200
    
    data = response.json()
    
    assert isinstance(data, dict)
    
    required_fields = ["expense_id", "title", "description", "amount", "creator_id", "status", "created_at"]
    
    for field in required_fields:
        assert field in data, f"Missing required field: '{field}'"
    
    assert isinstance(data["expense_id"], str)
    assert isinstance(data["status"], str)
    status = data["status"] 
    
    assert status == "submitted", "Submitted status"
    
    # after creating let us delete this expense
    response = client.delete(f"/expenses/delete/{e_id}", headers=header)        
    
    assert response.status_code == 200
    
    assert response.json().get('message') == f"the expense entry with the EID {e_id} has been deleted!" 

def test_create_expense_missing_param():
    """
    Tests the POST /expenses/ to create an expense.
    It expects a 422 status code stating unprocessable content.
    """
    
    token = get_auth_token()
    
    header = {"Authorization":f"Bearer {token}"}

    # defining the payload for a new expense
    # new expense expects title, description and amount
    payload ={
        "title": "Test Item",
        "amount": 10.45
    }
    
    response = client.post("/expenses/", headers=header, json=payload)
    data = response.json()
    assert response.status_code == 422
    assert data.get("detail")[0].get("type") == "missing"
    
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
        