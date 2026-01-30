"""
Legacy data endpoints for Fittechno database.

Provides access to legacy measurement data with filtering and session date resolution.

Endpoints:
- GET /data/athletes - List legacy athletes
- GET /data/sessions - List session times
- GET /data/metrics - List metric definitions
- GET /data/body-composition/freestyle - Body composition (freestyle) with dates
- GET /data/body-composition/greco-roman - Body composition (greco-roman) with dates
- GET /data/chestbelt-hr - Chestbelt heart rate data with dates
- GET /data/fitness - Fitness data with dates
- GET /data/urion-analysis - Urion analysis data with dates
"""

import math
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import User
from app.schemas import (
    ErrorResponse,
    LegacyAthleteListResponse,
    LegacyAthleteResponse,
    SessionTimeListResponse,
    SessionTimeResponse,
    MetricDefinitionListResponse,
    MetricDefinitionResponse,
    LegacyBodyCompositionListResponse,
    LegacyBodyCompositionResponse,
    LegacyChestbeltHRListResponse,
    LegacyChestbeltHRResponse,
    LegacyFitnessListResponse,
    LegacyFitnessResponse,
    LegacyUrionAnalysisListResponse,
    LegacyUrionAnalysisResponse,
    PaginationInfo,
)
from app.services.legacy_data_service import (
    get_legacy_athletes,
    get_session_times,
    get_legacy_metrics,
    get_body_composition_fs_with_dates,
    get_body_composition_gr_with_dates,
    get_chestbelt_hr_gr_with_dates,
    get_fitness_fs_with_dates,
    get_urion_analysis_gr_with_dates,
)
from app.utils.dependencies import get_current_user

router = APIRouter()


def calculate_pagination(total: int, page: int, per_page: int) -> PaginationInfo:
    """Calculate pagination metadata."""
    total_pages = math.ceil(total / per_page) if per_page > 0 else 0
    return PaginationInfo(
        page=page,
        perPage=per_page,
        total=total,
        totalPages=total_pages,
    )


# ============================================================================
# Legacy Athletes Endpoints
# ============================================================================


@router.get(
    "/athletes",
    response_model=LegacyAthleteListResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
    summary="List Legacy Athletes",
    description="Get a paginated list of athletes from the legacy Fittechno database.",
)
async def list_legacy_athletes(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=50, ge=1, le=100, alias="perPage", description="Items per page"),
    athlete_name: Optional[str] = Query(default=None, alias="athleteName", description="Filter by athlete name"),
) -> LegacyAthleteListResponse:
    """
    List legacy athletes with pagination and optional filtering.
    
    Args:
        db: Database session.
        current_user: Authenticated user.
        page: Page number (1-indexed).
        per_page: Number of items per page (max 100).
        athlete_name: Optional partial match filter for athlete name.
        
    Returns:
        LegacyAthleteListResponse: List of athletes with pagination info.
    """
    athletes, total = await get_legacy_athletes(db, page, per_page, athlete_name)
    
    athlete_responses = [
        LegacyAthleteResponse(
            id=a.id,
            athleteName=a.athlete_name,
            field=a.field,
            name=a.name,
            createdAt=a.created_at.isoformat() if a.created_at else None,
        )
        for a in athletes
    ]
    
    return LegacyAthleteListResponse(
        athletes=athlete_responses,
        pagination=calculate_pagination(total, page, per_page),
    )


# ============================================================================
# Session Times Endpoints
# ============================================================================


