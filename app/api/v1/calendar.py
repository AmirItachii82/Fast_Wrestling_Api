"""
Calendar endpoints.

Provides:
- GET /wrestlers/{wrestlerId}/calendar - Monthly programs
"""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import User, TrainingProgram, TrainingProgramBlock, TrainingProgramAIRecommendation
from app.schemas import (
    CalendarResponse,
    ErrorResponse,
)
from app.schemas.api import CalendarProgram, ProgramBlock
from app.utils.dependencies import get_current_user, validate_wrestler_access

router = APIRouter()


@router.get(
    "/{wrestler_id}/calendar",
    response_model=CalendarResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def get_calendar(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    month: int = Query(default=None, ge=1, le=12),
    year: int = Query(default=None, ge=2020, le=2100),
) -> CalendarResponse:
    """
    Get monthly training programs for calendar view.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user.
        month: Month number (1-12). Defaults to current month.
        year: Year. Defaults to current year.
        
    Returns:
        CalendarResponse: List of programs for the month.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    # Default to current month/year
    today = date.today()
    if month is None:
        month = today.month
    if year is None:
        year = today.year
    
    # Calculate date range for the month
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)
    
    # Get programs for the month
    result = await db.execute(
        select(TrainingProgram)
        .where(
            TrainingProgram.wrestler_id == wrestler_id,
            TrainingProgram.date >= start_date,
            TrainingProgram.date < end_date,
        )
        .order_by(TrainingProgram.date)
    )
    programs = result.scalars().all()
    
    calendar_programs = []
    for program in programs:
        # Get blocks
        result = await db.execute(
            select(TrainingProgramBlock)
            .where(TrainingProgramBlock.program_id == program.id)
        )
        blocks = result.scalars().all()
        
        # Get AI recommendations
        result = await db.execute(
            select(TrainingProgramAIRecommendation)
            .where(TrainingProgramAIRecommendation.program_id == program.id)
        )
        ai_recs = result.scalars().all()
        
        calendar_programs.append(CalendarProgram(
            date=program.date.strftime("%Y-%m-%d"),
            title=program.title,
            focus=program.focus,
            blocks=[
                ProgramBlock(name=b.name, sets=b.sets, reps=b.reps)
                for b in blocks
            ],
            nutrition=program.nutrition,
            recovery=program.recovery,
            aiRecommendations=[r.recommendation for r in ai_recs],
        ))
    
    return CalendarResponse(programs=calendar_programs)
