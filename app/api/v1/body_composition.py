"""
Body Composition endpoints.

Provides:
- GET /wrestlers/{wrestlerId}/body-composition - Summary metrics
- GET /wrestlers/{wrestlerId}/body-composition/score - Section score
- GET /wrestlers/{wrestlerId}/body-composition/trends - Trend charts
- GET /wrestlers/{wrestlerId}/body-composition/inbody - InBody breakdown
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import User
from app.schemas import (
    BodyCompositionResponse,
    BodyCompositionMetricsData,
    BodyCompositionTrendsResponse,
    SectionScoreResponse,
    InBodyResponse,
    ErrorResponse,
    TimeSeriesData,
)
from app.services.wrestler_service import (
    get_latest_body_composition_metrics,
    get_latest_section_score,
)
from app.services.time_series_service import get_body_composition_series
from app.utils.dependencies import get_current_user, validate_wrestler_access

router = APIRouter()


@router.get(
    "/{wrestler_id}/body-composition",
    response_model=BodyCompositionResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def get_body_composition_metrics(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> BodyCompositionResponse:
    """
    Get body composition metrics for a wrestler.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user.
        
    Returns:
        BodyCompositionResponse: Body composition metrics.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    metrics = await get_latest_body_composition_metrics(db, wrestler_id)
    
    if not metrics:
        return BodyCompositionResponse(
            metrics=BodyCompositionMetricsData(
                weight=0, bodyFatPercentage=0, muscleMass=0,
                bmr=1500, powerToWeight=0
            )
        )
    
    return BodyCompositionResponse(
        metrics=BodyCompositionMetricsData(
            weight=metrics.weight,
            bodyFatPercentage=metrics.body_fat_percent,
            muscleMass=metrics.muscle_mass,
            bmr=metrics.bmr,
            powerToWeight=metrics.power_to_weight,
        )
    )


@router.get(
    "/{wrestler_id}/body-composition/score",
    response_model=SectionScoreResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def get_body_composition_score(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SectionScoreResponse:
    """
    Get body composition section score.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user.
        
    Returns:
        SectionScoreResponse: Section score with grade.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    score = await get_latest_section_score(db, wrestler_id, "body_composition")
    
    if not score:
        return SectionScoreResponse(
            section="body_composition",
            score=0,
            grade="warning",
            lastUpdated="1970-01-01",
        )
    
    return SectionScoreResponse(
        section="body_composition",
        score=score.score,
        grade=score.grade.value,
        lastUpdated=score.recorded_at.strftime("%Y-%m-%d"),
    )


@router.get(
    "/{wrestler_id}/body-composition/trends",
    response_model=BodyCompositionTrendsResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def get_body_composition_trends(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = Query(default=30, ge=1, le=365),
) -> BodyCompositionTrendsResponse:
    """
    Get body composition trend charts.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user.
        limit: Maximum number of data points.
        
    Returns:
        BodyCompositionTrendsResponse: Trend data for charts.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    # Get series data
    power_to_weight = await get_body_composition_series(
        db, wrestler_id, "power_to_weight", limit
    )
    body_weight = await get_body_composition_series(
        db, wrestler_id, "weight", limit
    )
    body_fat = await get_body_composition_series(
        db, wrestler_id, "body_fat", limit
    )
    
    def to_time_series(data: list) -> TimeSeriesData:
        if not data:
            return TimeSeriesData(dates=[], values=[])
        dates = [item[0] for item in data]
        values = [item[1] for item in data]
        return TimeSeriesData(dates=dates, values=values)
    
    return BodyCompositionTrendsResponse(
        powerToWeight=to_time_series(power_to_weight),
        bodyWeight=to_time_series(body_weight),
        bodyFat=to_time_series(body_fat),
    )


@router.get(
    "/{wrestler_id}/body-composition/inbody",
    response_model=InBodyResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def get_inbody_breakdown(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> InBodyResponse:
    """
    Get InBody breakdown data.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user.
        
    Returns:
        InBodyResponse: InBody breakdown metrics.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    metrics = await get_latest_body_composition_metrics(db, wrestler_id)
    
    if not metrics:
        return InBodyResponse(
            intracellularWater=0,
            extracellularWater=0,
            visceralFatLevel=0,
            phaseAngle=0,
        )
    
    return InBodyResponse(
        intracellularWater=metrics.intracellular_water or 0,
        extracellularWater=metrics.extracellular_water or 0,
        visceralFatLevel=metrics.visceral_fat_level or 0,
        phaseAngle=metrics.phase_angle or 0,
    )
