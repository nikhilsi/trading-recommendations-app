# backend/app/core/security.py
"""
Core security utilities for JWT tokens and password hashing
"""
from datetime import datetime, timedelta
from typing import Optional, Union, Any
import secrets
import re
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status

# Security configuration
SECRET_KEY = "your-secret-key-change-this-in-production"  # TODO: Move to env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
INVITE_CODE_LENGTH = 8
INVITE_CODE_EXPIRE_DAYS = 7

# Password configuration
PASSWORD_MIN_LENGTH = 8
PASSWORD_REGEX = re.compile(
    r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]'
)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthError(HTTPException):
    """Custom auth exception"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def validate_password(password: str) -> tuple[bool, str]:
    """
    Validate password meets requirements
    Returns: (is_valid, error_message)
    """
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters long"
    
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[@$!%*#?&]', password):
        return False, "Password must contain at least one special character (@$!%*#?&)"
    
    return True, ""

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "type": "access"
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "type": "refresh"
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str, expected_type: str = "access") -> dict:
    """
    Decode and validate JWT token
    
    Args:
        token: JWT token to decode
        expected_type: Expected token type ('access' or 'refresh')
    
    Returns:
        Token payload
        
    Raises:
        AuthError: If token is invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Verify token type
        if payload.get("type") != expected_type:
            raise AuthError(f"Invalid token type. Expected {expected_type}")
        
        # Check expiration (jose handles this, but being explicit)
        exp = payload.get("exp")
        if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
            raise AuthError("Token has expired")
        
        return payload
        
    except JWTError as e:
        raise AuthError(f"Invalid token: {str(e)}")

def generate_invite_code() -> str:
    """Generate a secure random invite code"""
    # Use URL-safe characters, avoid confusion (no 0, O, l, I)
    alphabet = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ23456789"
    return ''.join(secrets.choice(alphabet) for _ in range(INVITE_CODE_LENGTH))

def generate_secure_token() -> str:
    """Generate a secure random token for refresh tokens"""
    return secrets.token_urlsafe(32)

# Email validation regex
EMAIL_REGEX = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)

def validate_email(email: str) -> bool:
    """Validate email format"""
    return bool(EMAIL_REGEX.match(email))

# Rate limiting helpers (for future use)
def get_rate_limit_key(user_id: str, endpoint: str) -> str:
    """Generate rate limit cache key"""
    return f"rate_limit:{user_id}:{endpoint}"

# Token blacklist helpers (for logout)
def get_token_blacklist_key(token_jti: str) -> str:
    """Generate token blacklist cache key"""
    return f"blacklist:{token_jti}"