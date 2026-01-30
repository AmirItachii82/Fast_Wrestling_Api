"""
Authentication endpoints.

Provides:
- POST /auth/signup
- POST /auth/login
- POST /auth/refresh
- POST /auth/logout
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import User, UserRole
from app.schemas import (
    LoginRequest,
    LoginResponse,
    LoginUser,
    RefreshRequest,
    RefreshResponse,
    LogoutRequest,
    LogoutResponse,
    SignupRequest,
    SignupResponse,
    ErrorResponse,
)
from app.services.auth_service import (
    authenticate_user,
    generate_tokens,
    refresh_access_token,
    blacklist_token,
    create_user,
)

router = APIRouter()


@router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid request"},
        409: {"model": ErrorResponse, "description": "User already exists"},
    },
)
async def signup(
    request: SignupRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SignupResponse:
    """
    Register a new user.
    
    Args:
        request: Signup request with user details.
        db: Database session.
        
    Returns:
        SignupResponse: Created user information.
        
    Raises:
        HTTPException: If user already exists or validation fails.
    """
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == request.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "USER_EXISTS",
                "message": "A user with this email already exists",
                "details": {"email": request.email},
            },
        )
    
    # Map role string to UserRole enum
    try:
        role = UserRole(request.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_ROLE",
                "message": "Invalid role specified",
                "details": {"role": "Must be one of: admin, coach, athlete"},
            },
        )
    
    # Create user
    user = await create_user(
        db=db,
        email=request.email,
        password=request.password,
        name=request.name,
        role=role,
        wrestler_id=request.wrestlerId,
        team_id=request.teamId,
    )
    
    return SignupResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role.value,
        createdAt=user.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


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
