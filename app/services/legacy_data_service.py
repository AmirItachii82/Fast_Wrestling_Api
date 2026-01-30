"""
Legacy data service for Fittechno database.

This service provides query methods for accessing legacy measurement data
with session date resolution via JOIN with session_time table.
"""

from typing import List, Optional, Tuple

from sqlalchemy import func, select, and_, cast, BigInteger
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    LegacyAthlete,
    SessionTime,
    LegacyMetric,
    BodyCompositionFS,
    BodyCompositionGR,
    ChestbeltHRGR,
    FitnessFS,
    UrionAnalysisGR,
)


async def get_legacy_athletes(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 50,
    athlete_name: Optional[str] = None,
) -> Tuple[List[LegacyAthlete], int]:
    """
    Get list of legacy athletes with pagination and optional filtering.
    
    Args:
        db: Database session.
        page: Page number (1-indexed).
        per_page: Number of items per page.
        athlete_name: Optional filter by athlete name (partial match).
        
    Returns:
        Tuple of (list of athletes, total count).
    """
    query = select(LegacyAthlete)
    count_query = select(func.count(LegacyAthlete.id))
    
    if athlete_name:
        query = query.where(LegacyAthlete.athlete_name.ilike(f"%{athlete_name}%"))
        count_query = count_query.where(LegacyAthlete.athlete_name.ilike(f"%{athlete_name}%"))
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Get paginated results
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page).order_by(LegacyAthlete.id)
    
    result = await db.execute(query)
    athletes = result.scalars().all()
    
    return list(athletes), total


async def get_session_times(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 50,
    athlete_name: Optional[str] = None,
    test_category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> Tuple[List[SessionTime], int]:
    """
    Get list of session times with pagination and optional filtering.
    
    Args:
        db: Database session.
        page: Page number (1-indexed).
        per_page: Number of items per page.
        athlete_name: Optional filter by athlete name.
        test_category: Optional filter by test category.
        date_from: Optional filter by start date (YYYY-MM-DD).
        date_to: Optional filter by end date (YYYY-MM-DD).
        
    Returns:
        Tuple of (list of sessions, total count).
    """
    query = select(SessionTime)
    count_query = select(func.count(SessionTime.session_id))
    
    conditions = []
    if athlete_name:
        conditions.append(SessionTime.athlete_name.ilike(f"%{athlete_name}%"))
    if test_category:
        conditions.append(SessionTime.test_category == test_category)
    if date_from:
        conditions.append(SessionTime.miladi_date >= date_from)
    if date_to:
        conditions.append(SessionTime.miladi_date <= date_to)
    
    if conditions:
        query = query.where(and_(*conditions))
        count_query = count_query.where(and_(*conditions))
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Get paginated results
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page).order_by(SessionTime.session_id.desc())
    
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    return list(sessions), total


async def get_legacy_metrics(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 50,
    category: Optional[str] = None,
) -> Tuple[List[LegacyMetric], int]:
    """
    Get list of metric definitions with pagination and optional filtering.
    
    Args:
        db: Database session.
        page: Page number (1-indexed).
        per_page: Number of items per page.
        category: Optional filter by category.
        
    Returns:
        Tuple of (list of metrics, total count).
    """
    query = select(LegacyMetric)
    count_query = select(func.count(LegacyMetric.id))
    
    if category:
        query = query.where(LegacyMetric.category == category)
        count_query = count_query.where(LegacyMetric.category == category)
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Get paginated results
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page).order_by(LegacyMetric.id)
    
    result = await db.execute(query)
    metrics = result.scalars().all()
    
    return list(metrics), total


