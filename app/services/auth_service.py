"""
Authentication service for user management.

This module provides functions for:
- User authentication
- Token management
- Role-based access control
"""

from datetime import datetime, timezone
from typing import Optional
import uuid

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.models import User, UserRole, TokenBlacklist


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> Optional[User]:
    """
    Authenticate a user by email and password.
    
    Args:
        db: Database session.
        email: User email.
        password: Plain text password.
        
    Returns:
        Optional[User]: The authenticated user or None if authentication fails.
    """
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    
    return user


async def create_user(
    db: AsyncSession,
    email: str,
    password: str,
    name: str,
    role: UserRole = UserRole.ATHLETE,
    wrestler_id: Optional[str] = None,
    team_id: Optional[str] = None,
) -> User:
    """
    Create a new user.
    
    Args:
        db: Database session.
        email: User email.
        password: Plain text password (will be hashed).
        name: User's display name.
        role: User role.
        wrestler_id: Optional linked wrestler ID (for athletes).
        team_id: Optional team ID (for coaches).
        
    Returns:
        User: The created user.
    """
    user = User(
        email=email,
        password_hash=get_password_hash(password),
        name=name,
        role=role,
        wrestler_id=wrestler_id,
        team_id=team_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


def generate_tokens(user: User) -> tuple[str, str]:
    """
    Generate access and refresh tokens for a user.
    
    Args:
        user: The user to generate tokens for.
        
    Returns:
        tuple: (access_token, refresh_token)
    """
    token_data = {
        "sub": user.id,
        "role": user.role.value,
        "jti": str(uuid.uuid4()),
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return access_token, refresh_token


async def refresh_access_token(
    db: AsyncSession, refresh_token: str
) -> Optional[str]:
    """
    Refresh an access token using a refresh token.
    
    Args:
        db: Database session.
        refresh_token: The refresh token.
        
    Returns:
        Optional[str]: New access token or None if refresh fails.
    """
    payload = verify_token(refresh_token, token_type="refresh")
    if not payload:
        return None
    
    # Check if token is blacklisted
    jti = payload.get("jti")
    if jti:
        result = await db.execute(
            select(TokenBlacklist).where(TokenBlacklist.token_jti == jti)
        )
        if result.scalar_one_or_none():
            return None
    
    # Verify user still exists
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        return None
    
    # Generate new access token
    token_data = {
        "sub": user.id,
        "role": user.role.value,
        "jti": str(uuid.uuid4()),
    }
    
    return create_access_token(token_data)


async def blacklist_token(db: AsyncSession, token: str) -> bool:
    """
    Blacklist a refresh token (for logout).
    
    Args:
        db: Database session.
        token: The refresh token to blacklist.
        
    Returns:
        bool: True if successful.
    """
    payload = verify_token(token, token_type="refresh")
    if not payload:
        return False
    
    jti = payload.get("jti")
    exp = payload.get("exp")
    
    if not jti or not exp:
        return False
    
    # Add to blacklist
    blacklist_entry = TokenBlacklist(
        token_jti=jti,
        expires_at=datetime.fromtimestamp(exp, tz=timezone.utc),
    )
    db.add(blacklist_entry)
    await db.commit()
    
    return True


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    """
    Get a user by their ID.
    
    Args:
        db: Database session.
        user_id: The user ID.
        
    Returns:
        Optional[User]: The user or None if not found.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def cleanup_expired_tokens(db: AsyncSession) -> int:
    """
    Clean up expired tokens from the blacklist.
    
    Args:
        db: Database session.
        
    Returns:
        int: Number of tokens removed.
    """
    result = await db.execute(
        delete(TokenBlacklist).where(
            TokenBlacklist.expires_at < datetime.now(timezone.utc)
        )
    )
    await db.commit()
    return result.rowcount