@router.get(
    "/sessions",
    response_model=SessionTimeListResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
    summary="List Session Times",
    description="Get a paginated list of session times with date information.",
)
async def list_session_times(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=50, ge=1, le=100, alias="perPage", description="Items per page"),
    athlete_name: Optional[str] = Query(default=None, alias="athleteName", description="Filter by athlete name"),
    test_category: Optional[str] = Query(default=None, alias="testCategory", description="Filter by test category"),
    date_from: Optional[str] = Query(default=None, alias="dateFrom", description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(default=None, alias="dateTo", description="Filter to date (YYYY-MM-DD)"),
) -> SessionTimeListResponse:
    """
    List session times with pagination and optional filtering.
    
    Args:
        db: Database session.
        current_user: Authenticated user.
        page: Page number (1-indexed).
        per_page: Number of items per page (max 100).
        athlete_name: Optional filter by athlete name.
        test_category: Optional filter by test category.
        date_from: Optional filter by start date (YYYY-MM-DD).
        date_to: Optional filter by end date (YYYY-MM-DD).
        
    Returns:
        SessionTimeListResponse: List of sessions with pagination info.
    """
    sessions, total = await get_session_times(
        db, page, per_page, athlete_name, test_category, date_from, date_to
    )
    
    session_responses = [
        SessionTimeResponse(
            sessionId=s.session_id,
            athleteId=s.athlete_id,
            athleteName=s.athlete_name,
            miladiDate=s.miladi_date,
            shamsiDate=s.shamsi_date,
            startTime=s.start_time,
            testCategory=s.test_category,
            createdAt=s.created_at.isoformat() if s.created_at else None,
        )
        for s in sessions
    ]
    
    return SessionTimeListResponse(
        sessions=session_responses,
        pagination=calculate_pagination(total, page, per_page),
    )


# ============================================================================
# Metric Definitions Endpoints
# ============================================================================


@router.get(
    "/metrics",
    response_model=MetricDefinitionListResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
    summary="List Metric Definitions",
    description="Get a paginated list of metric definitions.",
)
async def list_metric_definitions(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=50, ge=1, le=100, alias="perPage", description="Items per page"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
) -> MetricDefinitionListResponse:
    """
    List metric definitions with pagination and optional filtering.
    
    Args:
        db: Database session.
        current_user: Authenticated user.
        page: Page number (1-indexed).
        per_page: Number of items per page (max 100).
        category: Optional filter by category.
        
    Returns:
        MetricDefinitionListResponse: List of metrics with pagination info.
    """
    metrics, total = await get_legacy_metrics(db, page, per_page, category)
    
    metric_responses = [
        MetricDefinitionResponse(
            id=m.id,
            metricName=m.metric_name,
            metricMethod=m.metric_method,
            category=m.category,
        )
        for m in metrics
    ]
    
    return MetricDefinitionListResponse(
        metrics=metric_responses,
        pagination=calculate_pagination(total, page, per_page),
    )


# ============================================================================
# Body Composition Endpoints (Legacy)
# ============================================================================


@router.get(
    "/body-composition/freestyle",
    response_model=LegacyBodyCompositionListResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
    summary="List Body Composition (Freestyle)",
    description="Get freestyle body composition measurements with session dates resolved.",
)
async def list_body_composition_freestyle(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=50, ge=1, le=100, alias="perPage", description="Items per page"),
    athlete_name: Optional[str] = Query(default=None, alias="athleteName", description="Filter by athlete name"),
    metric_name: Optional[str] = Query(default=None, alias="metricName", description="Filter by metric name"),
    session_id: Optional[str] = Query(default=None, alias="sessionId", description="Filter by session ID"),
    date_from: Optional[str] = Query(default=None, alias="dateFrom", description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(default=None, alias="dateTo", description="Filter to date (YYYY-MM-DD)"),
) -> LegacyBodyCompositionListResponse:
    """
    List freestyle body composition data with session dates automatically resolved.
    
    The session date is resolved by joining with the session_time table using session_id.
    Both Gregorian (miladiDate) and Persian (shamsiDate) dates are included in the response.
    
    Args:
        db: Database session.
        current_user: Authenticated user.
        page: Page number (1-indexed).
        per_page: Number of items per page (max 100).
        athlete_name: Optional filter by athlete name (partial match).
        metric_name: Optional filter by metric name (partial match).
        session_id: Optional filter by exact session ID.
        date_from: Optional filter by start date (YYYY-MM-DD).
        date_to: Optional filter by end date (YYYY-MM-DD).
        
    Returns:
        LegacyBodyCompositionListResponse: List of measurements with dates and pagination.
    """
    data, total = await get_body_composition_fs_with_dates(
        db, page, per_page, athlete_name, metric_name, session_id, date_from, date_to
    )
    
    responses = [
        LegacyBodyCompositionResponse(
            id=d["id"],
            sessionId=d["session_id"],
            athleteName=d["athlete_name"],
            metricName=d["metric_name"],
            nvalue=d["nvalue"],
            tvalue=d["tvalue"],
            sessionDate=d["session_date"],
            sessionDateShamsi=d["session_date_shamsi"],
        )
        for d in data
    ]
    
    return LegacyBodyCompositionListResponse(
        data=responses,
        pagination=calculate_pagination(total, page, per_page),
        style="freestyle",
    )


