"""
Pydantic schemas for the Wrestling Dashboard API.

This module defines request/response schemas that match the API documentation.
"""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, EmailStr


# ============================================================================
# Common Schemas
# ============================================================================


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


class StatusLabel(str, Enum):
    """Status label enumeration."""
    GOOD = "good"
    WARNING = "warning"
    BAD = "bad"


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    error: str
    message: str
    details: Optional[Dict[str, str]] = None


# ============================================================================
# Authentication Schemas
# ============================================================================


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str = Field(min_length=1)


class LoginUser(BaseModel):
    """User info in login response."""
    id: str
    name: str
    role: str


class LoginResponse(BaseModel):
    """Login response schema."""
    accessToken: str
    refreshToken: str
    user: LoginUser


class RefreshRequest(BaseModel):
    """Refresh token request schema."""
    refreshToken: str


class RefreshResponse(BaseModel):
    """Refresh token response schema."""
    accessToken: str


class LogoutRequest(BaseModel):
    """Logout request schema."""
    refreshToken: str


class LogoutResponse(BaseModel):
    """Logout response schema."""
    success: bool = True


# ============================================================================
# Wrestler Schemas
# ============================================================================


class WrestlerBase(BaseModel):
    """Base wrestler schema."""
    id: str
    nameFa: str
    nameEn: str
    weightClass: int = Field(ge=50, le=150)
    imageUrl: Optional[str] = None


class WrestlerListItem(WrestlerBase):
    """Wrestler in list response."""
    pass


class WrestlerListResponse(BaseModel):
    """Wrestler list response."""
    wrestlers: List[WrestlerListItem]


class WrestlerSummary(WrestlerBase):
    """Wrestler summary/detail response."""
    status: str  # competition_ready|normal|attention


# ============================================================================
# Overview Schemas
# ============================================================================


class OverviewDeltas(BaseModel):
    """Overview metric deltas."""
    overallScore: float
    msi: float
    mes: float
    api: float
    vo2max: float
    frr: float
    acs: float
    bos: float


class OverviewMetricsData(BaseModel):
    """Overview metrics values."""
    overallScore: float = Field(ge=0, le=100)
    msi: float = Field(ge=0, le=100)
    mes: float = Field(ge=0, le=100)
    api: float = Field(ge=0, le=1000)
    vo2max: float = Field(ge=0, le=100)
    frr: float = Field(ge=0, le=100)
    acs: float = Field(ge=0, le=100)
    bos: float = Field(ge=0, le=10)


class OverviewStatusLabels(BaseModel):
    """Overview status labels."""
    overallScore: StatusLabel
    msi: StatusLabel
    mes: StatusLabel
    api: StatusLabel
    vo2max: StatusLabel
    frr: StatusLabel
    acs: StatusLabel
    bos: StatusLabel


class OverviewResponse(BaseModel):
    """Overview metrics response."""
    metrics: OverviewMetricsData
    deltas: OverviewDeltas
    statusLabels: OverviewStatusLabels


class SectionScoreResponse(BaseModel):
    """Section score response."""
    section: str
    score: float = Field(ge=0, le=100)
    grade: Grade
    lastUpdated: str  # YYYY-MM-DD


class OverviewChartResponse(BaseModel):
    """Overview radar chart response."""
    labels: List[str]
    values: List[float]


# ============================================================================
# Body Composition Schemas
# ============================================================================


class BodyCompositionMetricsData(BaseModel):
    """Body composition metrics."""
    weight: float = Field(ge=30, le=200)
    bodyFatPercentage: float = Field(ge=0, le=50)
    muscleMass: float = Field(ge=20, le=150)
    bmr: float = Field(ge=1000, le=5000)
    powerToWeight: float = Field(ge=0, le=5)


class BodyCompositionResponse(BaseModel):
    """Body composition metrics response."""
    metrics: BodyCompositionMetricsData


class TimeSeriesData(BaseModel):
    """Generic time series data."""
    dates: List[str]
    values: List[float]


