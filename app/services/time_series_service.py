"""
Time series service for handling trend data.

This module provides functions for fetching time series data
for various metrics and sections.
"""

from typing import List, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    OverviewSeries,
    BodyCompositionSeries,
    BloodworkSeries,
    RecoverySeries,
    SupplementsSeries,
    PerformanceSeries,
)


async def get_body_composition_series(
    db: AsyncSession,
    wrestler_id: str,
    metric_name: str,
    limit: int = 30,
) -> List[Tuple[str, float]]:
    """
    Get body composition time series data.
    
    Args:
        db: Database session.
        wrestler_id: The wrestler ID.
        metric_name: Name of the metric.
        limit: Maximum number of points.
        
    Returns:
        List of (date, value) tuples.
    """
    result = await db.execute(
        select(BodyCompositionSeries)
        .where(
            BodyCompositionSeries.wrestler_id == wrestler_id,
            BodyCompositionSeries.metric_name == metric_name,
        )
        .order_by(BodyCompositionSeries.recorded_at.desc())
        .limit(limit)
    )
    rows = result.scalars().all()
    
    # Return in chronological order
    return [
        (row.recorded_at.strftime("%Y-%m-%d"), row.value)
        for row in reversed(rows)
    ]


async def get_bloodwork_series(
    db: AsyncSession,
    wrestler_id: str,
    panel: str,
    metric_name: str,
    limit: int = 30,
) -> List[Tuple[str, float]]:
    """
    Get bloodwork time series data.
    
    Args:
        db: Database session.
        wrestler_id: The wrestler ID.
        panel: Panel name (cbc, lipids).
        metric_name: Name of the metric.
        limit: Maximum number of points.
        
    Returns:
        List of (date, value) tuples.
    """
    result = await db.execute(
        select(BloodworkSeries)
        .where(
            BloodworkSeries.wrestler_id == wrestler_id,
            BloodworkSeries.panel == panel,
            BloodworkSeries.metric_name == metric_name,
        )
        .order_by(BloodworkSeries.recorded_at.desc())
        .limit(limit)
    )
    rows = result.scalars().all()
    
    return [
        (row.recorded_at.strftime("%Y-%m-%d"), row.value)
        for row in reversed(rows)
    ]


async def get_recovery_series(
    db: AsyncSession,
    wrestler_id: str,
    metric_name: str,
    limit: int = 30,
) -> List[Tuple[str, float]]:
    """
    Get recovery time series data.
    
    Args:
        db: Database session.
        wrestler_id: The wrestler ID.
        metric_name: Name of the metric.
        limit: Maximum number of points.
        
    Returns:
        List of (date, value) tuples.
    """
    result = await db.execute(
        select(RecoverySeries)
        .where(
            RecoverySeries.wrestler_id == wrestler_id,
            RecoverySeries.metric_name == metric_name,
        )
        .order_by(RecoverySeries.recorded_at.desc())
        .limit(limit)
    )
    rows = result.scalars().all()
    
    return [
        (row.recorded_at.strftime("%Y-%m-%d"), row.value)
        for row in reversed(rows)
    ]


async def get_supplements_series(
    db: AsyncSession,
    wrestler_id: str,
    metric_name: str,
    limit: int = 30,
) -> List[Tuple[str, float]]:
    """
    Get supplements time series data.
    
    Args:
        db: Database session.
        wrestler_id: The wrestler ID.
        metric_name: Name of the metric.
        limit: Maximum number of points.
        
    Returns:
        List of (date, value) tuples.
    """
    result = await db.execute(
        select(SupplementsSeries)
        .where(
            SupplementsSeries.wrestler_id == wrestler_id,
            SupplementsSeries.metric_name == metric_name,
        )
        .order_by(SupplementsSeries.recorded_at.desc())
        .limit(limit)
    )
    rows = result.scalars().all()
    
    return [
        (row.recorded_at.strftime("%Y-%m-%d"), row.value)
        for row in reversed(rows)
    ]


async def get_performance_series(
    db: AsyncSession,
    wrestler_id: str,
    metric_name: str,
    limit: int = 30,
) -> List[Tuple[str, float]]:
    """
    Get performance time series data.
    
    Args:
        db: Database session.
        wrestler_id: The wrestler ID.
        metric_name: Name of the metric.
        limit: Maximum number of points.
        
    Returns:
        List of (date, value) tuples.
    """
    result = await db.execute(
        select(PerformanceSeries)
        .where(
            PerformanceSeries.wrestler_id == wrestler_id,
            PerformanceSeries.metric_name == metric_name,
        )
        .order_by(PerformanceSeries.recorded_at.desc())
        .limit(limit)
    )
    rows = result.scalars().all()
    
    return [
        (row.recorded_at.strftime("%Y-%m-%d"), row.value)
        for row in reversed(rows)
    ]


async def get_overview_series(
    db: AsyncSession,
    wrestler_id: str,
    limit: int = 30,
) -> List[Tuple[str, float]]:
    """
    Get overview radar chart data (latest values per label).
    
    Args:
        db: Database session.
        wrestler_id: The wrestler ID.
        limit: Maximum number of labels.
        
    Returns:
        List of (label, value) tuples.
    """
    # Get the latest recorded date
    result = await db.execute(
        select(OverviewSeries)
        .where(OverviewSeries.wrestler_id == wrestler_id)
        .order_by(OverviewSeries.recorded_at.desc())
        .limit(1)
    )
    latest = result.scalar_one_or_none()
    
    if not latest:
        return []
    
    # Get all values for that date
    result = await db.execute(
        select(OverviewSeries)
        .where(
            OverviewSeries.wrestler_id == wrestler_id,
            OverviewSeries.recorded_at == latest.recorded_at,
        )
        .limit(limit)
    )
    rows = result.scalars().all()
    
    return [(row.label, row.value) for row in rows]
