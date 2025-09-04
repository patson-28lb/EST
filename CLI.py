import requests
import sys
import os
from typing import List
from textwrap import wrap
from tabulate import tabulate
import click

BASE_URL = "http://localhost:8000"
MAX_COL_WIDTH = 10
# input params
class UserLogin:
    def __init__(self, username:str, password:str):
        self.username = username
        self.password = password
        
class CreateExpense:
    def __init__(self, title:str, description:str, amount:float):
        self.title = title
        self.description = description
        self.amount = amount
        
class ExpenseId:
    def __init__(self, expense_id:str):
        self.expense_id = expense_id
        
class RejectExpense:
    def __init__(self, expense_id:str, rejection_reason:str):
        self.expense_id = expense_id
        self.rejection_reason = rejection_reason
    

def save_token_to_file(token):
    """
    Saves the bearer token to a local file named 'bearer_token.txt'.
    """
    try:
        with open("bearer_token.txt", "w") as f:
            f.write(token)
        print("Bearer token saved to 'bearer_token.txt'.\n")
    except Exception as e:
        print(f"Failed to save token to file: {e}")
        
def get_auth_token():
    if os.path.exists('bearer_token.txt'):
        with open('bearer_token.txt', 'r') as file:
            token = file.readline()
            return token
    else:
        print("Token file does not exist!")
        raise FileNotFoundError
    
    
def login_user(user: UserLogin):
    """
    Method to log in using username and password
    """
    url = BASE_URL + '/login/'
    
    payload = {
        "username": user.username,
        "password": user.password
    }
    try:
        print(f"Attempting to log-in as {user.username}...")
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            print("\nLogin successful!")
            
            response_data = response.json()
            token = response_data.get("access_token")
            
            if token:
                print("Received auth token from server, saving this access locally...")
                save_token_to_file(token)

        else:
            print(f"\nLogin failed with status code: {response.status_code}")
            # Print the error message or details from the server's response.
            print("Response from server:")
            print(response.json())
        
    except requests.exceptions.ConnectionError:        
        print(f"\nError: Could not connect to the server at '{url}'.")
        print("Please ensure your FastAPI server is running.")
    except Exception as e:
        # Catch any other potential errors.
        print(f"\nAn unexpected error occurred: {e}")

def get_my_expenses(eid: None|ExpenseId = None) :
    try:
        token = get_auth_token()
    except FileNotFoundError:
        sys.exit("Please reauthenticate!")
        
    if eid != None:
        url = BASE_URL + f'/expenses/me/{eid.expense_id}'
    else: 
        url = BASE_URL + '/expenses/me/'
        
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print("Attempting to get the expense(s) you created...")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            # print("\nSuccessfully got expenses!")
            
            response_data = response.json()
            
            return response_data
            # pretty_print_expense(response_data)
    
        else:
            print(f"\nFailed to get expenses with status code:{response.status_code}")
            # Print the error message or details from the server's response.
            print("Response from server:")
            print(response.json())
        
    except requests.exceptions.ConnectionError:        
        print(f"\nError: Could not connect to the server at '{url}'.")
        print("Please ensure your FastAPI server is running.")
    except Exception as e:
        # Catch any other potential errors.
        print(f"\nAn unexpected error occurred: {e}")
    
    # print(token)

def create_expense(expense: CreateExpense):
    url = BASE_URL + '/expenses/'
    
    payload = {
        "title": expense.title,
        "description": expense.description,
        "amount": expense.amount
    }
    try:
        token = get_auth_token()
    except FileNotFoundError:
        sys.exit("Please reauthenticate!")
        
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print(f"\nTrying to create the expense...")
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print("\nSuccessfully created expense!")
            
            response_data = response.json()
            # pretty_print_expense(response_data)
            return response_data

        else:
            print(f"\nFailed to create expense with status code: {response.status_code}")
            # Print the error message or details from the server's response.
            print("Response from server:")
            print(response.json())
        
    except requests.exceptions.ConnectionError:        
        print(f"\nError: Could not connect to the server at '{url}'.")
        print("Please ensure your FastAPI server is running.")
    except Exception as e:
        # Catch any other potential errors.
        print(f"\nAn unexpected error occurred: {e}")

