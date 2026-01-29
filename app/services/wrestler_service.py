"""
Wrestler service for wrestler data management.

This module provides functions for:
- Wrestler listing and retrieval
- Wrestler metrics aggregation
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import (
    Wrestler,
    Team,
    OverviewMetrics,
    BodyCompositionMetrics,
    BloodworkMetrics,
    RecoveryMetrics,
    SupplementsMetrics,
    PerformanceMetrics,
    SectionScore,
)


async def get_wrestlers(
    db: AsyncSession,
    team_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> List[Wrestler]:
    """
    Get list of wrestlers with optional team filtering.
    
    Args:
        db: Database session.
        team_id: Optional team ID to filter by.
        limit: Maximum number of results.
        offset: Number of results to skip.
        
    Returns:
        List[Wrestler]: List of wrestlers.
    """
    query = select(Wrestler).offset(offset).limit(limit)
    
    if team_id:
        query = query.where(Wrestler.team_id == team_id)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_wrestler_by_id(
    db: AsyncSession, wrestler_id: str
) -> Optional[Wrestler]:
    """
    Get a wrestler by ID.
    
    Args:
        db: Database session.
        wrestler_id: The wrestler ID.
        
    Returns:
        Optional[Wrestler]: The wrestler or None if not found.
    """
    result = await db.execute(
        select(Wrestler).where(Wrestler.id == wrestler_id)
    )
    return result.scalar_one_or_none()


async def get_latest_overview_metrics(
    db: AsyncSession, wrestler_id: str
) -> Optional[OverviewMetrics]:
    """
    Get the latest overview metrics for a wrestler.
    
    Args:
        db: Database session.
        wrestler_id: The wrestler ID.
        
    Returns:
        Optional[OverviewMetrics]: Latest metrics or None.
    """
    result = await db.execute(
        select(OverviewMetrics)
        .where(OverviewMetrics.wrestler_id == wrestler_id)
        .order_by(OverviewMetrics.recorded_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_latest_body_composition_metrics(
    db: AsyncSession, wrestler_id: str
) -> Optional[BodyCompositionMetrics]:
    """
    Get the latest body composition metrics for a wrestler.
    
    Args:
        db: Database session.
        wrestler_id: The wrestler ID.
        
    Returns:
        Optional[BodyCompositionMetrics]: Latest metrics or None.
    """
    result = await db.execute(
        select(BodyCompositionMetrics)
        .where(BodyCompositionMetrics.wrestler_id == wrestler_id)
        .order_by(BodyCompositionMetrics.recorded_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_latest_bloodwork_metrics(
    db: AsyncSession, wrestler_id: str
) -> Optional[BloodworkMetrics]:
    """
    Get the latest bloodwork metrics for a wrestler.
    
    Args:
        db: Database session.
        wrestler_id: The wrestler ID.
        
    Returns:
        Optional[BloodworkMetrics]: Latest metrics or None.
    """
    result = await db.execute(
        select(BloodworkMetrics)
        .where(BloodworkMetrics.wrestler_id == wrestler_id)
        .order_by(BloodworkMetrics.recorded_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_latest_recovery_metrics(
    db: AsyncSession, wrestler_id: str
) -> Optional[RecoveryMetrics]:
    """
    Get the latest recovery metrics for a wrestler.
    
    Args:
        db: Database session.
        wrestler_id: The wrestler ID.
        
    Returns:
        Optional[RecoveryMetrics]: Latest metrics or None.
    """
    result = await db.execute(
        select(RecoveryMetrics)
        .where(RecoveryMetrics.wrestler_id == wrestler_id)
        .order_by(RecoveryMetrics.recorded_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_latest_supplements_metrics(
    db: AsyncSession, wrestler_id: str
) -> Optional[SupplementsMetrics]:
    """
    Get the latest supplements metrics for a wrestler.
    
    Args:
        db: Database session.
        wrestler_id: The wrestler ID.
        
    Returns:
        Optional[SupplementsMetrics]: Latest metrics or None.
    """
    result = await db.execute(
        select(SupplementsMetrics)
        .where(SupplementsMetrics.wrestler_id == wrestler_id)
        .order_by(SupplementsMetrics.recorded_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_latest_performance_metrics(
    db: AsyncSession, wrestler_id: str
) -> Optional[PerformanceMetrics]:
    """
    Get the latest performance metrics for a wrestler.
    
    Args:
        db: Database session.
        wrestler_id: The wrestler ID.
        
    Returns:
        Optional[PerformanceMetrics]: Latest metrics or None.
    """
    result = await db.execute(
        select(PerformanceMetrics)
        .where(PerformanceMetrics.wrestler_id == wrestler_id)
        .order_by(PerformanceMetrics.recorded_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def get_latest_section_score(
    db: AsyncSession, wrestler_id: str, section_key: str
) -> Optional[SectionScore]:
    """
    Get the latest section score for a wrestler.
    
    Args:
        db: Database session.
        wrestler_id: The wrestler ID.
        section_key: The section key (e.g., 'overview', 'body_composition').
        
    Returns:
        Optional[SectionScore]: Latest score or None.
    """
    result = await db.execute(
        select(SectionScore)
        .where(
            SectionScore.wrestler_id == wrestler_id,
            SectionScore.section_key == section_key,
        )
        .order_by(SectionScore.recorded_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()
