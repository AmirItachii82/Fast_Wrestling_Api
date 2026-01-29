"""
Supplements endpoints.

Provides:
- GET /wrestlers/{wrestlerId}/supplements - Summary metrics
- GET /wrestlers/{wrestlerId}/supplements/score - Section score
- GET /wrestlers/{wrestlerId}/supplements/charts - Charts
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import User
from app.schemas import (
    SupplementsResponse,
    SupplementsMetricsData,
    SupplementsChartsResponse,
    SectionScoreResponse,
    ErrorResponse,
    TimeSeriesData,
)
from app.schemas.api import StackOverview, SupplementItem
from app.services.wrestler_service import (
    get_latest_supplements_metrics,
    get_latest_section_score,
)
from app.services.time_series_service import get_supplements_series
from app.utils.dependencies import get_current_user, validate_wrestler_access

router = APIRouter()


@router.get(
    "/{wrestler_id}/supplements",
    response_model=SupplementsResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def get_supplements_metrics(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SupplementsResponse:
    """
    Get supplements metrics for a wrestler.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user.
        
    Returns:
        SupplementsResponse: Supplements metrics.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    metrics = await get_latest_supplements_metrics(db, wrestler_id)
    
    if not metrics:
        return SupplementsResponse(
            metrics=SupplementsMetricsData(
                adherenceRate=0,
                monthlyProgress="0%",
                performanceCorrelation=0,
                totalSupplements=0,
                creatineDailyGrams=0,
                proteinDailyGrams=0,
                hydrationLiters=0,
            )
        )
    
    return SupplementsResponse(
        metrics=SupplementsMetricsData(
            adherenceRate=metrics.adherence_rate,
            monthlyProgress=metrics.monthly_progress,
            performanceCorrelation=metrics.performance_corr,
            totalSupplements=metrics.total_supplements,
            creatineDailyGrams=metrics.creatine_daily_grams,
            proteinDailyGrams=metrics.protein_daily_grams,
            hydrationLiters=metrics.hydration_liters,
        )
    )


@router.get(
    "/{wrestler_id}/supplements/score",
    response_model=SectionScoreResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def get_supplements_score(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SectionScoreResponse:
    """
    Get supplements section score.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user.
        
    Returns:
        SectionScoreResponse: Section score with grade.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    score = await get_latest_section_score(db, wrestler_id, "supplements")
    
    if not score:
        return SectionScoreResponse(
            section="supplements",
            score=0,
            grade="warning",
            lastUpdated="1970-01-01",
        )
    
    return SectionScoreResponse(
        section="supplements",
        score=score.score,
        grade=score.grade.value,
        lastUpdated=score.recorded_at.strftime("%Y-%m-%d"),
    )


@router.get(
    "/{wrestler_id}/supplements/charts",
    response_model=SupplementsChartsResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def get_supplements_charts(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = Query(default=30, ge=1, le=365),
) -> SupplementsChartsResponse:
    """
    Get supplements charts.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user.
        limit: Maximum number of data points.
        
    Returns:
        SupplementsChartsResponse: Chart data.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    def to_time_series(data: list) -> TimeSeriesData:
        if not data:
            return TimeSeriesData(dates=[], values=[])
        dates = [item[0] for item in data]
        values = [item[1] for item in data]
        return TimeSeriesData(dates=dates, values=values)
    
    # Get series data
    creatine = await get_supplements_series(db, wrestler_id, "creatine", limit)
    protein = await get_supplements_series(db, wrestler_id, "protein", limit)
    adherence = await get_supplements_series(db, wrestler_id, "adherence", limit)
    hydration = await get_supplements_series(db, wrestler_id, "hydration", limit)
    perf_corr = await get_supplements_series(db, wrestler_id, "performance_correlation", limit)
    
    # Default stack overview
    stack = StackOverview(
        supplements=[
            SupplementItem(name="Creatine", daily=True),
            SupplementItem(name="Omega-3", daily=True),
            SupplementItem(name="Protein", daily=True),
            SupplementItem(name="Vitamin D", daily=True),
        ]
    )
    
    return SupplementsChartsResponse(
        creatine=to_time_series(creatine),
        protein=to_time_series(protein),
        adherence=to_time_series(adherence),
        hydration=to_time_series(hydration),
        performanceCorrelation=to_time_series(perf_corr),
        stackOverview=stack,
    )
