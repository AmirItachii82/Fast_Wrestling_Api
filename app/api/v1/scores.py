"""
Scoring endpoints.

Provides:
- GET /wrestlers/{wrestlerId}/scores/overall - Overall score
- GET /wrestlers/{wrestlerId}/scores/domains - Domain scores
- GET /wrestlers/{wrestlerId}/scores/explanation - Score explanation
"""

from typing import Annotated, List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import User, SectionScore, ScoreDriver
from app.schemas import (
    OverallScoreResponse,
    DomainScoresResponse,
    ScoreExplanationResponse,
    ErrorResponse,
)
from app.schemas.api import ScoreDriverItem
from app.services.wrestler_service import get_latest_section_score
from app.services.scoring_service import compute_overall_wrestler_score
from app.utils.dependencies import get_current_user, validate_wrestler_access

router = APIRouter()


@router.get(
    "/{wrestler_id}/scores/overall",
    response_model=OverallScoreResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def get_overall_score(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> OverallScoreResponse:
    """
    Get overall wrestler score.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user.
        
    Returns:
        OverallScoreResponse: Overall score with grade.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    # Get all section scores
    overview = await get_latest_section_score(db, wrestler_id, "overview")
    body_comp = await get_latest_section_score(db, wrestler_id, "body_composition")
    bloodwork = await get_latest_section_score(db, wrestler_id, "bloodwork")
    recovery = await get_latest_section_score(db, wrestler_id, "recovery")
    supplements = await get_latest_section_score(db, wrestler_id, "supplements")
    performance = await get_latest_section_score(db, wrestler_id, "bodybuilding_performance")
    
    # Compute overall score
    score, grade = compute_overall_wrestler_score(
        overview.score if overview else None,
        body_comp.score if body_comp else None,
        bloodwork.score if bloodwork else None,
        recovery.score if recovery else None,
        supplements.score if supplements else None,
        performance.score if performance else None,
    )
    
    # Get last updated from most recent section
    all_scores = [s for s in [overview, body_comp, bloodwork, recovery, supplements, performance] if s]
    if all_scores:
        latest = max(all_scores, key=lambda s: s.recorded_at)
        last_updated = latest.recorded_at.strftime("%Y-%m-%d")
    else:
        last_updated = "1970-01-01"
    
    return OverallScoreResponse(
        score=score,
        grade=grade.value,
        lastUpdated=last_updated,
    )


@router.get(
    "/{wrestler_id}/scores/domains",
    response_model=DomainScoresResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def get_domain_scores(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> DomainScoresResponse:
    """
    Get domain scores for a wrestler.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user.
        
    Returns:
        DomainScoresResponse: Scores for each domain.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    # Get section scores
    overview = await get_latest_section_score(db, wrestler_id, "overview")
    body_comp = await get_latest_section_score(db, wrestler_id, "body_composition")
    bloodwork = await get_latest_section_score(db, wrestler_id, "bloodwork")
    recovery = await get_latest_section_score(db, wrestler_id, "recovery")
    supplements = await get_latest_section_score(db, wrestler_id, "supplements")
    performance = await get_latest_section_score(db, wrestler_id, "bodybuilding_performance")
    
    return DomainScoresResponse(
        strength=performance.score if performance else 0,
        endurance=overview.score if overview else 0,  # Using overview as proxy
        recovery=recovery.score if recovery else 0,
        bodyComposition=body_comp.score if body_comp else 0,
        bloodwork=bloodwork.score if bloodwork else 0,
        supplements=supplements.score if supplements else 0,
    )


@router.get(
    "/{wrestler_id}/scores/explanation",
    response_model=ScoreExplanationResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def get_score_explanation(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ScoreExplanationResponse:
    """
    Get explanation of score factors.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user.
        
    Returns:
        ScoreExplanationResponse: Score drivers and notes.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    # Get latest overview section score with drivers
    result = await db.execute(
        select(SectionScore)
        .where(
            SectionScore.wrestler_id == wrestler_id,
            SectionScore.section_key == "overview",
        )
        .order_by(SectionScore.recorded_at.desc())
        .limit(1)
    )
    section_score = result.scalar_one_or_none()
    
    drivers: List[ScoreDriverItem] = []
    
    if section_score:
        # Get drivers
        result = await db.execute(
            select(ScoreDriver)
            .where(ScoreDriver.section_score_id == section_score.id)
        )
        db_drivers = result.scalars().all()
        
        for driver in db_drivers:
            drivers.append(ScoreDriverItem(
                metric=driver.metric_name,
                impact=driver.impact,
                weight=driver.weight,
            ))
    
    # If no drivers found, return default explanation
    if not drivers:
        drivers = [
            ScoreDriverItem(metric="vo2max", impact="+", weight=0.20),
            ScoreDriverItem(metric="recovery", impact="+", weight=0.15),
            ScoreDriverItem(metric="fatigueLevel", impact="-", weight=0.15),
            ScoreDriverItem(metric="bodyComposition", impact="+", weight=0.20),
            ScoreDriverItem(metric="supplementAdherence", impact="+", weight=0.10),
            ScoreDriverItem(metric="strength", impact="+", weight=0.20),
        ]
    
    return ScoreExplanationResponse(
        drivers=drivers,
        notes="Score is calculated using a weighted average of all domain metrics.",
    )
