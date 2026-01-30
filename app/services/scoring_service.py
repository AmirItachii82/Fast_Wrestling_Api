"""
Scoring service for computing wrestler scores.

This module provides deterministic score computation functions
for each section: overview, body_composition, bloodwork, recovery,
supplements, and bodybuilding_performance.
"""

from typing import Optional, Tuple

from app.models import Grade


def compute_grade(score: float) -> Grade:
    """
    Compute grade from score.
    
    Args:
        score: Score value (0-100).
        
    Returns:
        Grade: good, warning, or bad.
    """
    if score >= 80:
        return Grade.GOOD
    elif score >= 60:
        return Grade.WARNING
    else:
        return Grade.BAD


def compute_status_label(value: float, threshold_good: float, threshold_warning: float) -> str:
    """
    Compute status label for a metric.
    
    Args:
        value: The metric value.
        threshold_good: Value above this is 'good'.
        threshold_warning: Value above this is 'warning'.
        
    Returns:
        str: 'good', 'warning', or 'bad'.
    """
    if value >= threshold_good:
        return "good"
    elif value >= threshold_warning:
        return "warning"
    else:
        return "bad"


def compute_overview_score(
    overall_score: float,
    msi: float,
    mes: float,
    api: float,
    vo2max: float,
    frr: float,
    acs: float,
    bos: float,
) -> Tuple[float, Grade]:
    """
    Compute overview section score.
    
    Uses weighted average of normalized metrics.
    
    Args:
        overall_score: Overall score (0-100).
        msi: Muscle Strength Index (0-100).
        mes: Muscle Endurance Score (0-100).
        api: Anaerobic Power Index (0-1000, normalized).
        vo2max: VO2 max (0-100).
        frr: Fatigue Recovery Rate (0-100).
        acs: Athletic Conditioning Score (0-100).
        bos: Body Optimization Score (0-10, normalized).
        
    Returns:
        Tuple[float, Grade]: (score, grade)
    """
    # Normalize api (0-1000) to 0-100
    normalized_api = min(100, api / 10)
    # Normalize bos (0-10) to 0-100
    normalized_bos = bos * 10
    
    # Weighted average
    weights = {
        "overall_score": 0.20,
        "msi": 0.15,
        "mes": 0.15,
        "api": 0.10,
        "vo2max": 0.15,
        "frr": 0.10,
        "acs": 0.10,
        "bos": 0.05,
    }
    
    score = (
        overall_score * weights["overall_score"]
        + msi * weights["msi"]
        + mes * weights["mes"]
        + normalized_api * weights["api"]
        + vo2max * weights["vo2max"]
        + frr * weights["frr"]
        + acs * weights["acs"]
        + normalized_bos * weights["bos"]
    )
    
    return round(score, 1), compute_grade(score)


def compute_body_composition_score(
    weight: float,
    body_fat_percent: float,
    muscle_mass: float,
    bmr: float,
    power_to_weight: float,
) -> Tuple[float, Grade]:
    """
    Compute body composition section score.
    
    Args:
        weight: Body weight in kg.
        body_fat_percent: Body fat percentage.
        muscle_mass: Muscle mass in kg.
        bmr: Basal metabolic rate.
        power_to_weight: Power to weight ratio.
        
    Returns:
        Tuple[float, Grade]: (score, grade)
    """
    # Score based on optimal ranges for wrestlers
    # Lower body fat is better (optimal 8-12%)
    bf_score = max(0, 100 - abs(body_fat_percent - 10) * 5)
    
    # Higher muscle mass relative to weight is better
    muscle_ratio = (muscle_mass / weight) * 100 if weight > 0 else 0
    mr_score = min(100, muscle_ratio)
    
    # Power to weight (optimal 1.8-2.2)
    ptw_score = max(0, 100 - abs(power_to_weight - 2.0) * 30)
    
    # Weighted average
    score = (bf_score * 0.35) + (mr_score * 0.40) + (ptw_score * 0.25)
    
    return round(score, 1), compute_grade(score)


def compute_bloodwork_score(
    hemoglobin: float,
    hematocrit: float,
    testosterone: float,
) -> Tuple[float, Grade]:
    """
    Compute bloodwork section score.
    
    Args:
        hemoglobin: Hemoglobin level (g/dL).
        hematocrit: Hematocrit percentage.
        testosterone: Testosterone level (ng/dL).
        
    Returns:
        Tuple[float, Grade]: (score, grade)
    """
    # Hemoglobin optimal range 14-18 g/dL
    hb_score = max(0, 100 - abs(hemoglobin - 16) * 8)
    
    # Hematocrit optimal range 42-50%
    hct_score = max(0, 100 - abs(hematocrit - 46) * 5)
    
    # Testosterone optimal range 600-900 ng/dL
    test_score = max(0, 100 - abs(testosterone - 750) * 0.1)
    
    # Weighted average
    score = (hb_score * 0.35) + (hct_score * 0.30) + (test_score * 0.35)
    
    return round(score, 1), compute_grade(score)