class BodyCompositionTrendsResponse(BaseModel):
    """Body composition trends response."""
    powerToWeight: TimeSeriesData
    bodyWeight: TimeSeriesData
    bodyFat: TimeSeriesData


class InBodyResponse(BaseModel):
    """InBody breakdown response."""
    intracellularWater: float
    extracellularWater: float
    visceralFatLevel: float
    phaseAngle: float


# ============================================================================
# Bloodwork Schemas
# ============================================================================


class BloodworkMetricsData(BaseModel):
    """Bloodwork metrics."""
    hemoglobin: float = Field(ge=8, le=25)
    hematocrit: float = Field(ge=20, le=70)
    testosteroneLevel: float = Field(ge=100, le=1500)
    lastTestDate: str
    status: str  # optimal|normal|attention


class BloodworkResponse(BaseModel):
    """Bloodwork response."""
    metrics: BloodworkMetricsData


class CBCPanel(BaseModel):
    """CBC panel data."""
    wbc: TimeSeriesData
    rbc: TimeSeriesData
    hemoglobin: TimeSeriesData
    hematocrit: TimeSeriesData
    platelets: TimeSeriesData


class LipidsPanel(BaseModel):
    """Lipids panel data."""
    ldl: TimeSeriesData
    hdl: TimeSeriesData
    triglycerides: TimeSeriesData


class BloodworkChartsResponse(BaseModel):
    """Bloodwork charts response."""
    cbc: CBCPanel
    lipids: LipidsPanel


# ============================================================================
# Recovery Schemas
# ============================================================================


class RecoveryMetricsData(BaseModel):
    """Recovery metrics."""
    sleepQuality: float = Field(ge=0, le=100)
    hrvScore: float = Field(ge=0, le=200)
    fatigueLevel: float = Field(ge=0, le=100)
    hydrationLevel: float = Field(ge=0, le=100)
    readinessScore: float = Field(ge=0, le=100)


class RecoveryResponse(BaseModel):
    """Recovery response."""
    metrics: RecoveryMetricsData


class SleepData(BaseModel):
    """Sleep chart data."""
    dates: List[str]
    duration: List[float]
    quality: List[float]


class SorenessData(BaseModel):
    """Soreness chart data."""
    dates: List[str]
    upper: List[float]
    core: List[float]
    lower: List[float]


class RecoveryChartsResponse(BaseModel):
    """Recovery charts response."""
    sleep: SleepData
    hrv: TimeSeriesData
    stress: TimeSeriesData
    soreness: SorenessData


# ============================================================================
# Supplements Schemas
# ============================================================================


class SupplementsMetricsData(BaseModel):
    """Supplements metrics."""
    adherenceRate: float = Field(ge=0, le=100)
    monthlyProgress: str
    performanceCorrelation: float = Field(ge=-1, le=1)
    totalSupplements: int = Field(ge=0, le=50)
    creatineDailyGrams: float = Field(ge=0, le=20)
    proteinDailyGrams: float = Field(ge=0, le=500)
    hydrationLiters: float = Field(ge=0, le=10)


class SupplementsResponse(BaseModel):
    """Supplements response."""
    metrics: SupplementsMetricsData


class SupplementItem(BaseModel):
    """Single supplement in stack."""
    name: str
    daily: bool


class StackOverview(BaseModel):
    """Stack overview data."""
    supplements: List[SupplementItem]


class SupplementsChartsResponse(BaseModel):
    """Supplements charts response."""
    creatine: TimeSeriesData
    protein: TimeSeriesData
    adherence: TimeSeriesData
    hydration: TimeSeriesData
    performanceCorrelation: TimeSeriesData
    stackOverview: StackOverview


# ============================================================================
# Bodybuilding Performance Schemas
# ============================================================================


