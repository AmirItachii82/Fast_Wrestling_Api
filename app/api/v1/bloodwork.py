"""
Bloodwork endpoints.

Provides:
- GET /wrestlers/{wrestlerId}/bloodwork - Panels summary
- GET /wrestlers/{wrestlerId}/bloodwork/score - Section score
- GET /wrestlers/{wrestlerId}/bloodwork/charts - Panel charts
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import User
from app.schemas import (
    BloodworkResponse,
    BloodworkMetricsData,
    BloodworkChartsResponse,
    SectionScoreResponse,
    ErrorResponse,
    TimeSeriesData,
)
from app.schemas.api import CBCPanel, LipidsPanel
from app.services.wrestler_service import (
    get_latest_bloodwork_metrics,
    get_latest_section_score,
)
from app.services.time_series_service import get_bloodwork_series
from app.utils.dependencies import get_current_user, validate_wrestler_access

router = APIRouter()


@router.get(
    "/{wrestler_id}/bloodwork",
    response_model=BloodworkResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def get_bloodwork_metrics(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> BloodworkResponse:
    """
    Get bloodwork metrics for a wrestler.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user.
        
    Returns:
        BloodworkResponse: Bloodwork metrics.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    metrics = await get_latest_bloodwork_metrics(db, wrestler_id)
    
    if not metrics:
        return BloodworkResponse(
            metrics=BloodworkMetricsData(
                hemoglobin=0,
                hematocrit=0,
                testosteroneLevel=0,
                lastTestDate="1970-01-01",
                status="attention",
            )
        )
    
    return BloodworkResponse(
        metrics=BloodworkMetricsData(
            hemoglobin=metrics.hemoglobin,
            hematocrit=metrics.hematocrit,
            testosteroneLevel=metrics.testosterone,
            lastTestDate=metrics.last_test_date.strftime("%Y-%m-%d"),
            status=metrics.status,
        )
    )


@router.get(
    "/{wrestler_id}/bloodwork/score",
    response_model=SectionScoreResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def get_bloodwork_score(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SectionScoreResponse:
    """
    Get bloodwork section score.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user.
        
    Returns:
        SectionScoreResponse: Section score with grade.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    score = await get_latest_section_score(db, wrestler_id, "bloodwork")
    
    if not score:
        return SectionScoreResponse(
            section="bloodwork",
            score=0,
            grade="warning",
            lastUpdated="1970-01-01",
        )
    
    return SectionScoreResponse(
        section="bloodwork",
        score=score.score,
        grade=score.grade.value,
        lastUpdated=score.recorded_at.strftime("%Y-%m-%d"),
    )


@router.get(
    "/{wrestler_id}/bloodwork/charts",
    response_model=BloodworkChartsResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def get_bloodwork_charts(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = Query(default=30, ge=1, le=365),
) -> BloodworkChartsResponse:
    """
    Get bloodwork panel charts.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user.
        limit: Maximum number of data points.
        
    Returns:
        BloodworkChartsResponse: CBC and lipids panel data.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    def to_time_series(data: list) -> TimeSeriesData:
        if not data:
            return TimeSeriesData(dates=[], values=[])
        dates = [item[0] for item in data]
        values = [item[1] for item in data]
        return TimeSeriesData(dates=dates, values=values)
    
    # CBC panel
    wbc = await get_bloodwork_series(db, wrestler_id, "cbc", "wbc", limit)
    rbc = await get_bloodwork_series(db, wrestler_id, "cbc", "rbc", limit)
    hemoglobin = await get_bloodwork_series(db, wrestler_id, "cbc", "hemoglobin", limit)
    hematocrit = await get_bloodwork_series(db, wrestler_id, "cbc", "hematocrit", limit)
    platelets = await get_bloodwork_series(db, wrestler_id, "cbc", "platelets", limit)
    
    # Lipids panel
    ldl = await get_bloodwork_series(db, wrestler_id, "lipids", "ldl", limit)
    hdl = await get_bloodwork_series(db, wrestler_id, "lipids", "hdl", limit)
    triglycerides = await get_bloodwork_series(db, wrestler_id, "lipids", "triglycerides", limit)
    
    return BloodworkChartsResponse(
        cbc=CBCPanel(
            wbc=to_time_series(wbc),
            rbc=to_time_series(rbc),
            hemoglobin=to_time_series(hemoglobin),
            hematocrit=to_time_series(hematocrit),
            platelets=to_time_series(platelets),
        ),
        lipids=LipidsPanel(
            ldl=to_time_series(ldl),
            hdl=to_time_series(hdl),
            triglycerides=to_time_series(triglycerides),
        ),
    )