def compute_recovery_score(
    sleep_quality: float,
    hrv_score: float,
    fatigue_level: float,
    hydration_level: float,
    readiness_score: float,
) -> Tuple[float, Grade]:
    """
    Compute recovery section score.
    
    Args:
        sleep_quality: Sleep quality (0-100).
        hrv_score: HRV score (0-200, normalized).
        fatigue_level: Fatigue level (0-100, lower is better).
        hydration_level: Hydration level (0-100).
        readiness_score: Readiness score (0-100).
        
    Returns:
        Tuple[float, Grade]: (score, grade)
    """
    # Normalize HRV (0-200) to 0-100
    normalized_hrv = min(100, hrv_score / 2)
    
    # Invert fatigue (lower is better)
    fatigue_inverted = 100 - fatigue_level
    
    # Weighted average
    score = (
        sleep_quality * 0.25
        + normalized_hrv * 0.20
        + fatigue_inverted * 0.20
        + hydration_level * 0.15
        + readiness_score * 0.20
    )
    
    return round(score, 1), compute_grade(score)


def compute_supplements_score(
    adherence_rate: float,
    performance_corr: float,
) -> Tuple[float, Grade]:
    """
    Compute supplements section score.
    
    Args:
        adherence_rate: Supplement adherence rate (0-100).
        performance_corr: Performance correlation (-1 to 1).
        
    Returns:
        Tuple[float, Grade]: (score, grade)
    """
    # Normalize performance correlation to 0-100
    normalized_corr = (performance_corr + 1) * 50
    
    # Weighted average
    score = (adherence_rate * 0.60) + (normalized_corr * 0.40)
    
    return round(score, 1), compute_grade(score)


def compute_performance_score(
    bench_max: float,
    squat_max: float,
    deadlift_max: float,
    vo2max: float,
    body_fat_percent: float,
) -> Tuple[float, Grade]:
    """
    Compute bodybuilding performance section score.
    
    Args:
        bench_max: Bench press max (lbs).
        squat_max: Squat max (lbs).
        deadlift_max: Deadlift max (lbs).
        vo2max: VO2 max.
        body_fat_percent: Body fat percentage.
        
    Returns:
        Tuple[float, Grade]: (score, grade)
    """
    # Normalize strength lifts (assuming elite level ~500 lbs)
    bench_score = min(100, (bench_max / 400) * 100)
    squat_score = min(100, (squat_max / 500) * 100)
    deadlift_score = min(100, (deadlift_max / 600) * 100)
    
    # VO2 max (good athlete 50-60)
    vo2_score = min(100, (vo2max / 60) * 100)
    
    # Body fat (optimal for performance 10-15%)
    bf_score = max(0, 100 - abs(body_fat_percent - 12.5) * 4)
    
    # Weighted average
    score = (
        bench_score * 0.15
        + squat_score * 0.20
        + deadlift_score * 0.20
        + vo2_score * 0.25
        + bf_score * 0.20
    )
    
    return round(score, 1), compute_grade(score)


def compute_overall_wrestler_score(
    overview_score: Optional[float],
    body_comp_score: Optional[float],
    bloodwork_score: Optional[float],
    recovery_score: Optional[float],
    supplements_score: Optional[float],
    performance_score: Optional[float],
) -> Tuple[float, Grade]:
    """
    Compute overall wrestler score from all domain scores.
    
    Args:
        overview_score: Overview section score.
        body_comp_score: Body composition section score.
        bloodwork_score: Bloodwork section score.
        recovery_score: Recovery section score.
        supplements_score: Supplements section score.
        performance_score: Performance section score.
        
    Returns:
        Tuple[float, Grade]: (score, grade)
    """
    scores = []
    weights = []
    
    if overview_score is not None:
        scores.append(overview_score)
        weights.append(0.15)
    if body_comp_score is not None:
        scores.append(body_comp_score)
        weights.append(0.20)
    if bloodwork_score is not None:
        scores.append(bloodwork_score)
        weights.append(0.15)
    if recovery_score is not None:
        scores.append(recovery_score)
        weights.append(0.20)
    if supplements_score is not None:
        scores.append(supplements_score)
        weights.append(0.10)
    if performance_score is not None:
        scores.append(performance_score)
        weights.append(0.20)
    
    if not scores:
        return 0.0, Grade.BAD
    
    # Normalize weights
    total_weight = sum(weights)
    normalized_weights = [w / total_weight for w in weights]
    
    # Weighted average
    score = sum(s * w for s, w in zip(scores, normalized_weights))
    
    return round(score, 1), compute_grade(score)
