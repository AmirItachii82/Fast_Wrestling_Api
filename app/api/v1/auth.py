"""
Authentication endpoints.

Provides:
- POST /auth/login
- POST /auth/refresh
- POST /auth/logout
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas import (
    LoginRequest,
    LoginResponse,
    LoginUser,
    RefreshRequest,
    RefreshResponse,
    LogoutRequest,
    LogoutResponse,
    ErrorResponse,
)
from app.services.auth_service import (
    authenticate_user,
    generate_tokens,
    refresh_access_token,
    blacklist_token,
)

router = APIRouter()


@router.post(
    "/login",
    response_model=LoginResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
    },
)
async def login(
    request: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LoginResponse:
    """
    Authenticate user and return JWT tokens.
    
    Args:
        request: Login credentials (email, password).
        db: Database session.
        
    Returns:
        LoginResponse: Access token, refresh token, and user info.
        
    Raises:
        HTTPException: If credentials are invalid.
    """
    user = await authenticate_user(db, request.email, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "INVALID_CREDENTIALS",
                "message": "Invalid email or password",
                "details": {},
            },
        )
    
    access_token, refresh_token = generate_tokens(user)
    
    return LoginResponse(
        accessToken=access_token,
        refreshToken=refresh_token,
        user=LoginUser(
            id=user.id,
            name=user.name,
            role=user.role.value,
        ),
    )


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid refresh token"},
    },
)
async def refresh(
    request: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RefreshResponse:
    """
    Refresh access token using refresh token.
    
    Args:
        request: Refresh token.
        db: Database session.
        
    Returns:
        RefreshResponse: New access token.
        
    Raises:
        HTTPException: If refresh token is invalid.
    """
    new_access_token = await refresh_access_token(db, request.refreshToken)
    
    if not new_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "INVALID_REFRESH_TOKEN",
                "message": "Invalid or expired refresh token",
                "details": {},
            },
        )
    
    return RefreshResponse(accessToken=new_access_token)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid token"},
    },
)
async def logout(
    request: LogoutRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> LogoutResponse:
    """
    Logout user by blacklisting their refresh token.
    
    Args:
        request: Refresh token to blacklist.
        db: Database session.
        
    Returns:
        LogoutResponse: Success status.
        
    Raises:
        HTTPException: If token is invalid.
    """
    success = await blacklist_token(db, request.refreshToken)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "INVALID_TOKEN",
                "message": "Invalid refresh token",
                "details": {},
            },
        )
    
    return LogoutResponse(success=True)
