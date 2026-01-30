"""
Bodybuilding Performance endpoints.

Provides:
- GET /wrestlers/{wrestlerId}/bodybuilding-performance - Summary metrics
- POST /wrestlers/{wrestlerId}/bodybuilding-performance - Create metrics
- GET /wrestlers/{wrestlerId}/bodybuilding-performance/score - Section score
- GET /wrestlers/{wrestlerId}/bodybuilding-performance/charts - Charts
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import User, PerformanceMetrics
from app.schemas import (
    PerformanceResponse,
    PerformanceMetricsData,
    PerformanceChartsResponse,
    SectionScoreResponse,
    PerformanceCreateRequest,
    PerformanceCreateResponse,
    ErrorResponse,
    TimeSeriesData,
)
from app.schemas.api import (
    StrengthCharts,
    CardioCharts,
    AnalyticsCharts,
    BodybuildingCharts,
    HRZones,
    RPEBuckets,
    LabelValuePair,
)
from app.services.wrestler_service import (
    get_latest_performance_metrics,
    get_latest_section_score,
)
from app.services.time_series_service import get_performance_series
from app.utils.dependencies import get_current_user, validate_wrestler_access, require_admin_or_coach

router = APIRouter()


@router.get(
    "/{wrestler_id}/bodybuilding-performance",
    response_model=PerformanceResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def get_performance_metrics_endpoint(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> PerformanceResponse:
    """
    Get performance metrics for a wrestler.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user.
        
    Returns:
        PerformanceResponse: Performance metrics.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    metrics = await get_latest_performance_metrics(db, wrestler_id)
    
    if not metrics:
        return PerformanceResponse(
            metrics=PerformanceMetricsData(
                benchPressMax=0,
                squatMax=0,
                deadliftMax=0,
                vo2max=0,
                bodyFatPercentage=0,
                performanceScore=0,
            )
        )
    
    return PerformanceResponse(
        metrics=PerformanceMetricsData(
            benchPressMax=metrics.bench_max,
            squatMax=metrics.squat_max,
            deadliftMax=metrics.deadlift_max,
            vo2max=metrics.vo2max,
            bodyFatPercentage=metrics.body_fat_percent,
            performanceScore=metrics.performance_score,
        )
    )


@router.post(
    "/{wrestler_id}/bodybuilding-performance",
    response_model=PerformanceCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def create_performance_metrics(
    wrestler_id: str,
    request: PerformanceCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin_or_coach)],
) -> PerformanceCreateResponse:
    """
    Create performance metrics for a wrestler.
    
    Args:
        wrestler_id: The wrestler ID.
        request: Performance metrics data.
        db: Database session.
        current_user: Authenticated user (admin or coach).
        
    Returns:
        PerformanceCreateResponse: Success status and created ID.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    metrics = PerformanceMetrics(
        wrestler_id=wrestler_id,
        bench_max=request.benchPressMax,
        squat_max=request.squatMax,
        deadlift_max=request.deadliftMax,
        vo2max=request.vo2max,
        body_fat_percent=request.bodyFatPercentage,
        performance_score=request.performanceScore,
    )
    db.add(metrics)
    await db.commit()
    await db.refresh(metrics)
    
    return PerformanceCreateResponse(success=True, id=metrics.id)


@router.get(
    "/{wrestler_id}/bodybuilding-performance/score",
    response_model=SectionScoreResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def get_performance_score(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SectionScoreResponse:
    """
    Get performance section score.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user.
        
    Returns:
        SectionScoreResponse: Section score with grade.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    score = await get_latest_section_score(db, wrestler_id, "bodybuilding_performance")
    
    if not score:
        return SectionScoreResponse(
            section="bodybuilding_performance",
            score=0,
            grade="warning",
            lastUpdated="1970-01-01",
        )
    
    return SectionScoreResponse(
        section="bodybuilding_performance",
        score=score.score,
        grade=score.grade.value,
        lastUpdated=score.recorded_at.strftime("%Y-%m-%d"),
    )


@router.get(
    "/{wrestler_id}/bodybuilding-performance/charts",
    response_model=PerformanceChartsResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def get_performance_charts(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = Query(default=30, ge=1, le=365),
) -> PerformanceChartsResponse:
    """
    Get performance charts.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user.
        limit: Maximum number of data points.
        
    Returns:
        PerformanceChartsResponse: Chart data.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    def to_time_series(data: list) -> TimeSeriesData:
        if not data:
            return TimeSeriesData(dates=[], values=[])
        dates = [item[0] for item in data]
        values = [item[1] for item in data]
        return TimeSeriesData(dates=dates, values=values)
    
    # Get series data
    bench = await get_performance_series(db, wrestler_id, "bench", limit)
    squat = await get_performance_series(db, wrestler_id, "squat", limit)
    deadlift = await get_performance_series(db, wrestler_id, "deadlift", limit)
    vo2max = await get_performance_series(db, wrestler_id, "vo2max", limit)
    volume_load = await get_performance_series(db, wrestler_id, "volume_load", limit)
    
    return PerformanceChartsResponse(
        strength=StrengthCharts(
            bench=to_time_series(bench),
            squat=to_time_series(squat),
            deadlift=to_time_series(deadlift),
        ),
        cardio=CardioCharts(
            vo2max=to_time_series(vo2max),
            hrZones=HRZones(zones=["Z1", "Z2", "Z3", "Z4", "Z5"], values=[20, 30, 25, 15, 10]),
        ),
        analytics=AnalyticsCharts(
            volumeLoad=to_time_series(volume_load),
            rpe=RPEBuckets(buckets=["6", "7", "8", "9", "10"], values=[15, 25, 35, 20, 5]),
        ),
        bodybuilding=BodybuildingCharts(
            symmetry=LabelValuePair(labels=["Upper", "Lower"], values=[85, 82]),
            activation=LabelValuePair(labels=["Core", "Legs", "Arms"], values=[80, 90, 85]),
        ),
    )
