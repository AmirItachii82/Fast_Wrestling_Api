"""
Wrestler endpoints.

Provides:
- GET /wrestlers - List all wrestlers
- POST /wrestlers - Create a new wrestler
- GET /wrestlers/{wrestlerId} - Get wrestler summary
- PUT /wrestlers/{wrestlerId} - Update a wrestler
- DELETE /wrestlers/{wrestlerId} - Delete a wrestler
"""

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import User, UserRole, Wrestler, WrestlerStatus
from app.schemas import (
    WrestlerListResponse,
    WrestlerListItem,
    WrestlerSummary,
    WrestlerCreateRequest,
    WrestlerCreateResponse,
    WrestlerUpdateRequest,
    WrestlerUpdateResponse,
    WrestlerDeleteResponse,
    ErrorResponse,
)
from app.services.wrestler_service import get_wrestlers, get_wrestler_by_id
from app.utils.dependencies import get_current_user, validate_wrestler_access, require_admin_or_coach

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


@router.post(
    "",
    response_model=WrestlerCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def create_wrestler(
    request: WrestlerCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin_or_coach)],
) -> WrestlerCreateResponse:
    """
    Create a new wrestler.
    
    Args:
        request: Wrestler creation data.
        db: Database session.
        current_user: Authenticated user (admin or coach).
        
    Returns:
        WrestlerCreateResponse: Created wrestler info.
    """
    # Map status string to enum
    try:
        wrestler_status = WrestlerStatus(request.status)
    except ValueError:
        wrestler_status = WrestlerStatus.NORMAL
    
    # Coaches can only create wrestlers in their own team
    team_id = request.teamId
    if current_user.role == UserRole.COACH:
        team_id = current_user.team_id
    
    wrestler = Wrestler(
        name_fa=request.nameFa,
        name_en=request.nameEn,
        weight_class=request.weightClass,
        team_id=team_id,
        image_url=request.imageUrl,
        status=wrestler_status,
    )
    db.add(wrestler)
    await db.commit()
    await db.refresh(wrestler)
    
    return WrestlerCreateResponse(
        id=wrestler.id,
        nameFa=wrestler.name_fa,
        nameEn=wrestler.name_en,
        weightClass=wrestler.weight_class,
        status=wrestler.status.value,
        createdAt=wrestler.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
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


@router.put(
    "/{wrestler_id}",
    response_model=WrestlerUpdateResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "Wrestler not found"},
    },
)
async def update_wrestler(
    wrestler_id: str,
    request: WrestlerUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin_or_coach)],
) -> WrestlerUpdateResponse:
    """
    Update a wrestler.
    
    Args:
        wrestler_id: The wrestler ID.
        request: Wrestler update data.
        db: Database session.
        current_user: Authenticated user (admin or coach).
        
    Returns:
        WrestlerUpdateResponse: Success status.
    """
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
    
    # Coaches can only update wrestlers in their own team
    if current_user.role == UserRole.COACH and wrestler.team_id != current_user.team_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "ACCESS_DENIED",
                "message": "Cannot update wrestlers from other teams",
                "details": {},
            },
        )
    
    # Update fields if provided
    if request.nameFa is not None:
        wrestler.name_fa = request.nameFa
    if request.nameEn is not None:
        wrestler.name_en = request.nameEn
    if request.weightClass is not None:
        wrestler.weight_class = request.weightClass
    if request.imageUrl is not None:
        wrestler.image_url = request.imageUrl
    if request.status is not None:
        try:
            wrestler.status = WrestlerStatus(request.status)
        except ValueError:
            pass
    if request.teamId is not None and current_user.role == UserRole.ADMIN:
        wrestler.team_id = request.teamId
    
    await db.commit()
    
    return WrestlerUpdateResponse(success=True)


@router.delete(
    "/{wrestler_id}",
    response_model=WrestlerDeleteResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "Wrestler not found"},
    },
)
async def delete_wrestler(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin_or_coach)],
) -> WrestlerDeleteResponse:
    """
    Delete a wrestler.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user (admin or coach).
        
    Returns:
        WrestlerDeleteResponse: Success status.
    """
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
    
    # Coaches can only delete wrestlers in their own team
    if current_user.role == UserRole.COACH and wrestler.team_id != current_user.team_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "ACCESS_DENIED",
                "message": "Cannot delete wrestlers from other teams",
                "details": {},
            },
        )
    
    await db.delete(wrestler)
    await db.commit()
    
    return WrestlerDeleteResponse(success=True)