@router.get(
    "/body-composition/greco-roman",
    response_model=LegacyBodyCompositionListResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
    summary="List Body Composition (Greco-Roman)",
    description="Get greco-roman body composition measurements with session dates resolved.",
)
async def list_body_composition_greco_roman(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=50, ge=1, le=100, alias="perPage", description="Items per page"),
    athlete_name: Optional[str] = Query(default=None, alias="athleteName", description="Filter by athlete name"),
    metric_name: Optional[str] = Query(default=None, alias="metricName", description="Filter by metric name"),
    session_id: Optional[str] = Query(default=None, alias="sessionId", description="Filter by session ID"),
    date_from: Optional[str] = Query(default=None, alias="dateFrom", description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(default=None, alias="dateTo", description="Filter to date (YYYY-MM-DD)"),
) -> LegacyBodyCompositionListResponse:
    """
    List greco-roman body composition data with session dates automatically resolved.
    
    The session date is resolved by joining with the session_time table using session_id.
    Both Gregorian (miladiDate) and Persian (shamsiDate) dates are included in the response.
    """
    data, total = await get_body_composition_gr_with_dates(
        db, page, per_page, athlete_name, metric_name, session_id, date_from, date_to
    )
    
    responses = [
        LegacyBodyCompositionResponse(
            id=d["id"],
            sessionId=d["session_id"],
            athleteName=d["athlete_name"],
            metricName=d["metric_name"],
            nvalue=d["nvalue"],
            tvalue=d["tvalue"],
            sessionDate=d["session_date"],
            sessionDateShamsi=d["session_date_shamsi"],
        )
        for d in data
    ]
    
    return LegacyBodyCompositionListResponse(
        data=responses,
        pagination=calculate_pagination(total, page, per_page),
        style="greco-roman",
    )


# ============================================================================
# Chestbelt Heart Rate Endpoints
# ============================================================================


@router.get(
    "/chestbelt-hr",
    response_model=LegacyChestbeltHRListResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
    summary="List Chestbelt Heart Rate Data",
    description="Get chestbelt heart rate measurements with session dates resolved.",
)
async def list_chestbelt_hr(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=50, ge=1, le=100, alias="perPage", description="Items per page"),
    athlete_name: Optional[str] = Query(default=None, alias="athleteName", description="Filter by athlete name"),
    metric_name: Optional[str] = Query(default=None, alias="metricName", description="Filter by metric name"),
    session_id: Optional[str] = Query(default=None, alias="sessionId", description="Filter by session ID"),
    date_from: Optional[str] = Query(default=None, alias="dateFrom", description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(default=None, alias="dateTo", description="Filter to date (YYYY-MM-DD)"),
) -> LegacyChestbeltHRListResponse:
    """
    List chestbelt heart rate data with session dates automatically resolved.
    
    The session date is resolved by joining with the session_time table using session_id.
    """
    data, total = await get_chestbelt_hr_gr_with_dates(
        db, page, per_page, athlete_name, metric_name, session_id, date_from, date_to
    )
    
    responses = [
        LegacyChestbeltHRResponse(
            id=d["id"],
            sessionId=d["session_id"],
            athleteName=d["athlete_name"],
            metricName=d["metric_name"],
            nvalue=d["nvalue"],
            tvalue=d["tvalue"],
            sessionDate=d["session_date"],
            sessionDateShamsi=d["session_date_shamsi"],
        )
        for d in data
    ]
    
    return LegacyChestbeltHRListResponse(
        data=responses,
        pagination=calculate_pagination(total, page, per_page),
    )


