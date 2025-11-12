"""Authentication utilities for user login and JWT tokens."""

import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from mgx_backend.database import get_db_manager, UserModel

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password."""
    # Bcrypt has a 72 byte limit, truncate if necessary
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"✅ [Auth] Token verified successfully, user_id: {payload.get('sub')}")
        return payload
    except JWTError as e:
        print(f"❌ [Auth] JWT Error: {type(e).__name__}: {str(e)}")
        return None
    except Exception as e:
        print(f"❌ [Auth] Token verification error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> UserModel:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if token is None:
        raise credentials_exception
    
    payload = verify_token(token)
    if payload is None:
        print(f"❌ [Auth] Token verification failed for token: {token[:20]}...")
        raise credentials_exception
    
    user_id_str = payload.get("sub")
    if user_id_str is None:
        print(f"❌ [Auth] No user_id in token payload: {payload}")
        raise credentials_exception
    
    try:
        user_id = int(user_id_str)  # Convert string to int
    except (ValueError, TypeError):
        print(f"❌ [Auth] Invalid user_id type: {type(user_id_str)}, value: {user_id_str}")
        raise credentials_exception
    
    db = get_db_manager()
    user = db.get_user(user_id)
    if user is None:
        print(f"❌ [Auth] User not found for ID: {user_id}")
        raise credentials_exception
    
    print(f"✅ [Auth] User authenticated: {user.username} (ID: {user.id})")
    return user


async def authenticate_user(username: str, password: str) -> Optional[UserModel]:
    """Authenticate a user by username and password."""
    db = get_db_manager()
    user = db.get_user_by_username(username)
    if not user:
        return None
    # Check if user has password_hash (for existing users without password)
    if not hasattr(user, 'password_hash') or not user.password_hash:
        return None
    # Truncate password if too long (bcrypt limit is 72 bytes)
    password_to_verify = password[:72] if len(password.encode('utf-8')) > 72 else password
    if not verify_password(password_to_verify, user.password_hash):
        return None
    return user

