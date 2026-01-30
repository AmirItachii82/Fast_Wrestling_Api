"""
API dependencies for authentication and authorization.

This module provides FastAPI dependencies for:
- JWT token validation
- Role-based access control
- Wrestler access validation
"""

from typing import Annotated, List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import verify_token
from app.db.session import get_db
from app.models import User, UserRole
from app.services.auth_service import get_user_by_id
from app.services.wrestler_service import get_wrestler_by_id

# Security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Dependency to get the current authenticated user.
    
    Args:
        credentials: HTTP Bearer token credentials.
        db: Database session.
        
    Returns:
        User: The authenticated user.
        
    Raises:
        HTTPException: If token is invalid or user not found.
    """
    token = credentials.credentials
    payload = verify_token(token, token_type="access")
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user


def require_roles(allowed_roles: List[UserRole]):
    """
    Create a dependency that checks if user has one of the allowed roles.
    
    Args:
        allowed_roles: List of allowed roles.
        
    Returns:
        Dependency function that validates role.
    """
    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{current_user.role.value}' not authorized for this action",
            )
        return current_user
    
    return role_checker


# Common role dependencies
require_admin = require_roles([UserRole.ADMIN])
require_admin_or_coach = require_roles([UserRole.ADMIN, UserRole.COACH])
require_any_authenticated = require_roles([UserRole.ADMIN, UserRole.COACH, UserRole.ATHLETE])


async def validate_wrestler_access(
    wrestler_id: str,
    current_user: User,
    db: AsyncSession,
) -> None:
    """
    Validate that the current user has access to the specified wrestler.
    
    Admin: access to all wrestlers
    Coach: access to wrestlers in their team
    Athlete: access only to their own wrestler profile
    
    Args:
        wrestler_id: The wrestler ID to access.
        current_user: The current authenticated user.
        db: Database session.
        
    Raises:
        HTTPException: If access is denied.
    """
    # Admin has access to all
    if current_user.role == UserRole.ADMIN:
        return
    
    # Get the wrestler
    wrestler = await get_wrestler_by_id(db, wrestler_id)
    if not wrestler:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wrestler not found",
        )
    
    # Coach: can access wrestlers in their team
    if current_user.role == UserRole.COACH:
        if current_user.team_id and wrestler.team_id == current_user.team_id:
            return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Coach can only access wrestlers in their team",
        )
    
    # Athlete: can only access their own profile
    if current_user.role == UserRole.ATHLETE:
        if current_user.wrestler_id == wrestler_id:
            return
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Athlete can only access their own data",
        )
    
    # Default deny
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied",
    )