async def get_body_composition_fs_with_dates(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 50,
    athlete_name: Optional[str] = None,
    metric_name: Optional[str] = None,
    session_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> Tuple[List[dict], int]:
    """
    Get body composition freestyle data with session dates resolved.
    
    Args:
        db: Database session.
        page: Page number (1-indexed).
        per_page: Number of items per page.
        athlete_name: Optional filter by athlete name.
        metric_name: Optional filter by metric name.
        session_id: Optional filter by session ID.
        date_from: Optional filter by start date.
        date_to: Optional filter by end date.
        
    Returns:
        Tuple of (list of measurements with dates, total count).
    """
    # Main query with LEFT JOIN to session_time
    query = (
        select(
            BodyCompositionFS.id,
            BodyCompositionFS.session_id,
            BodyCompositionFS.athlete_name,
            BodyCompositionFS.metric_name,
            BodyCompositionFS.nvalue,
            BodyCompositionFS.tvalue,
            SessionTime.miladi_date,
            SessionTime.shamsi_date,
        )
        .select_from(BodyCompositionFS)
        .outerjoin(
            SessionTime,
            cast(BodyCompositionFS.session_id, BigInteger) == SessionTime.session_id
        )
    )
    
    # Build conditions - track date conditions separately
    conditions = []
    date_conditions = []
    
    if athlete_name:
        conditions.append(BodyCompositionFS.athlete_name.ilike(f"%{athlete_name}%"))
    if metric_name:
        conditions.append(BodyCompositionFS.metric_name.ilike(f"%{metric_name}%"))
    if session_id:
        conditions.append(BodyCompositionFS.session_id == session_id)
    if date_from:
        date_conditions.append(SessionTime.miladi_date >= date_from)
    if date_to:
        date_conditions.append(SessionTime.miladi_date <= date_to)
    
    all_conditions = conditions + date_conditions
    
    if all_conditions:
        query = query.where(and_(*all_conditions))
    
    # Build count query - only needs join if date filters are used
    if date_conditions:
        count_query = (
            select(func.count(BodyCompositionFS.id))
            .select_from(BodyCompositionFS)
            .outerjoin(
                SessionTime,
                cast(BodyCompositionFS.session_id, BigInteger) == SessionTime.session_id
            )
            .where(and_(*all_conditions))
        )
    elif conditions:
        count_query = select(func.count(BodyCompositionFS.id)).where(and_(*conditions))
    else:
        count_query = select(func.count(BodyCompositionFS.id))
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Get paginated results
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page).order_by(BodyCompositionFS.id.desc())
    
    result = await db.execute(query)
    rows = result.all()
    
    # Convert to dict format
    data = []
    for row in rows:
        data.append({
            "id": row.id,
            "session_id": row.session_id,
            "athlete_name": row.athlete_name,
            "metric_name": row.metric_name,
            "nvalue": row.nvalue,
            "tvalue": row.tvalue,
            "session_date": row.miladi_date,
            "session_date_shamsi": row.shamsi_date,
        })
    
    return data, total


async def get_body_composition_gr_with_dates(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 50,
    athlete_name: Optional[str] = None,
    metric_name: Optional[str] = None,
    session_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> Tuple[List[dict], int]:
    """
    Get body composition greco-roman data with session dates resolved.
    
    Args:
        db: Database session.
        page: Page number (1-indexed).
        per_page: Number of items per page.
        athlete_name: Optional filter by athlete name.
        metric_name: Optional filter by metric name.
        session_id: Optional filter by session ID.
        date_from: Optional filter by start date.
        date_to: Optional filter by end date.
        
    Returns:
        Tuple of (list of measurements with dates, total count).
    """
    query = (
        select(
            BodyCompositionGR.id,
            BodyCompositionGR.session_id,
            BodyCompositionGR.athlete_name,
            BodyCompositionGR.metric_name,
            BodyCompositionGR.nvalue,
            BodyCompositionGR.tvalue,
            SessionTime.miladi_date,
            SessionTime.shamsi_date,
        )
        .select_from(BodyCompositionGR)
        .outerjoin(
            SessionTime,
            cast(BodyCompositionGR.session_id, BigInteger) == SessionTime.session_id
        )
    )
    
    # Build conditions - track date conditions separately
    conditions = []
    date_conditions = []
    
    if athlete_name:
        conditions.append(BodyCompositionGR.athlete_name.ilike(f"%{athlete_name}%"))
    if metric_name:
        conditions.append(BodyCompositionGR.metric_name.ilike(f"%{metric_name}%"))
    if session_id:
        conditions.append(BodyCompositionGR.session_id == session_id)
    if date_from:
        date_conditions.append(SessionTime.miladi_date >= date_from)
    if date_to:
        date_conditions.append(SessionTime.miladi_date <= date_to)
    
    all_conditions = conditions + date_conditions
    
    if all_conditions:
        query = query.where(and_(*all_conditions))
    
    # Build count query - only needs join if date filters are used
    if date_conditions:
        count_query = (
            select(func.count(BodyCompositionGR.id))
            .select_from(BodyCompositionGR)
            .outerjoin(
                SessionTime,
                cast(BodyCompositionGR.session_id, BigInteger) == SessionTime.session_id
            )
            .where(and_(*all_conditions))
        )
    elif conditions:
        count_query = select(func.count(BodyCompositionGR.id)).where(and_(*conditions))
    else:
        count_query = select(func.count(BodyCompositionGR.id))
    
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page).order_by(BodyCompositionGR.id.desc())
    
    result = await db.execute(query)
    rows = result.all()
    
    data = []
    for row in rows:
        data.append({
            "id": row.id,
            "session_id": row.session_id,
            "athlete_name": row.athlete_name,
            "metric_name": row.metric_name,
            "nvalue": row.nvalue,
            "tvalue": row.tvalue,
            "session_date": row.miladi_date,
            "session_date_shamsi": row.shamsi_date,
        })
    
    return data, total


