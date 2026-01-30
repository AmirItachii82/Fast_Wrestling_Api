"""
Recovery endpoints.

Provides:
- GET /wrestlers/{wrestlerId}/recovery - Recovery metrics
- POST /wrestlers/{wrestlerId}/recovery - Create recovery metrics
- GET /wrestlers/{wrestlerId}/recovery/score - Section score
- GET /wrestlers/{wrestlerId}/recovery/charts - Recovery charts
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import User, RecoveryMetrics
from app.schemas import (
    RecoveryResponse,
    RecoveryMetricsData,
    RecoveryChartsResponse,
    SectionScoreResponse,
    RecoveryCreateRequest,
    RecoveryCreateResponse,
    ErrorResponse,
    TimeSeriesData,
)
from app.schemas.api import SleepData, SorenessData
from app.services.wrestler_service import (
    get_latest_recovery_metrics,
    get_latest_section_score,
)
from app.services.time_series_service import get_recovery_series
from app.utils.dependencies import get_current_user, validate_wrestler_access, require_admin_or_coach

router = APIRouter()


@router.get(
    "/{wrestler_id}/recovery",
    response_model=RecoveryResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def get_recovery_metrics(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> RecoveryResponse:
    """
    Get recovery metrics for a wrestler.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user.
        
    Returns:
        RecoveryResponse: Recovery metrics.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    metrics = await get_latest_recovery_metrics(db, wrestler_id)
    
    if not metrics:
        return RecoveryResponse(
            metrics=RecoveryMetricsData(
                sleepQuality=0,
                hrvScore=0,
                fatigueLevel=0,
                hydrationLevel=0,
                readinessScore=0,
            )
        )
    
    return RecoveryResponse(
        metrics=RecoveryMetricsData(
            sleepQuality=metrics.sleep_quality,
            hrvScore=metrics.hrv_score,
            fatigueLevel=metrics.fatigue_level,
            hydrationLevel=metrics.hydration_level,
            readinessScore=metrics.readiness_score,
        )
    )


@router.post(
    "/{wrestler_id}/recovery",
    response_model=RecoveryCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def create_recovery_metrics(
    wrestler_id: str,
    request: RecoveryCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin_or_coach)],
) -> RecoveryCreateResponse:
    """
    Create recovery metrics for a wrestler.
    
    Args:
        wrestler_id: The wrestler ID.
        request: Recovery metrics data.
        db: Database session.
        current_user: Authenticated user (admin or coach).
        
    Returns:
        RecoveryCreateResponse: Success status and created ID.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    metrics = RecoveryMetrics(
        wrestler_id=wrestler_id,
        sleep_quality=request.sleepQuality,
        hrv_score=request.hrvScore,
        fatigue_level=request.fatigueLevel,
        hydration_level=request.hydrationLevel,
        readiness_score=request.readinessScore,
    )
    db.add(metrics)
    await db.commit()
    await db.refresh(metrics)
    
    return RecoveryCreateResponse(success=True, id=metrics.id)


@router.get(
    "/{wrestler_id}/recovery/score",
    response_model=SectionScoreResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def get_recovery_score(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SectionScoreResponse:
    """
    Get recovery section score.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user.
        
    Returns:
        SectionScoreResponse: Section score with grade.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    score = await get_latest_section_score(db, wrestler_id, "recovery")
    
    if not score:
        return SectionScoreResponse(
            section="recovery",
            score=0,
            grade="warning",
            lastUpdated="1970-01-01",
        )
    
    return SectionScoreResponse(
        section="recovery",
        score=score.score,
        grade=score.grade.value,
        lastUpdated=score.recorded_at.strftime("%Y-%m-%d"),
    )


@router.get(
    "/{wrestler_id}/recovery/charts",
    response_model=RecoveryChartsResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def get_recovery_charts(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = Query(default=30, ge=1, le=365),
) -> RecoveryChartsResponse:
    """
    Get recovery charts.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user.
        limit: Maximum number of data points.
        
    Returns:
        RecoveryChartsResponse: Sleep, HRV, stress, and soreness data.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    def to_time_series(data: list) -> TimeSeriesData:
        if not data:
            return TimeSeriesData(dates=[], values=[])
        dates = [item[0] for item in data]
        values = [item[1] for item in data]
        return TimeSeriesData(dates=dates, values=values)
    
    # Get series data
    sleep_duration = await get_recovery_series(db, wrestler_id, "sleep_duration", limit)
    sleep_quality = await get_recovery_series(db, wrestler_id, "sleep_quality", limit)
    hrv = await get_recovery_series(db, wrestler_id, "hrv", limit)
    stress = await get_recovery_series(db, wrestler_id, "stress", limit)
    soreness_upper = await get_recovery_series(db, wrestler_id, "soreness_upper", limit)
    soreness_core = await get_recovery_series(db, wrestler_id, "soreness_core", limit)
    soreness_lower = await get_recovery_series(db, wrestler_id, "soreness_lower", limit)
    
    # Build sleep data
    sleep_dates = [item[0] for item in sleep_duration] if sleep_duration else []
    
    return RecoveryChartsResponse(
        sleep=SleepData(
            dates=sleep_dates,
            duration=[item[1] for item in sleep_duration] if sleep_duration else [],
            quality=[item[1] for item in sleep_quality] if sleep_quality else [],
        ),
        hrv=to_time_series(hrv),
        stress=to_time_series(stress),
        soreness=SorenessData(
            dates=[item[0] for item in soreness_upper] if soreness_upper else [],
            upper=[item[1] for item in soreness_upper] if soreness_upper else [],
            core=[item[1] for item in soreness_core] if soreness_core else [],
            lower=[item[1] for item in soreness_lower] if soreness_lower else [],
        ),
    )
