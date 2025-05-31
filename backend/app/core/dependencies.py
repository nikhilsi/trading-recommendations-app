# backend/app/core/dependencies.py
"""
Authentication dependencies for FastAPI
"""
from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime

from models.database import get_db
from models.auth import User, UserSession
from core.security import decode_token, AuthError

# Security scheme
security = HTTPBearer(auto_error=False)

async def get_current_user_optional(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if token provided, otherwise None
    Used for endpoints that work with or without auth
    """
    if not credentials:
        return None
    
    try:
        # Decode the access token
        payload = decode_token(credentials.credentials, expected_type="access")
        user_id: str = payload.get("sub")
        
        if not user_id:
            return None
        
        # Get user from database
        user = db.query(User).filter(
            User.id == user_id,
            User.is_active == True
        ).first()
        
        return user
        
    except AuthError:
        return None
    except Exception:
        return None

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Session = Depends(get_db)
) -> User:
    """
    Get current user from JWT token (required)
    Raises 401 if not authenticated
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Decode the access token
        payload = decode_token(credentials.credentials, expected_type="access")
        user_id: str = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = db.query(User).filter(
            User.id == user_id,
            User.is_active == True
        ).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e.detail),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Ensure user is active"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user

async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Ensure user is admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

async def get_current_verified_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """Ensure user email is verified"""
    if not current_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    return current_user

# Dependency for rate limiting (future use)
async def check_rate_limit(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
) -> None:
    """
    Check rate limits for current user
    For now, just a placeholder - implement when needed
    """
    # TODO: Implement rate limiting logic
    # Check user tier and endpoint limits
    # Use Redis for efficient rate limiting
    pass

# Helper to get user tier features
def get_user_features(user: User) -> dict:
    """Get features available for user's tier"""
    # Default free tier features
    default_features = {
        "scans_per_day": 50,
        "screener_filters": 3,
        "watchlist_size": 20,
        "saved_presets": 5,
        "api_calls_per_hour": 60,
        "export_csv": True,
        "real_time_updates": False,
        "advanced_indicators": False,
        "pattern_recognition": False,
        "backtesting": False
    }
    
    if user.tier and user.tier.is_active:
        # Merge with custom tier features
        return {**default_features, **user.tier.features}
    
    return default_features