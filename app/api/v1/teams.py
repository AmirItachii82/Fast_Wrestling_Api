"""
Team endpoints.

Provides:
- GET /teams/{teamId}/stats - Team stats
- GET /teams/{teamId}/athletes - Team roster cards
"""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import User, UserRole, Team, Wrestler, WrestlerStatus, SectionScore
from app.schemas import (
    TeamStatsResponse,
    TeamAthletesResponse,
    ErrorResponse,
)
from app.schemas.api import TeamAthlete, AthleteInsight
from app.utils.dependencies import get_current_user, require_admin_or_coach

router = APIRouter()


async def validate_team_access(
    team_id: str,
    current_user: User,
    db: AsyncSession,
) -> Team:
    """
    Validate team access and return team.
    
    Args:
        team_id: The team ID.
        current_user: Authenticated user.
        db: Database session.
        
    Returns:
        Team: The team if access is granted.
        
    Raises:
        HTTPException: If team not found or access denied.
    """
    result = await db.execute(select(Team).where(Team.id == team_id))
    team = result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "NOT_FOUND",
                "message": "Team not found",
                "details": {"team_id": team_id},
            },
        )
    
    # Admin can access any team
    if current_user.role == UserRole.ADMIN:
        return team
    
    # Coach can only access their own team
    if current_user.role == UserRole.COACH:
        if current_user.team_id != team_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Coach can only access their own team",
            )
        return team
    
    # Athletes cannot access team endpoints
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Athletes cannot access team data",
    )


@router.get(
    "/{team_id}/stats",
    response_model=TeamStatsResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "Team not found"},
    },
)
async def get_team_stats(
    team_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin_or_coach)],
) -> TeamStatsResponse:
    """
    Get team statistics.
    
    Args:
        team_id: The team ID.
        db: Database session.
        current_user: Authenticated user (admin or coach).
        
    Returns:
        TeamStatsResponse: Team statistics.
    """
    await validate_team_access(team_id, current_user, db)
    
    # Get wrestlers in the team
    result = await db.execute(
        select(Wrestler).where(Wrestler.team_id == team_id)
    )
    wrestlers = result.scalars().all()
    
    total_athletes = len(wrestlers)
    competition_ready = sum(1 for w in wrestlers if w.status == WrestlerStatus.COMPETITION_READY)
    needs_attention = sum(1 for w in wrestlers if w.status == WrestlerStatus.ATTENTION)
    
    # Calculate average score
    if wrestlers:
        wrestler_ids = [w.id for w in wrestlers]
        result = await db.execute(
            select(func.avg(SectionScore.score))
            .where(
                SectionScore.wrestler_id.in_(wrestler_ids),
                SectionScore.section_key == "overview",
            )
        )
        avg_score = result.scalar() or 0
    else:
        avg_score = 0
    
    return TeamStatsResponse(
        totalAthletes=total_athletes,
        averageScore=round(avg_score, 1),
        competitionReady=competition_ready,
        needsAttention=needs_attention,
    )


@router.get(
    "/{team_id}/athletes",
    response_model=TeamAthletesResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "Team not found"},
    },
)
async def get_team_athletes(
    team_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin_or_coach)],
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> TeamAthletesResponse:
    """
    Get team roster with athlete cards.
    
    Args:
        team_id: The team ID.
        db: Database session.
        current_user: Authenticated user (admin or coach).
        limit: Maximum number of results.
        offset: Number of results to skip.
        
    Returns:
        TeamAthletesResponse: List of athlete cards.
    """
    await validate_team_access(team_id, current_user, db)
    
    # Get wrestlers in the team
    result = await db.execute(
        select(Wrestler)
        .where(Wrestler.team_id == team_id)
        .offset(offset)
        .limit(limit)
    )
    wrestlers = result.scalars().all()
    
    athletes: List[TeamAthlete] = []
    for wrestler in wrestlers:
        # Get overall score
        result = await db.execute(
            select(SectionScore)
            .where(
                SectionScore.wrestler_id == wrestler.id,
                SectionScore.section_key == "overview",
            )
            .order_by(SectionScore.recorded_at.desc())
            .limit(1)
        )
        score = result.scalar_one_or_none()
        overall_score = score.score if score else 0
        
        # Generate insights based on status
        insights: List[AthleteInsight] = []
        if wrestler.status == WrestlerStatus.COMPETITION_READY:
            insights.append(AthleteInsight(label="Competition Ready", type="success"))
        elif wrestler.status == WrestlerStatus.ATTENTION:
            insights.append(AthleteInsight(label="Needs Attention", type="warning"))
        
        athletes.append(TeamAthlete(
            id=wrestler.id,
            nameFa=wrestler.name_fa,
            weightClass=wrestler.weight_class,
            overallScore=overall_score,
            currentActivity=None,
            insights=insights,
            trainingWeek=6,  # TODO: Calculate from programs
            totalWeeks=8,
        ))
    
    return TeamAthletesResponse(athletes=athletes)