# ============================================================================
# Fitness Endpoints
# ============================================================================


@router.get(
    "/fitness",
    response_model=LegacyFitnessListResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
    summary="List Fitness Data",
    description="Get fitness measurements with session dates resolved.",
)
async def list_fitness(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=50, ge=1, le=100, alias="perPage", description="Items per page"),
    athlete_name: Optional[str] = Query(default=None, alias="athleteName", description="Filter by athlete name"),
    metric_name: Optional[str] = Query(default=None, alias="metricName", description="Filter by metric name"),
    session_id: Optional[str] = Query(default=None, alias="sessionId", description="Filter by session ID"),
    date_from: Optional[str] = Query(default=None, alias="dateFrom", description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(default=None, alias="dateTo", description="Filter to date (YYYY-MM-DD)"),
) -> LegacyFitnessListResponse:
    """
    List fitness data with session dates automatically resolved.
    
    The session date is resolved by joining with the session_time table using session_id.
    """
    data, total = await get_fitness_fs_with_dates(
        db, page, per_page, athlete_name, metric_name, session_id, date_from, date_to
    )
    
    responses = [
        LegacyFitnessResponse(
            id=d["id"],
            sessionId=d["session_id"],
            athleteName=d["athlete_name"],
            metricName=d["metric_name"],
            metricMethod=d["metric_method"],
            value=d["value"],
            sessionDate=d["session_date"],
            sessionDateShamsi=d["session_date_shamsi"],
        )
        for d in data
    ]
    
    return LegacyFitnessListResponse(
        data=responses,
        pagination=calculate_pagination(total, page, per_page),
    )


# ============================================================================
# Urion Analysis Endpoints
# ============================================================================


@router.get(
    "/urion-analysis",
    response_model=LegacyUrionAnalysisListResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
    },
    summary="List Urion Analysis Data",
    description="Get urion analysis measurements with session dates resolved.",
)
async def list_urion_analysis(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(default=1, ge=1, description="Page number"),
    per_page: int = Query(default=50, ge=1, le=100, alias="perPage", description="Items per page"),
    athlete_name: Optional[str] = Query(default=None, alias="athleteName", description="Filter by athlete name"),
    metric_name: Optional[str] = Query(default=None, alias="metricName", description="Filter by metric name"),
    session_id: Optional[str] = Query(default=None, alias="sessionId", description="Filter by session ID"),
    date_from: Optional[str] = Query(default=None, alias="dateFrom", description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(default=None, alias="dateTo", description="Filter to date (YYYY-MM-DD)"),
) -> LegacyUrionAnalysisListResponse:
    """
    List urion analysis data with session dates automatically resolved.
    
    The session date is resolved by joining with the session_time table using session_id.
    """
    data, total = await get_urion_analysis_gr_with_dates(
        db, page, per_page, athlete_name, metric_name, session_id, date_from, date_to
    )
    
    responses = [
        LegacyUrionAnalysisResponse(
            id=d["id"],
            sessionId=d["session_id"],
            athleteName=d["athlete_name"],
            metricName=d["metric_name"],
            metricMethod=d["metric_method"],
            value=d["value"],
            sessionDate=d["session_date"],
            sessionDateShamsi=d["session_date_shamsi"],
        )
        for d in data
    ]
    
    return LegacyUrionAnalysisListResponse(
        data=responses,
        pagination=calculate_pagination(total, page, per_page),
    )
