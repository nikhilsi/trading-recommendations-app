# backend/app/schemas/auth.py
"""
Pydantic schemas for authentication
"""
from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

from core.security import validate_password, validate_email

# Request schemas
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    invite_code: str = Field(..., min_length=8, max_length=32)
    
    @validator('password')
    def validate_password_strength(cls, v):
        is_valid, error_msg = validate_password(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v
    
    @validator('email')
    def validate_email_format(cls, v):
        if not validate_email(v):
            raise ValueError('Invalid email format')
        return v.lower()  # Store emails in lowercase

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
    @validator('email')
    def lowercase_email(cls, v):
        return v.lower()

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class InviteCreate(BaseModel):
    email: Optional[EmailStr] = None  # Pre-assign to email (optional)
    notes: Optional[str] = None  # Admin notes
    expires_in_days: int = Field(default=7, ge=1, le=30)

# Response schemas
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds

class UserResponse(BaseModel):
    id: UUID
    email: str
    is_active: bool
    is_admin: bool
    email_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    tier: str = "free"
    
    class Config:
        orm_mode = True

class InviteResponse(BaseModel):
    id: UUID
    code: str
    email: Optional[str]
    created_at: datetime
    expires_at: datetime
    is_used: bool
    is_expired: bool
    notes: Optional[str]
    
    class Config:
        orm_mode = True

class UserProfileUpdate(BaseModel):
    # For future profile updates
    pass

class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        is_valid, error_msg = validate_password(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v

class PasswordReset(BaseModel):
    email: EmailStr
    
    @validator('email')
    def lowercase_email(cls, v):
        return v.lower()

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        is_valid, error_msg = validate_password(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v

# Admin schemas
class InviteListResponse(BaseModel):
    invites: List[InviteResponse]
    total: int
    active: int
    used: int
    expired: int

class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    active: int

# Success/Error responses
class AuthSuccessResponse(BaseModel):
    message: str
    user: Optional[UserResponse] = None

class AuthErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None