"""
Database models for the Wrestling Dashboard API.

This module defines all SQLModel entities based on the database analysis document.
Models include:
- Users (authentication)
- Teams
- Wrestlers
- Various metric tables (overview, body composition, bloodwork, etc.)
- Training programs
- AI insights
- Scoring
"""

from datetime import date, datetime
from enum import Enum
from typing import List, Optional
import uuid

from sqlmodel import Field, Relationship, SQLModel, Column, Index
from sqlalchemy import JSON, Text, UniqueConstraint


class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    COACH = "coach"
    ATHLETE = "athlete"


class WrestlerStatus(str, Enum):
    """Wrestler status enumeration."""
    COMPETITION_READY = "competition_ready"
    NORMAL = "normal"
    ATTENTION = "attention"


class Grade(str, Enum):
    """Score grade enumeration."""
    GOOD = "good"
    WARNING = "warning"
    BAD = "bad"


class Priority(str, Enum):
    """Recommendation priority enumeration."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ============================================================================
# Core Entities
# ============================================================================


class User(SQLModel, table=True):
    """User model for authentication."""
    
    __tablename__ = "users"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    email: str = Field(unique=True, index=True, max_length=255)
    password_hash: str = Field(max_length=255)
    name: str = Field(max_length=255)
    role: UserRole = Field(default=UserRole.ATHLETE)
    wrestler_id: Optional[str] = Field(default=None, foreign_key="wrestlers.id")
    team_id: Optional[str] = Field(default=None, foreign_key="teams.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    wrestler: Optional["Wrestler"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "[User.wrestler_id]"}
    )


class Team(SQLModel, table=True):
    """Team entity."""
    
    __tablename__ = "teams"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    wrestlers: List["Wrestler"] = Relationship(back_populates="team")


class Wrestler(SQLModel, table=True):
    """Wrestler profile entity."""
    
    __tablename__ = "wrestlers"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    team_id: Optional[str] = Field(default=None, foreign_key="teams.id", index=True)
    name_fa: str = Field(max_length=255)
    name_en: str = Field(max_length=255)
    weight_class: int = Field(ge=50, le=150)
    image_url: Optional[str] = Field(default=None, max_length=500)
    status: WrestlerStatus = Field(default=WrestlerStatus.NORMAL)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    team: Optional[Team] = Relationship(back_populates="wrestlers")
    user: Optional[User] = Relationship(
        back_populates="wrestler",
        sa_relationship_kwargs={"foreign_keys": "[User.wrestler_id]"}
    )
    overview_metrics: List["OverviewMetrics"] = Relationship(back_populates="wrestler")
    overview_series: List["OverviewSeries"] = Relationship(back_populates="wrestler")
    body_composition_metrics: List["BodyCompositionMetrics"] = Relationship(back_populates="wrestler")
    body_composition_series: List["BodyCompositionSeries"] = Relationship(back_populates="wrestler")
    bloodwork_metrics: List["BloodworkMetrics"] = Relationship(back_populates="wrestler")
    bloodwork_series: List["BloodworkSeries"] = Relationship(back_populates="wrestler")
    recovery_metrics: List["RecoveryMetrics"] = Relationship(back_populates="wrestler")
    recovery_series: List["RecoverySeries"] = Relationship(back_populates="wrestler")
    supplements_metrics: List["SupplementsMetrics"] = Relationship(back_populates="wrestler")
    supplements_series: List["SupplementsSeries"] = Relationship(back_populates="wrestler")
    performance_metrics: List["PerformanceMetrics"] = Relationship(back_populates="wrestler")
    performance_series: List["PerformanceSeries"] = Relationship(back_populates="wrestler")
    training_programs: List["TrainingProgram"] = Relationship(back_populates="wrestler")
    section_scores: List["SectionScore"] = Relationship(back_populates="wrestler")
    ai_chart_insights: List["AIChartInsight"] = Relationship(back_populates="wrestler")


# ============================================================================
# Metrics Tables (Latest Snapshots)
# ============================================================================


class OverviewMetrics(SQLModel, table=True):
    """Overview metrics snapshot per wrestler."""
    
    __tablename__ = "overview_metrics"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    wrestler_id: str = Field(foreign_key="wrestlers.id", index=True)
    overall_score: float = Field(ge=0, le=100)
    msi: float = Field(ge=0, le=100)  # Muscle Strength Index
    mes: float = Field(ge=0, le=100)  # Muscle Endurance Score
    api: float = Field(ge=0, le=1000)  # Anaerobic Power Index
    vo2max: float = Field(ge=0, le=100)
    frr: float = Field(ge=0, le=100)  # Fatigue Recovery Rate
    acs: float = Field(ge=0, le=100)  # Athletic Conditioning Score
    bos: float = Field(ge=0, le=10)  # Body Optimization Score
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    wrestler: Optional[Wrestler] = Relationship(back_populates="overview_metrics")


class OverviewSeries(SQLModel, table=True):
    """Overview time series data (e.g., radar chart values)."""
    
    __tablename__ = "overview_series"
    __table_args__ = (
        Index("ix_overview_series_wrestler_recorded", "wrestler_id", "recorded_at"),
    )
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    wrestler_id: str = Field(foreign_key="wrestlers.id", index=True)
    label: str = Field(max_length=100)  # e.g., "کمر", "سینه"
    value: float = Field(ge=0, le=100)
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    wrestler: Optional[Wrestler] = Relationship(back_populates="overview_series")


class BodyCompositionMetrics(SQLModel, table=True):
    """Body composition metrics snapshot."""
    
    __tablename__ = "body_composition_metrics"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    wrestler_id: str = Field(foreign_key="wrestlers.id", index=True)
    weight: float = Field(ge=30, le=200)
    body_fat_percent: float = Field(ge=0, le=50)
    muscle_mass: float = Field(ge=20, le=150)
    bmr: float = Field(ge=1000, le=5000)
    power_to_weight: float = Field(ge=0, le=5)
    # InBody breakdown
    intracellular_water: Optional[float] = Field(default=None, ge=0, le=100)
    extracellular_water: Optional[float] = Field(default=None, ge=0, le=100)
    visceral_fat_level: Optional[float] = Field(default=None, ge=0, le=30)
    phase_angle: Optional[float] = Field(default=None, ge=0, le=15)
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    wrestler: Optional[Wrestler] = Relationship(back_populates="body_composition_metrics")


class BodyCompositionSeries(SQLModel, table=True):
    """Body composition time series data."""
    
    __tablename__ = "body_composition_series"
    __table_args__ = (
        Index("ix_body_composition_series_wrestler_recorded", "wrestler_id", "recorded_at"),
    )
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    wrestler_id: str = Field(foreign_key="wrestlers.id", index=True)
    metric_name: str = Field(max_length=100)
    value: float
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    wrestler: Optional[Wrestler] = Relationship(back_populates="body_composition_series")


class BloodworkMetrics(SQLModel, table=True):
    """Bloodwork metrics snapshot."""
    
    __tablename__ = "bloodwork_metrics"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    wrestler_id: str = Field(foreign_key="wrestlers.id", index=True)
    hemoglobin: float = Field(ge=8, le=25)
    hematocrit: float = Field(ge=20, le=70)
    testosterone: float = Field(ge=100, le=1500)
    status: str = Field(default="normal", max_length=50)  # optimal|normal|attention
    last_test_date: date = Field(default_factory=date.today)
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    wrestler: Optional[Wrestler] = Relationship(back_populates="bloodwork_metrics")


class BloodworkSeries(SQLModel, table=True):
    """Bloodwork time series data."""
    
    __tablename__ = "bloodwork_series"
    __table_args__ = (
        Index("ix_bloodwork_series_wrestler_recorded", "wrestler_id", "recorded_at"),
    )
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    wrestler_id: str = Field(foreign_key="wrestlers.id", index=True)
    panel: str = Field(max_length=50)  # cbc|lipids
    metric_name: str = Field(max_length=100)
    value: float
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    wrestler: Optional[Wrestler] = Relationship(back_populates="bloodwork_series")


class RecoveryMetrics(SQLModel, table=True):
    """Recovery metrics snapshot."""
    
    __tablename__ = "recovery_metrics"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    wrestler_id: str = Field(foreign_key="wrestlers.id", index=True)
    sleep_quality: float = Field(ge=0, le=100)
    hrv_score: float = Field(ge=0, le=200)
    fatigue_level: float = Field(ge=0, le=100)
    hydration_level: float = Field(ge=0, le=100)
    readiness_score: float = Field(ge=0, le=100)
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    wrestler: Optional[Wrestler] = Relationship(back_populates="recovery_metrics")


class RecoverySeries(SQLModel, table=True):
    """Recovery time series data."""
    
    __tablename__ = "recovery_series"
    __table_args__ = (
        Index("ix_recovery_series_wrestler_recorded", "wrestler_id", "recorded_at"),
    )
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    wrestler_id: str = Field(foreign_key="wrestlers.id", index=True)
    metric_name: str = Field(max_length=100)
    value: float
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    wrestler: Optional[Wrestler] = Relationship(back_populates="recovery_series")


class SupplementsMetrics(SQLModel, table=True):
    """Supplements metrics snapshot."""
    
    __tablename__ = "supplements_metrics"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    wrestler_id: str = Field(foreign_key="wrestlers.id", index=True)
    adherence_rate: float = Field(ge=0, le=100)
    monthly_progress: str = Field(default="0%", max_length=20)
    performance_corr: float = Field(ge=-1, le=1)
    total_supplements: int = Field(ge=0, le=50)
    creatine_daily_grams: float = Field(ge=0, le=20)
    protein_daily_grams: float = Field(ge=0, le=500)
    hydration_liters: float = Field(ge=0, le=10)
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    wrestler: Optional[Wrestler] = Relationship(back_populates="supplements_metrics")


class SupplementsSeries(SQLModel, table=True):
    """Supplements time series data."""
    
    __tablename__ = "supplements_series"
    __table_args__ = (
        Index("ix_supplements_series_wrestler_recorded", "wrestler_id", "recorded_at"),
    )
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    wrestler_id: str = Field(foreign_key="wrestlers.id", index=True)
    metric_name: str = Field(max_length=100)
    value: float
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    wrestler: Optional[Wrestler] = Relationship(back_populates="supplements_series")


class PerformanceMetrics(SQLModel, table=True):
    """Bodybuilding/performance metrics snapshot."""
    
    __tablename__ = "performance_metrics"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    wrestler_id: str = Field(foreign_key="wrestlers.id", index=True)
    bench_max: float = Field(ge=0, le=1000)
    squat_max: float = Field(ge=0, le=1000)
    deadlift_max: float = Field(ge=0, le=1000)
    vo2max: float = Field(ge=0, le=100)
    body_fat_percent: float = Field(ge=0, le=50)
    performance_score: float = Field(ge=0, le=100)
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    wrestler: Optional[Wrestler] = Relationship(back_populates="performance_metrics")


class PerformanceSeries(SQLModel, table=True):
    """Performance time series data."""
    
    __tablename__ = "performance_series"
    __table_args__ = (
        Index("ix_performance_series_wrestler_recorded", "wrestler_id", "recorded_at"),
    )
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    wrestler_id: str = Field(foreign_key="wrestlers.id", index=True)
    metric_name: str = Field(max_length=100)
    value: float
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    wrestler: Optional[Wrestler] = Relationship(back_populates="performance_series")


# ============================================================================
# Training Programs
# ============================================================================


class TrainingProgram(SQLModel, table=True):
    """Training program entity."""
    
    __tablename__ = "training_programs"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    wrestler_id: str = Field(foreign_key="wrestlers.id", index=True)
    date: date
    title: Optional[str] = Field(default=None, max_length=255)
    focus: Optional[str] = Field(default=None, max_length=255)
    readiness: Optional[int] = Field(default=None, ge=1, le=10)
    session_rpe: Optional[int] = Field(default=None, ge=1, le=10)
    bodyweight: Optional[float] = Field(default=None, ge=30, le=200)
    hydration: Optional[float] = Field(default=None, ge=0, le=10)
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    nutrition: Optional[str] = Field(default=None, sa_column=Column(Text))
    recovery: Optional[str] = Field(default=None, sa_column=Column(Text))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    wrestler: Optional[Wrestler] = Relationship(back_populates="training_programs")
    blocks: List["TrainingProgramBlock"] = Relationship(back_populates="program")
    ai_recommendations: List["TrainingProgramAIRecommendation"] = Relationship(back_populates="program")


class TrainingProgramBlock(SQLModel, table=True):
    """Training program exercise block."""
    
    __tablename__ = "training_program_blocks"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    program_id: str = Field(foreign_key="training_programs.id", index=True)
    name: str = Field(max_length=255)
    sets: int = Field(ge=1, le=20)
    reps: str = Field(max_length=50)  # e.g., "6-8"
    load: Optional[float] = Field(default=None, ge=0)
    notes: Optional[str] = Field(default=None, max_length=500)
    
    # Relationship
    program: Optional[TrainingProgram] = Relationship(back_populates="blocks")


class TrainingProgramAIRecommendation(SQLModel, table=True):
    """AI-generated recommendations for training programs."""
    
    __tablename__ = "training_program_ai_recommendations"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    program_id: str = Field(foreign_key="training_programs.id", index=True)
    recommendation: str = Field(sa_column=Column(Text))
    
    # Relationship
    program: Optional[TrainingProgram] = Relationship(back_populates="ai_recommendations")


# ============================================================================
# AI Analysis
# ============================================================================


class AIChartInsight(SQLModel, table=True):
    """Cached AI chart insights."""
    
    __tablename__ = "ai_chart_insights"
    __table_args__ = (
        UniqueConstraint("wrestler_id", "chart_id", "input_hash", name="uq_ai_insight_hash"),
    )
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    wrestler_id: str = Field(foreign_key="wrestlers.id", index=True)
    chart_id: str = Field(max_length=100)
    input_hash: str = Field(max_length=64, index=True)
    summary: str = Field(sa_column=Column(Text))
    patterns_json: Optional[str] = Field(default=None, sa_column=Column(Text))
    recommendations_json: Optional[str] = Field(default=None, sa_column=Column(Text))
    warnings_json: Optional[str] = Field(default=None, sa_column=Column(Text))
    anomalies_json: Optional[str] = Field(default=None, sa_column=Column(Text))
    confidence: Optional[float] = Field(default=None, ge=0, le=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship
    wrestler: Optional[Wrestler] = Relationship(back_populates="ai_chart_insights")


# ============================================================================
# Scoring
# ============================================================================


class SectionScore(SQLModel, table=True):
    """Section scores per wrestler."""
    
    __tablename__ = "section_scores"
    __table_args__ = (
        Index("ix_section_scores_wrestler_section_recorded", "wrestler_id", "section_key", "recorded_at"),
    )
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    wrestler_id: str = Field(foreign_key="wrestlers.id", index=True)
    section_key: str = Field(max_length=50)  # overview|body_composition|bloodwork|recovery|supplements|bodybuilding_performance
    score: float = Field(ge=0, le=100)
    grade: Grade = Field(default=Grade.GOOD)
    recorded_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    wrestler: Optional[Wrestler] = Relationship(back_populates="section_scores")
    drivers: List["ScoreDriver"] = Relationship(back_populates="section_score")


class ScoreDriver(SQLModel, table=True):
    """Score driver factors for transparency."""
    
    __tablename__ = "score_drivers"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    section_score_id: str = Field(foreign_key="section_scores.id", index=True)
    metric_name: str = Field(max_length=100)
    impact: str = Field(max_length=10)  # "+" or "-"
    weight: float = Field(ge=0, le=1)
    
    # Relationship
    section_score: Optional[SectionScore] = Relationship(back_populates="drivers")


# ============================================================================
# Token Blacklist (for logout)
# ============================================================================


class TokenBlacklist(SQLModel, table=True):
    """Blacklisted refresh tokens."""
    
    __tablename__ = "token_blacklist"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    token_jti: str = Field(unique=True, index=True, max_length=64)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
