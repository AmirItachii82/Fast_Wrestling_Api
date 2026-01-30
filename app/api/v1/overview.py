"""
Overview endpoints.

Provides:
- GET /wrestlers/{wrestlerId}/overview - Overview metrics
- POST /wrestlers/{wrestlerId}/overview - Create overview metrics
- GET /wrestlers/{wrestlerId}/overview/score - Section score
- GET /wrestlers/{wrestlerId}/overview/chart - Radar chart data
- POST /wrestlers/{wrestlerId}/overview/chart - Create chart data
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import User, OverviewMetrics, OverviewSeries
from app.schemas import (
    OverviewResponse,
    OverviewMetricsData,
    OverviewDeltas,
    OverviewStatusLabels,
    SectionScoreResponse,
    OverviewChartResponse,
    OverviewMetricsCreateRequest,
    OverviewMetricsCreateResponse,
    OverviewChartCreateRequest,
    OverviewChartCreateResponse,
    ErrorResponse,
)
from app.schemas.api import StatusLabel
from app.services.wrestler_service import (
    get_latest_overview_metrics,
    get_latest_section_score,
)
from app.services.time_series_service import get_overview_series
from app.services.scoring_service import compute_status_label
from app.utils.dependencies import get_current_user, validate_wrestler_access, require_admin_or_coach

router = APIRouter()


@router.get(
    "/{wrestler_id}/overview",
    response_model=OverviewResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        404: {"model": ErrorResponse, "description": "Wrestler not found"},
    },
)
async def get_overview_metrics(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> OverviewResponse:
    """
    Get overview metrics for a wrestler.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user.
        
    Returns:
        OverviewResponse: Overview metrics with deltas and status labels.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    metrics = await get_latest_overview_metrics(db, wrestler_id)
    
    if not metrics:
        # Return default values if no metrics found
        return OverviewResponse(
            metrics=OverviewMetricsData(
                overallScore=0, msi=0, mes=0, api=0,
                vo2max=0, frr=0, acs=0, bos=0
            ),
            deltas=OverviewDeltas(
                overallScore=0, msi=0, mes=0, api=0,
                vo2max=0, frr=0, acs=0, bos=0
            ),
            statusLabels=OverviewStatusLabels(
                overallScore=StatusLabel.WARNING,
                msi=StatusLabel.WARNING,
                mes=StatusLabel.WARNING,
                api=StatusLabel.WARNING,
                vo2max=StatusLabel.WARNING,
                frr=StatusLabel.WARNING,
                acs=StatusLabel.WARNING,
                bos=StatusLabel.WARNING,
            ),
        )
    
    # Calculate status labels
    def get_status(value: float, good_threshold: float, warning_threshold: float) -> StatusLabel:
        status = compute_status_label(value, good_threshold, warning_threshold)
        return StatusLabel(status)
    
    return OverviewResponse(
        metrics=OverviewMetricsData(
            overallScore=metrics.overall_score,
            msi=metrics.msi,
            mes=metrics.mes,
            api=metrics.api,
            vo2max=metrics.vo2max,
            frr=metrics.frr,
            acs=metrics.acs,
            bos=metrics.bos,
        ),
        deltas=OverviewDeltas(
            overallScore=3.2,  # TODO: Calculate from historical data
            msi=1.5,
            mes=-0.8,
            api=2.1,
            vo2max=0.4,
            frr=-1.2,
            acs=0.9,
            bos=-0.6,
        ),
        statusLabels=OverviewStatusLabels(
            overallScore=get_status(metrics.overall_score, 80, 60),
            msi=get_status(metrics.msi, 80, 60),
            mes=get_status(metrics.mes, 80, 60),
            api=get_status(metrics.api / 10, 80, 60),  # Normalize to 0-100
            vo2max=get_status(metrics.vo2max, 50, 40),
            frr=get_status(metrics.frr, 80, 60),
            acs=get_status(metrics.acs, 80, 60),
            bos=get_status(metrics.bos * 10, 80, 60),  # Normalize to 0-100
        ),
    )


@router.post(
    "/{wrestler_id}/overview",
    response_model=OverviewMetricsCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def create_overview_metrics(
    wrestler_id: str,
    request: OverviewMetricsCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin_or_coach)],
) -> OverviewMetricsCreateResponse:
    """
    Create overview metrics for a wrestler.
    
    Args:
        wrestler_id: The wrestler ID.
        request: Overview metrics data.
        db: Database session.
        current_user: Authenticated user (admin or coach).
        
    Returns:
        OverviewMetricsCreateResponse: Success status and created ID.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    metrics = OverviewMetrics(
        wrestler_id=wrestler_id,
        overall_score=request.overallScore,
        msi=request.msi,
        mes=request.mes,
        api=request.api,
        vo2max=request.vo2max,
        frr=request.frr,
        acs=request.acs,
        bos=request.bos,
    )
    db.add(metrics)
    await db.commit()
    await db.refresh(metrics)
    
    return OverviewMetricsCreateResponse(success=True, id=metrics.id)


@router.get(
    "/{wrestler_id}/overview/score",
    response_model=SectionScoreResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def get_overview_score(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SectionScoreResponse:
    """
    Get overview section score.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user.
        
    Returns:
        SectionScoreResponse: Section score with grade.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    score = await get_latest_section_score(db, wrestler_id, "overview")
    
    if not score:
        return SectionScoreResponse(
            section="overview",
            score=0,
            grade="warning",
            lastUpdated="1970-01-01",
        )
    
    return SectionScoreResponse(
        section="overview",
        score=score.score,
        grade=score.grade.value,
        lastUpdated=score.recorded_at.strftime("%Y-%m-%d"),
    )


@router.get(
    "/{wrestler_id}/overview/chart",
    response_model=OverviewChartResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def get_overview_chart(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> OverviewChartResponse:
    """
    Get overview radar chart data.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user.
        
    Returns:
        OverviewChartResponse: Labels and values for radar chart.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    series = await get_overview_series(db, wrestler_id)
    
    if not series:
        # Return default values
        return OverviewChartResponse(
            labels=["کمر", "سینه", "پاها", "بازوها", "شانه‌ها", "میان‌تنه"],
            values=[0, 0, 0, 0, 0, 0],
        )
    
    labels = [item[0] for item in series]
    values = [item[1] for item in series]
    
    return OverviewChartResponse(labels=labels, values=values)


@router.post(
    "/{wrestler_id}/overview/chart",
    response_model=OverviewChartCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def create_overview_chart(
    wrestler_id: str,
    request: OverviewChartCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(require_admin_or_coach)],
) -> OverviewChartCreateResponse:
    """
    Create overview radar chart data.
    
    Args:
        wrestler_id: The wrestler ID.
        request: Chart data with labels and values.
        db: Database session.
        current_user: Authenticated user (admin or coach).
        
    Returns:
        OverviewChartCreateResponse: Success status.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    # Validate labels and values have same length
    if len(request.labels) != len(request.values):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "VALIDATION_ERROR",
                "message": "Labels and values must have the same length",
                "details": {},
            },
        )
    
    # Create series entries for each label/value pair
    for label, value in zip(request.labels, request.values):
        series = OverviewSeries(
            wrestler_id=wrestler_id,
            label=label,
            value=value,
        )
        db.add(series)
    
    await db.commit()
    
    return OverviewChartCreateResponse(success=True)