async def get_chestbelt_hr_gr_with_dates(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 50,
    athlete_name: Optional[str] = None,
    metric_name: Optional[str] = None,
    session_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> Tuple[List[dict], int]:
    """
    Get chestbelt heart rate data with session dates resolved.
    
    Args:
        db: Database session.
        page: Page number (1-indexed).
        per_page: Number of items per page.
        athlete_name: Optional filter by athlete name.
        metric_name: Optional filter by metric name.
        session_id: Optional filter by session ID.
        date_from: Optional filter by start date (YYYY-MM-DD).
        date_to: Optional filter by end date (YYYY-MM-DD).
        
    Returns:
        Tuple of (list of measurements with dates, total count).
    """
    query = (
        select(
            ChestbeltHRGR.id,
            ChestbeltHRGR.session_id,
            ChestbeltHRGR.athlete_name,
            ChestbeltHRGR.metric_name,
            ChestbeltHRGR.nvalue,
            ChestbeltHRGR.tvalue,
            SessionTime.miladi_date,
            SessionTime.shamsi_date,
        )
        .select_from(ChestbeltHRGR)
        .outerjoin(
            SessionTime,
            cast(ChestbeltHRGR.session_id, BigInteger) == SessionTime.session_id
        )
    )
    
    # Build conditions - track date conditions separately
    conditions = []
    date_conditions = []
    
    if athlete_name:
        conditions.append(ChestbeltHRGR.athlete_name.ilike(f"%{athlete_name}%"))
    if metric_name:
        conditions.append(ChestbeltHRGR.metric_name.ilike(f"%{metric_name}%"))
    if session_id:
        conditions.append(ChestbeltHRGR.session_id == session_id)
    if date_from:
        date_conditions.append(SessionTime.miladi_date >= date_from)
    if date_to:
        date_conditions.append(SessionTime.miladi_date <= date_to)
    
    all_conditions = conditions + date_conditions
    
    if all_conditions:
        query = query.where(and_(*all_conditions))
    
    # Build count query - only needs join if date filters are used
    if date_conditions:
        count_query = (
            select(func.count(ChestbeltHRGR.id))
            .select_from(ChestbeltHRGR)
            .outerjoin(
                SessionTime,
                cast(ChestbeltHRGR.session_id, BigInteger) == SessionTime.session_id
            )
            .where(and_(*all_conditions))
        )
    elif conditions:
        count_query = select(func.count(ChestbeltHRGR.id)).where(and_(*conditions))
    else:
        count_query = select(func.count(ChestbeltHRGR.id))
    
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page).order_by(ChestbeltHRGR.id.desc())
    
    result = await db.execute(query)
    rows = result.all()
    
    data = []
    for row in rows:
        data.append({
            "id": row.id,
            "session_id": row.session_id,
            "athlete_name": row.athlete_name,
            "metric_name": row.metric_name,
            "nvalue": row.nvalue,
            "tvalue": row.tvalue,
            "session_date": row.miladi_date,
            "session_date_shamsi": row.shamsi_date,
        })
    
    return data, total


