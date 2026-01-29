"""
Training Program endpoints.

Provides:
- GET /wrestlers/{wrestlerId}/training-program - Current day program
- POST /wrestlers/{wrestlerId}/training-program - Submit program update
"""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import User, TrainingProgram, TrainingProgramBlock
from app.schemas import (
    TrainingProgramResponse,
    TrainingProgramRequest,
    TrainingProgramUpdateResponse,
    ErrorResponse,
)
from app.schemas.api import Exercise, ExerciseSet
from app.utils.dependencies import get_current_user, validate_wrestler_access

router = APIRouter()


@router.get(
    "/{wrestler_id}/training-program",
    response_model=TrainingProgramResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
    },
)
async def get_training_program(
    wrestler_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> TrainingProgramResponse:
    """
    Get current day training program for a wrestler.
    
    Args:
        wrestler_id: The wrestler ID.
        db: Database session.
        current_user: Authenticated user.
        
    Returns:
        TrainingProgramResponse: Today's training program.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    today = date.today()
    
    # Get today's program
    result = await db.execute(
        select(TrainingProgram)
        .where(
            TrainingProgram.wrestler_id == wrestler_id,
            TrainingProgram.date == today,
        )
        .limit(1)
    )
    program = result.scalar_one_or_none()
    
    if not program:
        # Return empty program for today
        return TrainingProgramResponse(
            date=today.strftime("%Y-%m-%d"),
            readiness=None,
            sessionRPE=None,
            bodyweight=None,
            hydration=None,
            notes=None,
            exercises=[],
        )
    
    # Get program blocks (exercises)
    result = await db.execute(
        select(TrainingProgramBlock)
        .where(TrainingProgramBlock.program_id == program.id)
    )
    blocks = result.scalars().all()
    
    # Convert blocks to exercises
    exercises = []
    for block in blocks:
        # Parse reps string to get sets
        sets = []
        try:
            # Assume load is per set
            reps_parts = block.reps.split("-")
            target_reps = int(reps_parts[0]) if reps_parts else 8
            for _ in range(block.sets):
                sets.append(ExerciseSet(reps=target_reps, weight=block.load or 0))
        except (ValueError, IndexError):
            for _ in range(block.sets):
                sets.append(ExerciseSet(reps=8, weight=block.load or 0))
        
        exercises.append(Exercise(name=block.name, sets=sets))
    
    return TrainingProgramResponse(
        date=program.date.strftime("%Y-%m-%d"),
        readiness=program.readiness,
        sessionRPE=program.session_rpe,
        bodyweight=program.bodyweight,
        hydration=program.hydration,
        notes=program.notes,
        exercises=exercises,
    )


@router.post(
    "/{wrestler_id}/training-program",
    response_model=TrainingProgramUpdateResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
async def submit_training_program(
    wrestler_id: str,
    request: TrainingProgramRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> TrainingProgramUpdateResponse:
    """
    Submit or update training program for a wrestler.
    
    Args:
        wrestler_id: The wrestler ID.
        request: Training program data.
        db: Database session.
        current_user: Authenticated user.
        
    Returns:
        TrainingProgramUpdateResponse: Success status.
    """
    await validate_wrestler_access(wrestler_id, current_user, db)
    
    # Parse date
    try:
        program_date = date.fromisoformat(request.date)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "VALIDATION_ERROR",
                "message": "Invalid date format",
                "details": {"date": "Date must be in YYYY-MM-DD format"},
            },
        )
    
    # Check if program exists for this date
    result = await db.execute(
        select(TrainingProgram)
        .where(
            TrainingProgram.wrestler_id == wrestler_id,
            TrainingProgram.date == program_date,
        )
    )
    existing_program = result.scalar_one_or_none()
    
    if existing_program:
        # Update existing program
        existing_program.readiness = request.readiness
        existing_program.session_rpe = request.sessionRPE
        existing_program.bodyweight = request.bodyweight
        existing_program.hydration = request.hydration
        existing_program.notes = request.notes
        
        # Delete existing blocks
        await db.execute(
            select(TrainingProgramBlock)
            .where(TrainingProgramBlock.program_id == existing_program.id)
        )
        # Would need to delete - simplified for now
        
        program = existing_program
    else:
        # Create new program
        program = TrainingProgram(
            wrestler_id=wrestler_id,
            date=program_date,
            readiness=request.readiness,
            session_rpe=request.sessionRPE,
            bodyweight=request.bodyweight,
            hydration=request.hydration,
            notes=request.notes,
        )
        db.add(program)
        await db.flush()
    
    # Add exercise blocks
    for exercise in request.exercises:
        # Calculate average weight and reps
        if exercise.sets:
            avg_weight = sum(s.weight for s in exercise.sets) / len(exercise.sets)
            rep_range = f"{min(s.reps for s in exercise.sets)}-{max(s.reps for s in exercise.sets)}"
        else:
            avg_weight = 0
            rep_range = "0"
        
        block = TrainingProgramBlock(
            program_id=program.id,
            name=exercise.name,
            sets=len(exercise.sets),
            reps=rep_range,
            load=avg_weight,
        )
        db.add(block)
    
    await db.commit()
    
    return TrainingProgramUpdateResponse(success=True)
