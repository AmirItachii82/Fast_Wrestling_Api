"""
Pydantic schemas for legacy Fittechno data APIs.

This module defines request/response schemas for accessing legacy measurement data
from the Fittechno database with session date resolution.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ============================================================================
# Common Response Schemas
# ============================================================================


class MeasurementWithDate(BaseModel):
    """Base measurement response with session date resolved."""
    id: int
    sessionId: str
    athleteName: str
    metricName: str
    sessionDate: Optional[str] = None  # Gregorian date
    sessionDateShamsi: Optional[str] = None  # Persian date


class PaginationInfo(BaseModel):
    """Pagination metadata."""
    page: int = Field(ge=1)
    perPage: int = Field(ge=1, le=100)
    total: int = Field(ge=0)
    totalPages: int = Field(ge=0)


# ============================================================================
# Legacy Athlete Schemas
# ============================================================================


class LegacyAthleteResponse(BaseModel):
    """Legacy athlete response."""
    id: int
    athleteName: str
    field: Optional[str] = None
    name: Optional[str] = None
    createdAt: Optional[str] = None


class LegacyAthleteListResponse(BaseModel):
    """List of legacy athletes."""
    athletes: List[LegacyAthleteResponse]
    pagination: PaginationInfo


# ============================================================================
# Session Time Schemas
# ============================================================================


class SessionTimeResponse(BaseModel):
    """Session time response."""
    sessionId: int
    athleteId: Optional[int] = None
    athleteName: Optional[str] = None
    miladiDate: Optional[str] = None  # Gregorian date
    shamsiDate: Optional[str] = None  # Persian date
    startTime: Optional[str] = None
    testCategory: Optional[str] = None
    createdAt: Optional[str] = None


class SessionTimeListResponse(BaseModel):
    """List of session times."""
    sessions: List[SessionTimeResponse]
    pagination: PaginationInfo


# ============================================================================
# Metric Definition Schemas
# ============================================================================


class MetricDefinitionResponse(BaseModel):
    """Metric definition response."""
    id: int
    metricName: str
    metricMethod: Optional[str] = None
    category: Optional[str] = None


class MetricDefinitionListResponse(BaseModel):
    """List of metric definitions."""
    metrics: List[MetricDefinitionResponse]
    pagination: PaginationInfo


# ============================================================================
# Body Composition Schemas (Legacy)
# ============================================================================


class LegacyBodyCompositionResponse(MeasurementWithDate):
    """Legacy body composition measurement response."""
    nvalue: Optional[float] = None  # Numeric value
    tvalue: Optional[str] = None  # Text value


class LegacyBodyCompositionListResponse(BaseModel):
    """List of legacy body composition measurements."""
    data: List[LegacyBodyCompositionResponse]
    pagination: PaginationInfo
    style: str = Field(description="Wrestling style: 'freestyle' or 'greco-roman'")


# ============================================================================
# Chestbelt Heart Rate Schemas (Legacy)
# ============================================================================


class LegacyChestbeltHRResponse(MeasurementWithDate):
    """Legacy chestbelt heart rate measurement response."""
    nvalue: Optional[float] = None  # Numeric value
    tvalue: Optional[str] = None  # Text value


class LegacyChestbeltHRListResponse(BaseModel):
    """List of legacy chestbelt HR measurements."""
    data: List[LegacyChestbeltHRResponse]
    pagination: PaginationInfo


# ============================================================================
# Fitness Schemas (Legacy)
# ============================================================================


class LegacyFitnessResponse(MeasurementWithDate):
    """Legacy fitness measurement response."""
    metricMethod: Optional[str] = None
    value: Optional[float] = None


class LegacyFitnessListResponse(BaseModel):
    """List of legacy fitness measurements."""
    data: List[LegacyFitnessResponse]
    pagination: PaginationInfo


# ============================================================================
# Urion Analysis Schemas (Legacy)
# ============================================================================


class LegacyUrionAnalysisResponse(MeasurementWithDate):
    """Legacy urion analysis measurement response."""
    metricMethod: Optional[str] = None
    value: Optional[float] = None


class LegacyUrionAnalysisListResponse(BaseModel):
    """List of legacy urion analysis measurements."""
    data: List[LegacyUrionAnalysisResponse]
    pagination: PaginationInfo


# ============================================================================
# Filter Parameters Schemas
# ============================================================================


class MeasurementFilterParams(BaseModel):
    """Common filter parameters for measurement queries."""
    athleteName: Optional[str] = Field(default=None, description="Filter by athlete name")
    metricName: Optional[str] = Field(default=None, description="Filter by metric name")
    sessionId: Optional[str] = Field(default=None, description="Filter by session ID")
    dateFrom: Optional[str] = Field(default=None, description="Filter by start date (YYYY-MM-DD)")
    dateTo: Optional[str] = Field(default=None, description="Filter by end date (YYYY-MM-DD)")
    page: int = Field(default=1, ge=1, description="Page number")
    perPage: int = Field(default=50, ge=1, le=100, description="Items per page")