async def get_fitness_fs_with_dates(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 50,
    athlete_name: Optional[str] = None,
    metric_name: Optional[str] = None,
    session_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> Tuple[List[dict], int]:
    """
    Get fitness freestyle data with session dates resolved.
    
    Args:
        db: Database session.
        page: Page number (1-indexed).
        per_page: Number of items per page.
        athlete_name: Optional filter by athlete name.
        metric_name: Optional filter by metric name.
        session_id: Optional filter by session ID.
        date_from: Optional filter by start date (YYYY-MM-DD).
        date_to: Optional filter by end date (YYYY-MM-DD).
        
    Returns:
        Tuple of (list of measurements with dates, total count).
    """
    query = (
        select(
            FitnessFS.id,
            FitnessFS.session_id,
            FitnessFS.athlete_name,
            FitnessFS.metric_name,
            FitnessFS.metric_method,
            FitnessFS.value,
            SessionTime.miladi_date,
            SessionTime.shamsi_date,
        )
        .select_from(FitnessFS)
        .outerjoin(
            SessionTime,
            cast(FitnessFS.session_id, BigInteger) == SessionTime.session_id
        )
    )
    
    # Build conditions - track date conditions separately
    conditions = []
    date_conditions = []
    
    if athlete_name:
        conditions.append(FitnessFS.athlete_name.ilike(f"%{athlete_name}%"))
    if metric_name:
        conditions.append(FitnessFS.metric_name.ilike(f"%{metric_name}%"))
    if session_id:
        conditions.append(FitnessFS.session_id == session_id)
    if date_from:
        date_conditions.append(SessionTime.miladi_date >= date_from)
    if date_to:
        date_conditions.append(SessionTime.miladi_date <= date_to)
    
    all_conditions = conditions + date_conditions
    
    if all_conditions:
        query = query.where(and_(*all_conditions))
    
    # Build count query - only needs join if date filters are used
    if date_conditions:
        count_query = (
            select(func.count(FitnessFS.id))
            .select_from(FitnessFS)
            .outerjoin(
                SessionTime,
                cast(FitnessFS.session_id, BigInteger) == SessionTime.session_id
            )
            .where(and_(*all_conditions))
        )
    elif conditions:
        count_query = select(func.count(FitnessFS.id)).where(and_(*conditions))
    else:
        count_query = select(func.count(FitnessFS.id))
    
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page).order_by(FitnessFS.id.desc())
    
    result = await db.execute(query)
    rows = result.all()
    
    data = []
    for row in rows:
        data.append({
            "id": row.id,
            "session_id": row.session_id,
            "athlete_name": row.athlete_name,
            "metric_name": row.metric_name,
            "metric_method": row.metric_method,
            "value": row.value,
            "session_date": row.miladi_date,
            "session_date_shamsi": row.shamsi_date,
        })
    
    return data, total


async def get_urion_analysis_gr_with_dates(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 50,
    athlete_name: Optional[str] = None,
    metric_name: Optional[str] = None,
    session_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> Tuple[List[dict], int]:
    """
    Get urion analysis data with session dates resolved.
    
    Args:
        db: Database session.
        page: Page number (1-indexed).
        per_page: Number of items per page.
        athlete_name: Optional filter by athlete name.
        metric_name: Optional filter by metric name.
        session_id: Optional filter by session ID.
        date_from: Optional filter by start date (YYYY-MM-DD).
        date_to: Optional filter by end date (YYYY-MM-DD).
        
    Returns:
        Tuple of (list of measurements with dates, total count).
    """
    query = (
        select(
            UrionAnalysisGR.id,
            UrionAnalysisGR.session_id,
            UrionAnalysisGR.athlete_name,
            UrionAnalysisGR.metric_name,
            UrionAnalysisGR.metric_method,
            UrionAnalysisGR.value,
            SessionTime.miladi_date,
            SessionTime.shamsi_date,
        )
        .select_from(UrionAnalysisGR)
        .outerjoin(
            SessionTime,
            cast(UrionAnalysisGR.session_id, BigInteger) == SessionTime.session_id
        )
    )
    
    # Build conditions - track date conditions separately
    conditions = []
    date_conditions = []
    
    if athlete_name:
        conditions.append(UrionAnalysisGR.athlete_name.ilike(f"%{athlete_name}%"))
    if metric_name:
        conditions.append(UrionAnalysisGR.metric_name.ilike(f"%{metric_name}%"))
    if session_id:
        conditions.append(UrionAnalysisGR.session_id == session_id)
    if date_from:
        date_conditions.append(SessionTime.miladi_date >= date_from)
    if date_to:
        date_conditions.append(SessionTime.miladi_date <= date_to)
    
    all_conditions = conditions + date_conditions
    
    if all_conditions:
        query = query.where(and_(*all_conditions))
    
    # Build count query - only needs join if date filters are used
    if date_conditions:
        count_query = (
            select(func.count(UrionAnalysisGR.id))
            .select_from(UrionAnalysisGR)
            .outerjoin(
                SessionTime,
                cast(UrionAnalysisGR.session_id, BigInteger) == SessionTime.session_id
            )
            .where(and_(*all_conditions))
        )
    elif conditions:
        count_query = select(func.count(UrionAnalysisGR.id)).where(and_(*conditions))
    else:
        count_query = select(func.count(UrionAnalysisGR.id))
    
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page).order_by(UrionAnalysisGR.id.desc())
    
    result = await db.execute(query)
    rows = result.all()
    
    data = []
    for row in rows:
        data.append({
            "id": row.id,
            "session_id": row.session_id,
            "athlete_name": row.athlete_name,
            "metric_name": row.metric_name,
            "metric_method": row.metric_method,
            "value": row.value,
            "session_date": row.miladi_date,
            "session_date_shamsi": row.shamsi_date,
        })
    
    return data, total