def submit_expense(eid:ExpenseId):
    url = BASE_URL + f'/expenses/submit/{eid.expense_id}'
    
    try:
        token = get_auth_token()
    except FileNotFoundError:
        sys.exit("Please reauthenticate!")
        
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print(f"\nTrying to submit expense...")
        response = requests.post(url, headers=headers)
        
        if response.status_code == 200:
            print("\nSuccessfully submitted expense!")
            
            response_data = response.json()
            return response_data

        else:
            print(f"\nFailed to Submit expense with status code: {response.status_code}")
            # Print the error message or details from the server's response.
            print("Response from server:")
            print(response.json())
        
    except requests.exceptions.ConnectionError:        
        print(f"\nError: Could not connect to the server at '{url}'.")
        print("Please ensure your FastAPI server is running.")
    except Exception as e:
        # Catch any other potential errors.
        print(f"\nAn unexpected error occurred: {e}")
        
def delete_expense(eid: ExpenseId):
    url = BASE_URL + f'/expenses/delete/{eid.expense_id}'
    
    try:
        token = get_auth_token()
    except FileNotFoundError:
        sys.exit("Please reauthenticate!")
        
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        print(f"\nTrying to delete expense...")
        response = requests.delete(url, headers=headers)
        
        if response.status_code == 200:
            print("\nSuccessfully deleted expense!")
            
            response_data = response.json()

        else:
            print(f"\nFailed to Delete expense with status code: {response.status_code}")
            # Print the error message or details from the server's response.
            print("Response from server:")
            print(response.json())
        
    except requests.exceptions.ConnectionError:        
        print(f"\nError: Could not connect to the server at '{url}'.")
        print("Please ensure your FastAPI server is running.")
    except Exception as e:
        # Catch any other potential errors.
        print(f"\nAn unexpected error occurred: {e}")

def get_my_approvals(eid: None | ExpenseId=None):
    try:
        token = get_auth_token()
    except FileNotFoundError:
        sys.exit("Please reauthenticate!")
        
    if eid != None:
        url = BASE_URL + f'/expenses/approvals/me/{eid.expense_id}'
    else: 
        url = BASE_URL + '/expenses/approvals/me/'
        
    headers = {"Authorization": f"Bearer {token}"}
    
    try:

        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print("\nSuccessfully got your Approvals!")
            
            response_data = response.json()
            
            return response_data
    
        else:
            print(f"\nFailed to get Approvals with status code:{response.status_code}")
            # Print the error message or details from the server's response.
            print("Response from server:")
            print(response.json())
        
    except requests.exceptions.ConnectionError:        
        print(f"\nError: Could not connect to the server at '{url}'.")
        print("Please ensure your FastAPI server is running.")
    except Exception as e:
        # Catch any other potential errors.
        print(f"\nAn unexpected error occurred: {e}")

def approve_an_expense(eid:ExpenseId):
    try:
        token = get_auth_token()
    except FileNotFoundError:
        sys.exit("Please reauthenticate!")
        
   
    url = BASE_URL + f'/expenses/approve/{eid.expense_id}/'
        
    headers = {"Authorization": f"Bearer {token}"}
    
    try:

        response = requests.post(url, headers=headers)
        
        if response.status_code == 200:
            print("\nsuccessfully marked expense as approved!")
            
            response_data = response.json()
            
            return response_data
    
        else:
            print(f"\nFailed to approve expense with status code:{response.status_code}")
            # Print the error message or details from the server's response.
            print("Response from server:")
            print(response.json())
        
    except requests.exceptions.ConnectionError:        
        print(f"\nError: Could not connect to the server at '{url}'.")
        print("Please ensure your FastAPI server is running.")
    except Exception as e:
        # Catch any other potential errors.
        print(f"\nAn unexpected error occurred: {e}")
        
def reject_an_expense(reject: RejectExpense):
    try:
        token = get_auth_token()
    except FileNotFoundError:
        sys.exit("Please reauthenticate!")
        
    url = BASE_URL + f'/expenses/reject/{reject.expense_id}/'
        
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "rejection_reason": reject.rejection_reason
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            print("\nsuccessfully marked expense as rejected!")
            
            response_data = response.json()
            
            return response_data
    
        else:
            print(f"\nFailed to reject expense with status code:{response.status_code}")
            # Print the error message or details from the server's response.
            print("Response from server:")
            print(response.json())
        
    except requests.exceptions.ConnectionError:        
        print(f"\nError: Could not connect to the server at '{url}'.")
        print("Please ensure your FastAPI server is running.")
    except Exception as e:
        # Catch any other potential errors.
        print(f"\nAn unexpected error occurred: {e}")
        
