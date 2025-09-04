# importing required data types and a way to define the columns of the table
from sqlalchemy import Column, String, Integer, String, Boolean, Float, ForeignKey, Enum, DateTime
# the declarative base allows us to define the table structure as a python class when it actually could convert to a SQL table schema
from sqlalchemy.orm import declarative_base

# allows to specify current datetime
from datetime import datetime, timezone

# allows to create enums
import enum

# defining the Base class, this allows to map python classes to SQL tables
Base = declarative_base()

# this is the enum class that specifies the values of the instances of statusenum
class StatusEnum(enum.Enum):
    draft = "draft"
    submitted = "submitted"
    accepted = "accepted"
    rejected = "rejected"

# creating User model
class User(Base):
    """
    Represents the user table, this table would contain data on all users who could use the program
    """

    # setting the table name
    __tablename__ = 'user'
    
    # defining the columns below:
    
    user_id = Column(String, primary_key=True)
    username = Column(String, unique=True)
    name = Column(String)
    password = Column(String)
    department_id = Column(Integer)
    is_approver = Column(Boolean)
    
    # the repr is a function we can define within a class so that when we call print(user) where user is an instance of User, this below item will get 
    # it is known as a representation function 
    def __repr__(self):
        """
        Provides a helpful representation of the User object for debugging.
        """
        return f"<User(user_id='{self.user_id}', username='{self.username}', name='{self.name}')>"

class Expense(Base):
    """
    This class represents the expense table, it will be used to store expenses on SQL
    """
    
    __tablename__ = "expense"
    
    expense_id = Column(String, primary_key=True)
    title = Column(String)
    description = Column(String)
    amount = Column(Float)
    
    # this is for the creator_id, nullable is set to false
    # it is a FK to table user
    # FK is a string as if it were defined using the class python would raise an error
    creator_id = Column(String, ForeignKey('user.user_id'), nullable=False)
    approver_id = Column(String, ForeignKey('user.user_id'), nullable=False)
    
    status = Column(Enum(StatusEnum), default=StatusEnum.draft, nullable=False)
    
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    approved_at = Column(DateTime, nullable=True)
    rejected_at = Column(DateTime, nullable=True)

    rejection_reason = Column(String, nullable=True)
    
    def __repr__(self):
        """
        Provides a string representation for debugging and logging.
        """
        return f"<Expense(expense_id='{self.expense_id}', title='{self.title}', amount='{self.amount}', status='{self.status}')>"
