from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .model import Base, User, Expense, StatusEnum
from datetime import datetime, timedelta, timezone


# setting up DB connection string, this defines the path of SQL server that we have access to
# the URL specicifies the use of sqlite db
DB_URL = "sqlite:///./mydatabase.db"

# creating an SQL alchemy engine
# the engine is what actually allows to communicate b/w python and SQL db
engine = create_engine(DB_URL, echo=False)

# creating a session generator
# this method would allow us to start sessions, the benefit of starting sessions is that if an error occures mid execution, we can always rollback.
SessionLocal = sessionmaker(autoflush=False, autocommit = False, bind=engine)
# when autocomit is set to False, it prevents the action to acually change a db, only session.commit() will retain the changes done during execution
# autoflush prevents the pending changes that need to be commited into the logs


# initializing the db, this allows us to work with predefined tables using the sql connection
def init_db():
    """
    This program allows to initialize a db, it is used when a program starts
    """
    # the below line checks if tables exists that follow schema specified in model.py
    # else this creates blank tables that follow the schema defined in model.py, if it is not already exists
    Base.metadata.create_all(bind=engine)
    
def get_db():
    """
    This method allows to start and create a Session, which will be closed once the calloing method has executed. 
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def add_dummy_users():
    """
    allows to add dummy users to the db
    """
    db = SessionLocal()
    try:
        # Check if the "patson" user already exists to prevent duplicates
        existing_user = db.query(User).filter_by(username="patson").first()
        if existing_user:
            print("Dummy users already exist. Skipping creation.")
            return

        print("Adding dummy users...")
        users_to_add = [
            User(user_id="UID01", username="patson", name="Patson", password="password", department_id=1, is_approver=True),
            User(user_id="UID02", username="jane_doe", name="Jane Doe", password="password", department_id=2, is_approver=False),
            User(user_id="UID03", username="john_smith", name="John Smith", password="password", department_id=1, is_approver=False),
            User(user_id="UID04", username="adam_sandler", name="Adam Sandler", password="password", department_id=2, is_approver=True)
        ]
        
        db.add_all(users_to_add)
        db.commit()
        print("Dummy users added successfully.")
    except Exception as e:
        db.rollback()
        print(f"An error occurred while adding dummy users: {e}")
    finally:
        db.close()

def add_dummy_expenses():
    """
    allows to add dummy expenses to the db
    """
    db = SessionLocal()
    try:
        # Check if the "EID01" expense already exists to prevent duplicates
        exisitng_expense = db.query(Expense).filter_by(expense_id="EID01").first()
        if exisitng_expense:
            print("Dummy expenses already exist. Skipping creation.")
            return

        expenses_to_add = [
            Expense(
                expense_id="EID01",
                title="Office Supplies",
                description="Purchase of pens, paper, and ink cartridges.",
                amount=75.50,
                creator_id="UID02",  # Jane Doe
                approver_id = "UID04",
                status=StatusEnum.submitted,
                created_at=datetime.now(timezone.utc) - timedelta(days=2)
            ),
            Expense(
                expense_id="EID02",
                title="Client Lunch",
                description="Lunch with the Acme Corp. team to discuss the new project.",
                amount=120.00,
                creator_id="UID03",  # John Smith
                approver_id="UID01",  # Patson
                status=StatusEnum.accepted,
                created_at=datetime.now(timezone.utc) - timedelta(days=5),
                approved_at=datetime.now(timezone.utc) - timedelta(days=4)
            ),
            Expense(
                expense_id="EID03",
                title="Software Subscription",
                description="Monthly subscription for project management software.",
                amount=29.99,
                creator_id="UID03",  # John Smith
                approver_id="UID01",  # Patson
                status=StatusEnum.draft,
                created_at=datetime.now(timezone.utc) - timedelta(days=1)
            ),
            Expense(
                expense_id="EID04",
                title="Travel Expenses",
                description="Flight ticket for the Q2 conference.",
                amount=450.00,
                creator_id="UID02",  # Jane Doe
                approver_id="UID04",  # Adam Sandler
                status=StatusEnum.rejected,
                created_at=datetime.now(timezone.utc) - timedelta(days=7),
                approved_at=datetime.now(timezone.utc) - timedelta(days=6),
                rejection_reason="Missing receipt from airline."
            ),
            Expense(
                expense_id="EID05",
                title="Travel Expenses",
                description="Flight ticket for the Q3 conference.",
                amount=450.00,
                creator_id="UID01", 
                approver_id="UID01",  # Adam Sandler
                status=StatusEnum.rejected,
                created_at=datetime.now(timezone.utc) - timedelta(days=7),
                rejected_at=datetime.now(timezone.utc) - timedelta(days=6),
                rejection_reason="Missing receipt from airline."
            )
        ]

        db.add_all(expenses_to_add)
        db.commit()
        print("Dummy expenses added successfully.")
        
    except Exception as e:
        db.rollback()
        print(f"An error occurred while adding dummy expenses: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Initiallizing the database...")
    init_db()
    add_dummy_users()
    add_dummy_expenses()
    print("Database set up complete")
    