def wrap_all_strings(data, width):
    """
    Recursively wraps all string values in a dictionary or list of dictionaries.
    """
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, str):
                data[key] = '\n'.join(wrap(value, width))
            elif isinstance(value, (dict, list)):
                wrap_all_strings(value, width)
    elif isinstance(data, list):
        for item in data:
            wrap_all_strings(item, width)
    return data

def pretty_print_expense(data: dict | List[dict]):
    try:
        if not (type(data) == list):
            data = [data]

        headers = "keys"
        tablefmt = "fancy_grid"
        

        wrap_all_strings(data, MAX_COL_WIDTH)
        
        print(tabulate(data, headers=headers, tablefmt=tablefmt))
    except TypeError:
        sys.exit("Erorr in printing expenses! There might have not been any expense data to print!")
    
    except Exception as e:
        sys.exit(f"Ran into some issue while printing expenses with exit as {e}")


@click.group()
def cli():
    """A CLI for managing and tracking expenses."""
    pass

@cli.command()
@click.option('--username', '-u', required=True, help='Your username.')
@click.option('--password', '-p', required=True, help='Your password.')
def login(username, password):
    """Allows you to log in to the EMS"""
    user = UserLogin(username, password)
    login_user(user)
    
# command to get my expenses
@cli.command()
@click.option('--expense_id', '-e', type=str, help='Optional: View a specific expense by ID.')
def myexpenses(expense_id):
    """List your created expenses."""
    if expense_id:
        expense_id = ExpenseId(expense_id)
        pretty_print_expense(get_my_expenses(expense_id))
    else: pretty_print_expense(get_my_expenses())

@cli.command()
@click.option('--title', '-t', type=str, required = True, help='title of the expense you need to create.' )
@click.option('--description', '-d', type=str, required = True, help='description of the expense you need to create.' )  
@click.option('--amount', '-a', type=float, required = True, help='amount of the expense you need to create.' ) 
def createxpense(title, description, amount):
    """Allows you to create an expense"""
    if len(title)<3 or len(title)>100:
        sys.exit("Issue with the characters in title! 3<len(title)<100 ")
    if len(description)<10 or len(title)>500:
        sys.exit("Issue with the characters in description! 3<len(description)<100 ")
    if not amount>0:
        sys.exit("Expense needs to be > 0!")
    
    new_expense = CreateExpense(title, description, amount )
    pretty_print_expense(create_expense(new_expense))

# Submit expense command
@cli.command()
@click.option('--expense_id', '-e', required=True, type=str, help='The ID of the expense to submit.')
def submitexpense(expense_id):
    """Submits an expense for approval."""
    expense_id = ExpenseId(expense_id)
    pretty_print_expense(submit_expense(expense_id))

@cli.command()
@click.option('--expense_id', '-e', required=True, type=str, help='The ID of the expense to delete.')
def deletexpense(expense_id):
    """Deletes an expense."""
    expense_id = ExpenseId(expense_id)
    delete_expense(expense_id)

@cli.command()
@click.option('--expense_id', '-e', type=str, help='Optional: View a specific approval request by ID.')
def myapprovals(expense_id):
    """Lists expenses awaiting your approval."""
    if expense_id:
        expense_id = ExpenseId(expense_id)
        pretty_print_expense(get_my_approvals(expense_id))
    else: pretty_print_expense(get_my_approvals())
    
# Approve expense command
@cli.command()
@click.option('--expense_id', '-e', required=True, type=str, help='The ID of the expense to approve.')
def approvexpense(expense_id):
    """Approves an expense."""
    expense_id = ExpenseId(expense_id)
    pretty_print_expense(approve_an_expense(expense_id))
    
@cli.command()
@click.option('--expense_id', '-e', required=True, type=str, help='The ID of the expense to reject.')
@click.option('--reason', '-r', required=True, help='The reason for rejecting the expense.')
def rejectexpense(expense_id, reason):
    """Rejects an expense."""
    rejection = RejectExpense(expense_id, reason)
    pretty_print_expense(reject_an_expense(rejection))

if __name__ == "__main__":
    cli()
    