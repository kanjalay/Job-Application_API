from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import bcrypt  
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
import app.models as models

# 1. Security Configuration Keys
SECRET_KEY = "SUPER_SECRET_KEY_FOR_YOUTH_EMPLOYMENT_API_DONT_SHARE"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# 2. GLOBAL SECURITY SCHEME: This tells FastAPI & Swagger UI to display the Authorize Lock Button!
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# --- PASSWORD UTILITIES (MODERN DIRECT BCRYPT) ---
def hash_password(password: str) -> str:
    """Takes a plain text password and returns a secure, unreadable string hash."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compares a typed password with the stored hash to see if they match."""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False

# --- JWT TOKEN UTILITIES ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a secure temporary digital passport (JWT token) for a user."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- GATEKEEPER UTILITY FOR SECURING ROUTES ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    Decodes the JWT token, extracts the user, and verifies they exist in the DB.
    Locks down any route that adds this function as a dependency.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials/Digital passport expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
        
    return user