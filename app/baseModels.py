from pydantic import BaseModel, Field
from typing import Optional

from datetime import datetime

class UserLogin(BaseModel):
    """
    Schema for the user login request body.
    """
    username: str
    password: str
    
class ExpenseOut(BaseModel):
    """
    Schema for an expense to be returned in a response.
    """
    expense_id: str
    title: str
    description: str
    amount: float
    creator_id: str
    approver_id: Optional[str] = None
    status: str
    created_at: datetime
    approved_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
        
class ExpenseCreate(BaseModel):
    """
    Schema for what a user will input while creating an expense 
    """
    title: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    amount: float = Field(..., gt=0)


class ExpenseRejection(BaseModel):
    """
    schema for a rejection message for an expense
    """
    rejection_reason: str = Field(..., min_length=10, max_length=500)