class PerformanceMetricsData(BaseModel):
    """Performance metrics."""
    benchPressMax: float = Field(ge=0, le=1000)
    squatMax: float = Field(ge=0, le=1000)
    deadliftMax: float = Field(ge=0, le=1000)
    vo2max: float = Field(ge=0, le=100)
    bodyFatPercentage: float = Field(ge=0, le=50)
    performanceScore: float = Field(ge=0, le=100)


class PerformanceResponse(BaseModel):
    """Performance response."""
    metrics: PerformanceMetricsData


class StrengthCharts(BaseModel):
    """Strength charts."""
    bench: TimeSeriesData
    squat: TimeSeriesData
    deadlift: TimeSeriesData


class HRZones(BaseModel):
    """HR zones data."""
    zones: List[str]
    values: List[float]


class CardioCharts(BaseModel):
    """Cardio charts."""
    vo2max: TimeSeriesData
    hrZones: HRZones


class RPEBuckets(BaseModel):
    """RPE bucket data."""
    buckets: List[str]
    values: List[float]


class AnalyticsCharts(BaseModel):
    """Analytics charts."""
    volumeLoad: TimeSeriesData
    rpe: RPEBuckets


class LabelValuePair(BaseModel):
    """Label-value pair for charts."""
    labels: List[str]
    values: List[float]


class BodybuildingCharts(BaseModel):
    """Bodybuilding-specific charts."""
    symmetry: LabelValuePair
    activation: LabelValuePair


class PerformanceChartsResponse(BaseModel):
    """Performance charts response."""
    strength: StrengthCharts
    cardio: CardioCharts
    analytics: AnalyticsCharts
    bodybuilding: BodybuildingCharts


# ============================================================================
# Training Program Schemas
# ============================================================================


class ExerciseSet(BaseModel):
    """Single exercise set."""
    reps: int = Field(ge=1, le=100)
    weight: float = Field(ge=0, le=1000)


class Exercise(BaseModel):
    """Exercise with sets."""
    name: str
    sets: List[ExerciseSet]


class TrainingProgramResponse(BaseModel):
    """Training program response."""
    date: str
    readiness: Optional[int] = Field(default=None, ge=1, le=10)
    sessionRPE: Optional[int] = Field(default=None, ge=1, le=10)
    bodyweight: Optional[float] = Field(default=None, ge=30, le=200)
    hydration: Optional[float] = Field(default=None, ge=0, le=10)
    notes: Optional[str] = None
    exercises: List[Exercise] = []


class TrainingProgramRequest(BaseModel):
    """Training program update request."""
    date: str
    readiness: Optional[int] = Field(default=None, ge=1, le=10)
    sessionRPE: Optional[int] = Field(default=None, ge=1, le=10)
    bodyweight: Optional[float] = Field(default=None, ge=30, le=200)
    hydration: Optional[float] = Field(default=None, ge=0, le=10)
    notes: Optional[str] = None
    exercises: List[Exercise] = []


class TrainingProgramUpdateResponse(BaseModel):
    """Training program update response."""
    success: bool = True


# ============================================================================
# Calendar Schemas
# ============================================================================


class ProgramBlock(BaseModel):
    """Program block for calendar."""
    name: str
    sets: int = Field(ge=1, le=20)
    reps: str


class CalendarProgram(BaseModel):
    """Calendar program entry."""
    date: str
    title: Optional[str] = None
    focus: Optional[str] = None
    blocks: List[ProgramBlock] = []
    nutrition: Optional[str] = None
    recovery: Optional[str] = None
    aiRecommendations: List[str] = []


class CalendarResponse(BaseModel):
    """Calendar response."""
    programs: List[CalendarProgram]


# ============================================================================
# Team Schemas
# ============================================================================


class TeamStatsResponse(BaseModel):
    """Team stats response."""
    totalAthletes: int
    averageScore: float
    competitionReady: int
    needsAttention: int


class AthleteInsight(BaseModel):
    """Athlete insight item."""
    label: str
    type: str  # success|warning|info


