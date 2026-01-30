"""
Legacy Fittechno database models.

This module defines SQLModel entities for the existing Fittechno database tables.
These models provide read-only access to legacy measurement data.

Tables included:
- Athlete (legacy athlete records)
- SessionTime (session dates and metadata)
- Metric (metric definitions)
- BodyCompositionFS (freestyle body composition data)
- BodyCompositionGR (greco-roman body composition data)
- ChestbeltHRGR (greco-roman heart rate data)
- FitnessFS (freestyle fitness data)
- UrionAnalysisGR (greco-roman urion analysis data)
"""

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def _utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


class LegacyAthlete(SQLModel, table=True):
    """Legacy athlete model from Fittechno database."""
    
    __tablename__ = "athlete"
    
    id: int = Field(primary_key=True)
    athlete_name: str
    field: Optional[str] = None
    name: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=_utc_now)


class SessionTime(SQLModel, table=True):
    """Session time model - links session_id to dates."""
    
    __tablename__ = "session_time"
    
    session_id: int = Field(primary_key=True)
    athlete_id: Optional[int] = None
    miladi_date: Optional[str] = None  # Gregorian date as text
    shamsi_date: Optional[str] = None  # Persian/Shamsi date as text
    start_time: Optional[str] = None
    test_category: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=_utc_now)
    athlete_name: Optional[str] = None


class LegacyMetric(SQLModel, table=True):
    """Metric definition model."""
    
    __tablename__ = "metric"
    
    id: int = Field(primary_key=True)
    metric_name: str
    metric_method: Optional[str] = None
    category: Optional[str] = None


class BodyCompositionFS(SQLModel, table=True):
    """Body composition data for freestyle wrestling."""
    
    __tablename__ = "body_composition_fs"
    
    id: int = Field(primary_key=True)
    session_id: str = Field(max_length=255)
    athlete_name: str = Field(max_length=255)
    metric_name: str = Field(max_length=255)
    nvalue: Optional[float] = None
    tvalue: Optional[str] = Field(default="", max_length=255)


class BodyCompositionGR(SQLModel, table=True):
    """Body composition data for greco-roman wrestling."""
    
    __tablename__ = "body_composition_gr"
    
    id: int = Field(primary_key=True)
    session_id: str = Field(max_length=255)
    athlete_name: str = Field(max_length=255)
    metric_name: str = Field(max_length=255)
    nvalue: Optional[float] = None
    tvalue: Optional[str] = Field(default="", max_length=255)


class ChestbeltHRGR(SQLModel, table=True):
    """Chestbelt heart rate data for greco-roman wrestling."""
    
    __tablename__ = "chestbelt_hr_gr"
    
    id: int = Field(primary_key=True)
    session_id: str = Field(max_length=255)
    athlete_name: str = Field(max_length=255)
    metric_name: str = Field(max_length=255)
    nvalue: Optional[float] = None
    tvalue: Optional[str] = Field(default=None, max_length=255)


class FitnessFS(SQLModel, table=True):
    """Fitness data for freestyle wrestling."""
    
    __tablename__ = "fitness_fs"
    
    id: int = Field(primary_key=True)
    session_id: str = Field(max_length=255)
    athlete_name: str = Field(max_length=255)
    metric_name: str = Field(max_length=255)
    metric_method: Optional[str] = Field(default=None, max_length=255)
    value: Optional[float] = None


class UrionAnalysisGR(SQLModel, table=True):
    """Urion analysis data for greco-roman wrestling."""
    
    __tablename__ = "urion_analysis_gr"
    
    id: int = Field(primary_key=True)
    session_id: str = Field(max_length=255)
    athlete_name: str = Field(max_length=255)
    metric_name: str = Field(max_length=255)
    metric_method: Optional[str] = Field(default=None, max_length=255)
    value: Optional[float] = None
