"""
Wrestler endpoints.

Provides:
- GET /wrestlers - List all wrestlers
- GET /wrestlers/{wrestlerId} - Get wrestler summary
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import User, UserRole
from app.schemas import (
    WrestlerListResponse,
    WrestlerListItem,
    WrestlerSummary,
    ErrorResponse,
)
from app.services.wrestler_service import get_wrestlers, get_wrestler_by_id
from app.utils.dependencies import get_current_user, validate_wrestler_access

router = APIRouter()


@router.get(
    "",
    response_model=WrestlerListResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
)
async def list_wrestlers(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> WrestlerListResponse:
    """
    List all wrestlers (filtered by role access).
    
    Args:
        db: Database session.
        current_user: Authenticated user.
        limit: Maximum number of results.
        offset: Number of results to skip.
        
    Returns:
        WrestlerListResponse: List of wrestlers.
    """
    # Filter by team for coaches
    team_id = None
    if current_user.role == UserRole.COACH and current_user.team_id:
        team_id = current_user.team_id
    elif current_user.role == UserRole.ATHLETE:
        # Athletes only see themselves
        if current_user.wrestler_id:
            wrestler = await get_wrestler_by_id(db, current_user.wrestler_id)
            if wrestler:
                return WrestlerListResponse(
                    wrestlers=[
                        WrestlerListItem(
                            id=wrestler.id,
                            nameFa=wrestler.name_fa,
                            nameEn=wrestler.name_en,
                            weightClass=wrestler.weight_class,
                            imageUrl=wrestler.image_url,
                        )
                    ]
                )
        return WrestlerListResponse(wrestlers=[])
    
    wrestlers = await get_wrestlers(db, team_id=team_id, limit=limit, offset=offset)
    
    return WrestlerListResponse(
        wrestlers=[
            WrestlerListItem(
                id=w.id,
                nameFa=w.name_fa,
                nameEn=w.name_en,
                weightClass=w.weight_class,
                imageUrl=w.image_url,
            )
            for w in wrestlers
        ]
    )


@router.get(
    "/{wrestler_id}",
    response_model=WrestlerSummary,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "Wrestler not found"},
    },
)
async def get_wrestler(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> WrestlerSummary:
    """
    Get wrestler summary by ID.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user.
        
    Returns:
        WrestlerSummary: Wrestler summary.
        
    Raises:
        HTTPException: If wrestler not found or access denied.
    """
    # Validate access
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    wrestler = await get_wrestler_by_id(db, wrestler_id)
    if not wrestler:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "NOT_FOUND",
                "message": "Wrestler not found",
                "details": {"wrestler_id": wrestler_id},
            },
        )
    
    return WrestlerSummary(
        id=wrestler.id,
        nameFa=wrestler.name_fa,
        nameEn=wrestler.name_en,
        weightClass=wrestler.weight_class,
        imageUrl=wrestler.image_url,
        status=wrestler.status.value,
    )
