"""
AI endpoints.

Provides:
- POST /ai/chart-insight - Chart insight
- POST /ai/chart-insight/advanced - Advanced chart insight
- POST /ai/training-program - AI training program generation

Note: Rate limiting is recommended for these endpoints (10 requests/min/user).
"""

import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models import User, AIChartInsight
from app.schemas import (
    ChartInsightRequest,
    ChartInsightResponse,
    AdvancedChartInsightRequest,
    AdvancedChartInsightResponse,
    AITrainingProgramRequest,
    AITrainingProgramResponse,
    ErrorResponse,
)
from app.services.ai_service import (
    get_llm_adapter,
    compute_input_hash,
    sanitize_for_ai,
    cache_service,
)
from app.utils.dependencies import get_current_user, validate_wrestler_access
from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


@router.post(
    "/chart-insight",
    response_model=ChartInsightResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        501: {"model": ErrorResponse, "description": "AI provider not configured"},
    },
)
async def get_chart_insight(
    request: ChartInsightRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> ChartInsightResponse:
    """
    Get AI insight for a chart.
    
    Implements caching to reduce AI calls for identical chart data.
    
    Args:
        request: Chart insight request with chart data.
        db: Database session.
        current_user: Authenticated user.
        
    Returns:
        ChartInsightResponse: AI-generated insight.
    """
    await validate_wrestler_access(request.wrestlerId, current_user, db)
    
    # Sanitize data for AI (remove PII)
    sanitized_data = sanitize_for_ai(request.chartData.model_dump())
    
    # Compute input hash for caching
    hash_input = {
        "wrestler_id": request.wrestlerId,
        "chart_id": request.chartId,
        "chart_data": sanitized_data,
    }
    input_hash = compute_input_hash(hash_input)
    
    # Check cache first
    cache_key = f"chart_insight:{input_hash}"
    cached_result = await cache_service.get(cache_key)
    
    if cached_result:
        # Return cached result
        cached_data = json.loads(cached_result)
        return ChartInsightResponse(**cached_data)
    
    # Check database cache
    result = await db.execute(
        select(AIChartInsight)
        .where(
            AIChartInsight.wrestler_id == request.wrestlerId,
            AIChartInsight.chart_id == request.chartId,
            AIChartInsight.input_hash == input_hash,
        )
        .order_by(AIChartInsight.created_at.desc())
        .limit(1)
    )
    db_cached = result.scalar_one_or_none()
    
    if db_cached:
        # Reconstruct response from DB
        patterns = json.loads(db_cached.patterns_json) if db_cached.patterns_json else []
        recommendations = json.loads(db_cached.recommendations_json) if db_cached.recommendations_json else []
        warnings = json.loads(db_cached.warnings_json) if db_cached.warnings_json else []
        
        response = ChartInsightResponse(
            summary=db_cached.summary,
            patterns=patterns,
            recommendations=recommendations,
            warnings=warnings,
        )
        
        # Update Redis cache
        await cache_service.set(cache_key, response.model_dump_json(), settings.ai_cache_ttl_hours)
        
        return response
    
    # Get AI adapter and generate insight
    adapter = get_llm_adapter()
    
    try:
        response = await adapter.generate_chart_insight(
            chart_id=request.chartId,
            chart_data=sanitized_data,
            locale=request.locale,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={
                "error": "AI_ERROR",
                "message": "Failed to generate AI insight. Provider may not be configured.",
                "details": {"error": str(e)},
            },
        )
    
    # Save to database
    db_insight = AIChartInsight(
        wrestler_id=request.wrestlerId,
        chart_id=request.chartId,
        input_hash=input_hash,
        summary=response.summary,
        patterns_json=json.dumps(response.patterns),
        recommendations_json=json.dumps([r.model_dump() for r in response.recommendations]),
        warnings_json=json.dumps(response.warnings),
    )
    db.add(db_insight)
    await db.commit()
    
    # Update cache
    await cache_service.set(cache_key, response.model_dump_json(), settings.ai_cache_ttl_hours)
    
    return response


@router.post(
    "/chart-insight/advanced",
    response_model=AdvancedChartInsightResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        501: {"model": ErrorResponse, "description": "AI provider not configured"},
    },
)
async def get_advanced_chart_insight(
    request: AdvancedChartInsightRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AdvancedChartInsightResponse:
    """
    Get advanced AI insight for a chart with time series data.
    
    Implements caching to reduce AI calls.
    
    Args:
        request: Advanced chart insight request.
        db: Database session.
        current_user: Authenticated user.
        
    Returns:
        AdvancedChartInsightResponse: AI-generated advanced insight.
    """
    await validate_wrestler_access(request.wrestlerId, current_user, db)
    
    # Sanitize data for AI
    chart_data = sanitize_for_ai(request.chartData.model_dump())
    context_data = sanitize_for_ai(request.context.model_dump() if request.context else {})
    
    # Compute input hash
    hash_input = {
        "wrestler_id": request.wrestlerId,
        "section": request.section,
        "chart_id": request.chartId,
        "chart_data": chart_data,
        "context": context_data,
    }
    input_hash = compute_input_hash(hash_input)
    
    # Check cache
    cache_key = f"advanced_insight:{input_hash}"
    cached_result = await cache_service.get(cache_key)
    
    if cached_result:
        cached_data = json.loads(cached_result)
        return AdvancedChartInsightResponse(**cached_data)
    
    # Get AI adapter and generate insight
    adapter = get_llm_adapter()
    
    try:
        response = await adapter.generate_advanced_insight(
            section=request.section,
            chart_id=request.chartId,
            chart_data=chart_data,
            context=context_data,
            locale=request.locale,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={
                "error": "AI_ERROR",
                "message": "Failed to generate AI insight.",
                "details": {"error": str(e)},
            },
        )
    
    # Save to database
    db_insight = AIChartInsight(
        wrestler_id=request.wrestlerId,
        chart_id=f"{request.section}:{request.chartId}",
        input_hash=input_hash,
        summary=response.summary,
        patterns_json=json.dumps(response.patterns),
        recommendations_json=json.dumps([r.model_dump() for r in response.recommendations]),
        anomalies_json=json.dumps([a.model_dump() for a in response.anomalies]),
        confidence=response.confidence,
    )
    db.add(db_insight)
    await db.commit()
    
    # Update cache
    await cache_service.set(cache_key, response.model_dump_json(), settings.ai_cache_ttl_hours)
    
    return response


@router.post(
    "/training-program",
    response_model=AITrainingProgramResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Access denied"},
        501: {"model": ErrorResponse, "description": "AI provider not configured"},
    },
)
async def generate_training_program(
    request: AITrainingProgramRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> AITrainingProgramResponse:
    """
    Generate an AI-powered training program.
    
    Args:
        request: Training program generation request.
        db: Database session.
        current_user: Authenticated user.
        
    Returns:
        AITrainingProgramResponse: Generated training program.
    """
    await validate_wrestler_access(request.wrestlerId, current_user, db)
    
    # Compute input hash for caching
    hash_input = {
        "wrestler_id": request.wrestlerId,
        "goal": request.goal,
        "date": request.date,
    }
    input_hash = compute_input_hash(hash_input)
    
    # Check cache
    cache_key = f"training_program:{input_hash}"
    cached_result = await cache_service.get(cache_key)
    
    if cached_result:
        cached_data = json.loads(cached_result)
        return AITrainingProgramResponse(**cached_data)
    
    # Get AI adapter and generate program
    adapter = get_llm_adapter()
    
    try:
        program = await adapter.generate_training_program(
            goal=request.goal,
            target_date=request.date,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={
                "error": "AI_ERROR",
                "message": "Failed to generate training program.",
                "details": {"error": str(e)},
            },
        )
    
    response = AITrainingProgramResponse(program=program)
    
    # Update cache
    await cache_service.set(cache_key, response.model_dump_json(), settings.ai_cache_ttl_hours)
    
    return response
