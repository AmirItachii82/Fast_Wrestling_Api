"""Services module initialization."""

from app.services.auth_service import (
    authenticate_user,
    create_user,
    generate_tokens,
    refresh_access_token,
    blacklist_token,
    get_user_by_id,
)
from app.services.wrestler_service import (
    get_wrestlers,
    get_wrestler_by_id,
    get_latest_overview_metrics,
    get_latest_body_composition_metrics,
    get_latest_bloodwork_metrics,
    get_latest_recovery_metrics,
    get_latest_supplements_metrics,
    get_latest_performance_metrics,
    get_latest_section_score,
)
from app.services.scoring_service import (
    compute_grade,
    compute_overview_score,
    compute_body_composition_score,
    compute_bloodwork_score,
    compute_recovery_score,
    compute_supplements_score,
    compute_performance_score,
    compute_overall_wrestler_score,
)
from app.services.ai_service import (
    get_llm_adapter,
    compute_input_hash,
    sanitize_for_ai,
    cache_service,
    LLMAdapter,
    MockLLMAdapter,
)
from app.services.time_series_service import (
    get_body_composition_series,
    get_bloodwork_series,
    get_recovery_series,
    get_supplements_series,
    get_performance_series,
    get_overview_series,
)

__all__ = [
    # Auth
    "authenticate_user",
    "create_user",
    "generate_tokens",
    "refresh_access_token",
    "blacklist_token",
    "get_user_by_id",
    # Wrestler
    "get_wrestlers",
    "get_wrestler_by_id",
    "get_latest_overview_metrics",
    "get_latest_body_composition_metrics",
    "get_latest_bloodwork_metrics",
    "get_latest_recovery_metrics",
    "get_latest_supplements_metrics",
    "get_latest_performance_metrics",
    "get_latest_section_score",
    # Scoring
    "compute_grade",
    "compute_overview_score",
    "compute_body_composition_score",
    "compute_bloodwork_score",
    "compute_recovery_score",
    "compute_supplements_score",
    "compute_performance_score",
    "compute_overall_wrestler_score",
    # AI
    "get_llm_adapter",
    "compute_input_hash",
    "sanitize_for_ai",
    "cache_service",
    "LLMAdapter",
    "MockLLMAdapter",
    # Time series
    "get_body_composition_series",
    "get_bloodwork_series",
    "get_recovery_series",
    "get_supplements_series",
    "get_performance_series",
    "get_overview_series",
]