class TeamAthlete(BaseModel):
    """Team athlete card data."""
    id: str
    nameFa: str
    weightClass: int
    overallScore: float
    currentActivity: Optional[str] = None
    insights: List[AthleteInsight] = []
    trainingWeek: Optional[int] = None
    totalWeeks: Optional[int] = None


class TeamAthletesResponse(BaseModel):
    """Team athletes response."""
    athletes: List[TeamAthlete]


# ============================================================================
# AI Schemas
# ============================================================================


class ChartData(BaseModel):
    """Simple chart data for AI insight."""
    labels: Optional[List[str]] = None
    values: Optional[List[float]] = None


class ChartInsightRequest(BaseModel):
    """Chart insight request."""
    wrestlerId: str
    chartId: str
    chartData: ChartData
    locale: str = "fa-IR"


class Recommendation(BaseModel):
    """AI recommendation."""
    text: str
    priority: Priority


class ChartInsightResponse(BaseModel):
    """Chart insight response."""
    summary: str
    patterns: List[str]
    recommendations: List[Recommendation]
    warnings: List[str] = []


class TimeSeriesPoint(BaseModel):
    """Time series point."""
    date: str
    value: float


class SeriesData(BaseModel):
    """Series data for advanced insight."""
    name: str
    points: List[TimeSeriesPoint]


class AdvancedChartData(BaseModel):
    """Advanced chart data."""
    series: List[SeriesData]


class Threshold(BaseModel):
    """Threshold definition."""
    label: str
    value: float


class Baseline(BaseModel):
    """Baseline definition."""
    value: float
    label: str


class InsightContext(BaseModel):
    """Context for advanced insight."""
    baseline: Optional[Baseline] = None
    thresholds: Optional[List[Threshold]] = None
    recentNotes: Optional[List[str]] = None


class AdvancedChartInsightRequest(BaseModel):
    """Advanced chart insight request."""
    wrestlerId: str
    section: str  # body_composition|bloodwork|recovery|supplements|bodybuilding_performance
    chartId: str
    chartData: AdvancedChartData
    context: Optional[InsightContext] = None
    locale: str = "fa-IR"


class Anomaly(BaseModel):
    """Detected anomaly."""
    label: str
    date: str
    value: float


class AdvancedChartInsightResponse(BaseModel):
    """Advanced chart insight response."""
    summary: str
    patterns: List[str]
    anomalies: List[Anomaly] = []
    recommendations: List[Recommendation]
    confidence: float = Field(ge=0, le=1)


class AITrainingProgramRequest(BaseModel):
    """AI training program request."""
    wrestlerId: str
    goal: str
    date: str


class AIGeneratedProgram(BaseModel):
    """AI-generated program."""
    date: str
    title: str
    focus: str
    blocks: List[ProgramBlock]
    nutrition: Optional[str] = None
    recovery: Optional[str] = None
    aiRecommendations: List[str] = []


class AITrainingProgramResponse(BaseModel):
    """AI training program response."""
    program: AIGeneratedProgram


# ============================================================================
# Scoring Schemas
# ============================================================================


class OverallScoreResponse(BaseModel):
    """Overall score response."""
    score: float = Field(ge=0, le=100)
    grade: Grade
    lastUpdated: str


class DomainScoresResponse(BaseModel):
    """Domain scores response."""
    strength: float = Field(ge=0, le=100)
    endurance: float = Field(ge=0, le=100)
    recovery: float = Field(ge=0, le=100)
    bodyComposition: float = Field(ge=0, le=100)
    bloodwork: float = Field(ge=0, le=100)
    supplements: float = Field(ge=0, le=100)


class ScoreDriverItem(BaseModel):
    """Score driver item."""
    metric: str
    impact: str  # "+" or "-"
    weight: float = Field(ge=0, le=1)


class ScoreExplanationResponse(BaseModel):
    """Score explanation response."""
    drivers: List[ScoreDriverItem]
    notes: Optional[str] = None
