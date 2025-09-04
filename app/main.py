from fastapi import FastAPI, HTTPException, Depends, Security
# allows to define security based on JWT token
from fastapi.security import HTTPBearer

# models for inputs from postFunctions
from .baseModels import UserLogin, ExpenseOut, ExpenseCreate, ExpenseRejection

# allowing to get db session using get db
from .database import get_db
from sqlalchemy.orm import Session

# getting the table of User
from .model import User, Expense, StatusEnum

# created utils for security using jwt
from .jwt_utils import create_jwt_token, get_current_user

# for a list of items
from typing import List
from datetime import datetime, timezone

 

security_scheme = {
    "Bearer": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Enter your JWT token in the format 'Bearer <token>'"
    }
}


app = FastAPI(title="Expense Submission Tool", security= security_scheme)

@app.get('/')
def root():
    return {"message": "welcome to expense submission tool"}

@app.post('/login/')
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    This is the login feature expects username and password.
    on success this method returns a JWT valid for 30 mins
    """
    
    # query the db to check if specified user exists
    db_user = db.query(User).filter(
        User.username == user.username,
        User.password == user.password
    ).first()
    
    # edit isUser function for db implementation
    if db_user:
        data = {
            "sub": user.username
        }
        token = create_jwt_token(data)
        
        # curent_user = get_current_user(token)
        
        return {"access_token": token, "token_type": "bearer"} 
    
    else:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )         

@app.post(
    "/logout/",
    dependencies=[Security(HTTPBearer())],
)
def logout(token_bearer: str = Depends(HTTPBearer())):
    return token_bearer

def get_valid_user(db: Session, username: str):
    db_user = db.query(User).filter(User.username == username).first()
    
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return db_user
def get_valid_expense(db: Session, expense_id: str):
    db_expense = db.query(Expense).filter(Expense.expense_id == expense_id).first()
    
    if not db_expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )
    return db_expense

def get_valid_user_expense(db: Session, expense_id: str, user_db: User):
    db_expense = db.query(Expense).filter(Expense.expense_id == expense_id,
                                          Expense.creator_id == user_db.user_id).first()
    
    if not db_expense:
        raise HTTPException(
            status_code=404,
            detail="Expense does not exist or youre not the creator"
        )
    return db_expense

def get_valid_approver_expense(db: Session, expense_id: str, user_db: User):
    db_expense = db.query(Expense).filter(Expense.expense_id == expense_id,
                                          Expense.approver_id == user_db.user_id).first()
    
    if not db_expense:
        raise HTTPException(
            status_code=404,
            detail="Expense does not exist or youre not an approver"
        )
    return db_expense

# @app.get("/expenses/me", response_model=List[ExpenseOut])
@app.get("/expenses/me", response_model=List[ExpenseOut], dependencies=[Security(HTTPBearer())])
def read_my_expenses(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    this is a function that allows a user to view all expenses created by them. It expects a security bearer token to validate whom the user is
    """
    db_user = get_valid_user(db, current_user)
        
    expenses = db.query(Expense).filter(Expense.creator_id == db_user.user_id).all()
    
    return expenses

