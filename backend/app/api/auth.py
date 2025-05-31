# backend/app/api/auth.py
"""
Authentication API endpoints
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.database import get_db
from models.auth import User, Invite, UserSession, UserTier
from schemas.auth import (
    UserRegister, UserLogin, TokenResponse, UserResponse,
    RefreshTokenRequest, InviteCreate, InviteResponse,
    InviteListResponse, AuthSuccessResponse, PasswordChange
)
from core.security import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, decode_token, generate_invite_code,
    generate_secure_token, ACCESS_TOKEN_EXPIRE_MINUTES
)
from core.dependencies import get_current_user, get_current_admin_user
from services.email_service import email_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserRegister,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Register new user with invite code
    """
    # Check if email already exists
    existing_user = db.query(User).filter(
        func.lower(User.email) == user_data.email.lower()
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate invite code
    invite = db.query(Invite).filter(
        Invite.code == user_data.invite_code
    ).first()
    
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid invite code"
        )
    
    if invite.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite code already used"
        )
    
    if invite.is_expired:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invite code expired"
        )
    
    # Check if invite is for specific email
    if invite.email and invite.email.lower() != user_data.email.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invite is for a different email address"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email.lower(),
        password_hash=get_password_hash(user_data.password),
        is_active=True,
        is_admin=False
    )
    
    db.add(new_user)
    db.flush()  # Get user ID without committing
    
    # Mark invite as used
    invite.used_by = new_user.id
    invite.used_at = datetime.utcnow()
    
    # Create default user tier
    user_tier = UserTier(
        user_id=new_user.id,
        tier="free"
    )
    db.add(user_tier)
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(new_user.id)})
    refresh_token_str = generate_secure_token()
    
    # Save refresh token
    user_session = UserSession(
        user_id=new_user.id,
        refresh_token=refresh_token_str,
        expires_at=datetime.utcnow() + timedelta(days=7),
        ip_address=request.client.host,
        user_agent=request.headers.get("User-Agent")
    )
    db.add(user_session)
    
    db.commit()
    
    # Send welcome email (async, don't wait)
    try:
        email_service.send_welcome_email(new_user.email, new_user.email.split('@')[0])
    except Exception as e:
        logger.error(f"Failed to send welcome email: {e}")
    
    logger.info(f"New user registered: {new_user.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/login", response_model=TokenResponse)
async def login(
    user_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Login with email and password
    """
    # Find user
    user = db.query(User).filter(
        func.lower(User.email) == user_data.email.lower()
    ).first()
    
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token_str = generate_secure_token()
    
    # Save refresh token
    user_session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token_str,
        expires_at=datetime.utcnow() + timedelta(days=7),
        ip_address=request.client.host,
        user_agent=request.headers.get("User-Agent")
    )
    db.add(user_session)
    
    db.commit()
    
    logger.info(f"User logged in: {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    # Find session
    session = db.query(UserSession).filter(
        UserSession.refresh_token == token_data.refresh_token
    ).first()
    
    if not session or not session.is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Get user
    user = session.user
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Revoke old session
    session.revoked_at = datetime.utcnow()
    
    # Create new tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token_str = generate_secure_token()
    
    # Save new refresh token
    new_session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token_str,
        expires_at=datetime.utcnow() + timedelta(days=7),
        ip_address=request.client.host,
        user_agent=request.headers.get("User-Agent")
    )
    db.add(new_session)
    
    db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token_str,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout current user (revoke all sessions)
    """
    # Revoke all user sessions
    db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.revoked_at == None
    ).update({"revoked_at": datetime.utcnow()})
    
    db.commit()
    
    logger.info(f"User logged out: {current_user.email}")
    
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        is_active=current_user.is_active,
        is_admin=current_user.is_admin,
        email_verified=current_user.email_verified,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
        tier=current_user.tier.tier if current_user.tier else "free"
    )

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change current user's password
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Update password
    current_user.password_hash = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    
    # Revoke all sessions except current
    # (User will need to login again on other devices)
    db.query(UserSession).filter(
        UserSession.user_id == current_user.id,
        UserSession.revoked_at == None
    ).update({"revoked_at": datetime.utcnow()})
    
    db.commit()
    
    return {"message": "Password changed successfully"}

# Admin endpoints for invite management
@router.post("/invites", response_model=InviteResponse)
async def create_invite(
    invite_data: InviteCreate,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create new invite (admin only)
    """
    # Generate unique invite code
    code = generate_invite_code()
    while db.query(Invite).filter(Invite.code == code).first():
        code = generate_invite_code()
    
    # Create invite
    invite = Invite(
        code=code,
        email=invite_data.email,
        notes=invite_data.notes,
        created_by=current_admin.id,
        expires_at=datetime.utcnow() + timedelta(days=invite_data.expires_in_days)
    )
    
    db.add(invite)
    db.commit()
    db.refresh(invite)
    
    # Send invite email if email provided
    if invite_data.email:
        try:
            email_service.send_invite_email(
                invite_data.email,
                code,
                current_admin.email
            )
        except Exception as e:
            logger.error(f"Failed to send invite email: {e}")
    
    logger.info(f"Invite created by {current_admin.email}: {code}")
    
    return InviteResponse(
        id=invite.id,
        code=invite.code,
        email=invite.email,
        created_at=invite.created_at,
        expires_at=invite.expires_at,
        is_used=invite.is_used,
        is_expired=invite.is_expired,
        notes=invite.notes
    )

@router.get("/invites", response_model=InviteListResponse)
async def list_invites(
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
    include_used: bool = False,
    include_expired: bool = False
):
    """
    List all invites (admin only)
    """
    query = db.query(Invite)
    
    if not include_used:
        query = query.filter(Invite.used_by == None)
    
    if not include_expired:
        query = query.filter(Invite.expires_at > datetime.utcnow())
    
    invites = query.order_by(Invite.created_at.desc()).all()
    
    # Calculate stats
    total = len(invites)
    active = sum(1 for i in invites if not i.is_used and not i.is_expired)
    used = sum(1 for i in invites if i.is_used)
    expired = sum(1 for i in invites if i.is_expired and not i.is_used)
    
    return InviteListResponse(
        invites=[
            InviteResponse(
                id=invite.id,
                code=invite.code,
                email=invite.email,
                created_at=invite.created_at,
                expires_at=invite.expires_at,
                is_used=invite.is_used,
                is_expired=invite.is_expired,
                notes=invite.notes
            )
            for invite in invites
        ],
        total=total,
        active=active,
        used=used,
        expired=expired
    )

@router.delete("/invites/{invite_id}")
async def revoke_invite(
    invite_id: str,
    current_admin: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Revoke an invite (admin only)
    """
    invite = db.query(Invite).filter(Invite.id == invite_id).first()
    
    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite not found"
        )
    
    if invite.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot revoke used invite"
        )
    
    db.delete(invite)
    db.commit()
    
    logger.info(f"Invite revoked by {current_admin.email}: {invite.code}")
    
    return {"message": "Invite revoked successfully"}