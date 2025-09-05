# this import is for the time, we could specify expiry of the token
from datetime import datetime, timedelta, timezone

# jose is JSON, object signing and encryption 
from jose import jwt, JWTError

from fastapi.security import HTTPBearer

from fastapi import Depends, HTTPException

import uuid
import redis

from dotenv import load_dotenv
import os


redis_client = redis.Redis(host='redis', port=6379, db=0)

load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")

ALGORITHM = "HS256"
TOKEN_EXPIRY_TIME_MINUTES = 30

bearer_scheme = HTTPBearer()

def create_jwt_token(data: dict):
    """
    this program expects data stored as a dict and will encode it using JOSE to produce a JWT token valid for 60 mins
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRY_TIME_MINUTES)
    to_encode.update({"exp":expire})
    
    # adding an identifier for the token
    jti = str(uuid.uuid4())
    to_encode.update({"jti": jti})
    
    jwt_token = jwt.encode(to_encode, SECRET_KEY ,algorithm=ALGORITHM)
    
    return jwt_token

# def get_current_user(token: str):
#     """
#     this is a method that takes in a jwt token and verifies if it is a valid token, if the token is valid it will return the username of the user
#     """
    
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get('sub')
#         if username is None:
#             raise JWTError("Invalid token payload")
#         return username
#     except JWTError:
#         # when the token is invalid like it could be fake or expired, this is the executions
#         raise JWTError("Invalid token, please re-authenticate!")



def get_current_user(token_bearer: str = Depends(bearer_scheme)):
    """
    A dependency that validates a JWT token and returns the username.
    It expects the token to be in the "Authorization: Bearer <token>" header.
    """
    try:
        # The .credentials attribute of bearer_scheme contains the token string.
        payload = jwt.decode(token_bearer.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        
        jti = payload.get('jti')
        if jti is None or redis_client.exists(jti):
            raise HTTPException(
                status_code=401,
                detail="Invalid token or token blacklisted"
            )
        
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token payload"
            )
        return username
    
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token, please re-authenticate: {e}"
        )

def logout_current_user(token_bearer: str = Depends(bearer_scheme)):
    """
    A dependency that logs out a JWT token and returns the username.
    It expects the token to be in the "Authorization: Bearer <token>" header.
    """
    try:
        # The .credentials attribute of bearer_scheme contains the token string.
        payload = jwt.decode(token_bearer.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        
        jti = payload.get('jti')
        if jti is None or redis_client.exists(jti):
            raise HTTPException(
                status_code=401,
                detail="Invalid token or user is already logged out!"
            )
        
        # Get the expiration time from the payload
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: Missing expiration claim"
            )
        
        username: str | None = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token payload"
            )
        # when active user wishes to logout, we add the "jti" to redis along with TTL specified in payload as exp
        exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
        time_to_expire = exp_datetime - datetime.now(timezone.utc)

        # Ensure a positive time to expire to avoid issues
        if time_to_expire.total_seconds() > 0:
            # Blacklist the JTI with the remaining expiration time
            redis_client.setex(jti, int(time_to_expire.total_seconds()), "blacklisted")
        
        return username
    # when the JWT is invalid, there is no need to logout.
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token, your authorization is invalid, please re-authenticate: {e}"
        )