@app.get("/expenses/me/{expense_id}", response_model=ExpenseOut, dependencies=[Security(HTTPBearer())])
def get_my_expense_by_id(expense_id: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    this is a function that allows a user to view all expenses created by them. It expects a security bearer token to validate whom the user is and then this is followed by a lookup of the specific expense_id stated in the get request
    """
    db_user = get_valid_user(db, current_user)
        
    expense = db.query(Expense).filter(Expense.creator_id == db_user.user_id, Expense.expense_id == expense_id).first()
    
    if not expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found or you are not the creator"
        )
    return expense

@app.post('/expenses', 
          response_model=ExpenseOut, 
          dependencies=[Security(HTTPBearer())]
          )
def create_my_expense(expense: ExpenseCreate, 
                   current_user: str = Depends(get_current_user), 
                   db: Session = Depends(get_db)):
    """
    this is a method that allows to create a new expense, it expects the user to have title, description and amount in the post message
    """
    db_user = get_valid_user(db, current_user)
    
    # New expense entry for the DB
    
    expense_id = f"EID{db.query(Expense).count() +1 :02d}"
    # print(f"expense id: {expense_id}")
    
    # getting the approver who belongs to the same department as the user
    approver = db.query(User).filter(User.department_id == db_user.department_id, User.is_approver==True).first()
    
    # print(f"approver id{approver.user_id}")
    
    new_expense = Expense(
        title = expense.title,
        description = expense.description,
        amount = expense.amount,
        creator_id = db_user.user_id,
        created_at = datetime.now(timezone.utc),
        expense_id = expense_id,
        approver_id = approver.user_id
    )
    
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    
    return new_expense

@app.post('/expenses/submit/{expense_id}',
          response_model=ExpenseOut, 
          dependencies=[Security(HTTPBearer())])
def submit_my_expense(expense_id: str, 
                      current_user: str = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    """
    Method that allows me to submit an expense that is currently in a draft
    """
    db_user = get_valid_user(db, current_user)
    # check if the expense exists:
    db_expense = get_valid_user_expense(db, expense_id, db_user)
    
    if db_expense.status != StatusEnum.draft:
        raise HTTPException(
            status_code=404,
            detail="Only draft expenses can be submitted!"
        )
    
    db_expense.status = StatusEnum.submitted
    
    # commiting the change on the db
    db.commit()
    db.refresh(db_expense)
    
    return db_expense
    

@app.delete('/expenses/delete/{expense_id}', 
          dependencies=[Security(HTTPBearer())])
def delete_my_expense(expense_id: str, 
                      current_user: str = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    """
    Method that allows user to delete an expense that is currently in a draft or submitted state
    """
    db_user = get_valid_user(db, current_user)
    # check if the expense exists:
    db_expense = get_valid_user_expense(db, expense_id, db_user)
    
    if not (db_expense.status == StatusEnum.draft or db_expense.status == StatusEnum.submitted):
        raise HTTPException(
            status_code=404,
            detail="Only draft and submitted expenses can be deleted! You cant delete an approved/rejected expense"
        )
    
    # delete method
    db.delete(db_expense)
    # commiting the change on the db
    db.commit()
    
    return {"message": f"the expense entry with the EID {db_expense.expense_id} has been deleted!"}


@app.get("/expenses/approvals/me", response_model=List[ExpenseOut], dependencies=[Security(HTTPBearer())])
def read_my_approvals(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    this is a function that allows a user to view all expenses that have to be approved by them. It expects a security bearer token to validate whom the user is
    """
    db_user = get_valid_user(db, current_user)
    if not db_user.is_approver:
        raise HTTPException(
            status_code=404,
            detail="User is not an approver!"
        )
        
    expenses = db.query(Expense).filter(Expense.approver_id == db_user.user_id).all()
    
    return expenses

@app.get("/expenses/approvals/me/{expense_id}", response_model=ExpenseOut, dependencies=[Security(HTTPBearer())])
def get_my_approvals_by_id(expense_id: str, current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    this is a function that allows a user to view all expenses that have to be approved by them. It expects a security bearer token to validate whom the user is and then this is followed by a lookup of the specific expense_id stated in the get request
    """
    db_user = get_valid_user(db, current_user)
    
    if not db_user.is_approver:
        raise HTTPException(
            status_code=404,
            detail="User is not an approver!"
        )
        
    expense = db.query(Expense).filter(Expense.approver_id == db_user.user_id, Expense.expense_id == expense_id).first()
    
    if not expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found or you are not the approver"
        )
    return expense

@app.post('/expenses/approve/{expense_id}',
          response_model=ExpenseOut, 
          dependencies=[Security(HTTPBearer())])
def approve_an_expense(expense_id: str, 
                      current_user: str = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    """
    Method that allows an approver to approve an expense that is currently in submitted state
    """
    db_user = get_valid_user(db, current_user)
    
    # check if the expense exists:
    db_expense = get_valid_approver_expense(db, expense_id, db_user)
    
    if not (db_expense.status == StatusEnum.submitted):
        raise HTTPException(
            status_code=404,
            detail="Only submitted expenses can be approved!"
        )
    
    db_expense.status = StatusEnum.accepted
    db_expense.approved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(db_expense)
    
    return db_expense
    
    
@app.post('/expenses/reject/{expense_id}',
          response_model=ExpenseOut, 
          dependencies=[Security(HTTPBearer())])
def reject_an_expense(expense_id: str,
                      rejection_reason: ExpenseRejection, 
                      current_user: str = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    """
    Method that allows an approver to reject an expense that is currently in submitted state
    """
    db_user = get_valid_user(db, current_user)
    
    # check if the expense exists:
    db_expense = get_valid_approver_expense(db, expense_id, db_user)
    
    if not (db_expense.status == StatusEnum.submitted):
        raise HTTPException(
            status_code=404,
            detail="Only submitted expenses can be rejected!"
        )
    
    # updating values
    db_expense.rejection_reason = rejection_reason.rejection_reason
    db_expense.status = StatusEnum.rejected
    db_expense.rejected_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(db_expense)
    
    return db_expense
