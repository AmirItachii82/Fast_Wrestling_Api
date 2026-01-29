"""
Unit tests for scoring service.
"""

import pytest

from app.services.scoring_service import (
    compute_grade,
    compute_overview_score,
    compute_body_composition_score,
    compute_bloodwork_score,
    compute_recovery_score,
    compute_supplements_score,
    compute_performance_score,
    compute_overall_wrestler_score,
    compute_status_label,
)
from app.models import Grade


class TestComputeGrade:
    """Tests for compute_grade function."""
    
    def test_good_grade_high_score(self):
        """Score >= 80 should be GOOD."""
        assert compute_grade(80) == Grade.GOOD
        assert compute_grade(90) == Grade.GOOD
        assert compute_grade(100) == Grade.GOOD
    
    def test_warning_grade_medium_score(self):
        """Score 60-79 should be WARNING."""
        assert compute_grade(60) == Grade.WARNING
        assert compute_grade(70) == Grade.WARNING
        assert compute_grade(79) == Grade.WARNING
    
    def test_bad_grade_low_score(self):
        """Score < 60 should be BAD."""
        assert compute_grade(0) == Grade.BAD
        assert compute_grade(30) == Grade.BAD
        assert compute_grade(59) == Grade.BAD


class TestComputeStatusLabel:
    """Tests for compute_status_label function."""
    
    def test_good_status(self):
        """Value above good threshold should be 'good'."""
        assert compute_status_label(90, 80, 60) == "good"
    
    def test_warning_status(self):
        """Value between thresholds should be 'warning'."""
        assert compute_status_label(70, 80, 60) == "warning"
    
    def test_bad_status(self):
        """Value below warning threshold should be 'bad'."""
        assert compute_status_label(50, 80, 60) == "bad"


class TestComputeOverviewScore:
    """Tests for overview score computation."""
    
    def test_compute_high_score(self):
        """Test computation with high values."""
        score, grade = compute_overview_score(
            overall_score=90,
            msi=90,
            mes=90,
            api=800,
            vo2max=60,
            frr=90,
            acs=90,
            bos=8,
        )
        assert score >= 80
        assert grade == Grade.GOOD
    
    def test_compute_low_score(self):
        """Test computation with low values."""
        score, grade = compute_overview_score(
            overall_score=30,
            msi=30,
            mes=30,
            api=200,
            vo2max=30,
            frr=30,
            acs=30,
            bos=2,
        )
        assert score < 60
        assert grade == Grade.BAD
    
    def test_deterministic(self):
        """Same inputs should always produce same output."""
        inputs = dict(
            overall_score=86,
            msi=92,
            mes=78,
            api=420,
            vo2max=55,
            frr=84,
            acs=72,
            bos=4,
        )
        result1 = compute_overview_score(**inputs)
        result2 = compute_overview_score(**inputs)
        assert result1 == result2


class TestComputeBodyCompositionScore:
    """Tests for body composition score computation."""
    
    def test_optimal_athlete(self):
        """Optimal athlete metrics should score high."""
        score, grade = compute_body_composition_score(
            weight=86,
            body_fat_percent=10,
            muscle_mass=76,
            bmr=2100,
            power_to_weight=2.0,
        )
        assert score >= 70
    
    def test_high_body_fat(self):
        """High body fat should lower score."""
        score_low_bf, _ = compute_body_composition_score(
            weight=86, body_fat_percent=10, muscle_mass=76, bmr=2100, power_to_weight=2.0
        )
        score_high_bf, _ = compute_body_composition_score(
            weight=86, body_fat_percent=25, muscle_mass=76, bmr=2100, power_to_weight=2.0
        )
        assert score_low_bf > score_high_bf


class TestComputeBloodworkScore:
    """Tests for bloodwork score computation."""
    
    def test_optimal_values(self):
        """Optimal bloodwork should score high."""
        score, grade = compute_bloodwork_score(
            hemoglobin=16,
            hematocrit=46,
            testosterone=750,
        )
        assert score >= 80
        assert grade == Grade.GOOD
    
    def test_low_hemoglobin(self):
        """Low hemoglobin should lower score."""
        score_normal, _ = compute_bloodwork_score(16, 46, 750)
        score_low, _ = compute_bloodwork_score(10, 46, 750)
        assert score_normal > score_low


class TestComputeRecoveryScore:
    """Tests for recovery score computation."""
    
    def test_well_recovered(self):
        """Well-recovered athlete should score high."""
        score, grade = compute_recovery_score(
            sleep_quality=90,
            hrv_score=120,
            fatigue_level=10,
            hydration_level=90,
            readiness_score=90,
        )
        assert score >= 80
    
    def test_high_fatigue(self):
        """High fatigue should lower score."""
        score_low_fatigue, _ = compute_recovery_score(90, 120, 10, 90, 90)
        score_high_fatigue, _ = compute_recovery_score(90, 120, 80, 90, 90)
        assert score_low_fatigue > score_high_fatigue


class TestComputeSupplementsScore:
    """Tests for supplements score computation."""
    
    def test_high_adherence(self):
        """High adherence should score well."""
        score, grade = compute_supplements_score(
            adherence_rate=95,
            performance_corr=0.9,
        )
        assert score >= 80
    
    def test_low_adherence(self):
        """Low adherence should score poorly."""
        score, grade = compute_supplements_score(
            adherence_rate=30,
            performance_corr=0.2,
        )
        assert score < 60


class TestComputePerformanceScore:
    """Tests for performance score computation."""
    
    def test_strong_athlete(self):
        """Strong athlete should score high."""
        score, grade = compute_performance_score(
            bench_max=350,
            squat_max=450,
            deadlift_max=550,
            vo2max=55,
            body_fat_percent=12,
        )
        assert score >= 70


class TestComputeOverallWrestlerScore:
    """Tests for overall wrestler score computation."""
    
    def test_all_scores_present(self):
        """Test with all section scores."""
        score, grade = compute_overall_wrestler_score(
            overview_score=85,
            body_comp_score=80,
            bloodwork_score=85,
            recovery_score=90,
            supplements_score=75,
            performance_score=85,
        )
        assert 70 <= score <= 100
    
    def test_partial_scores(self):
        """Test with some missing scores."""
        score, grade = compute_overall_wrestler_score(
            overview_score=85,
            body_comp_score=None,
            bloodwork_score=85,
            recovery_score=None,
            supplements_score=None,
            performance_score=85,
        )
        assert score > 0
    
    def test_no_scores(self):
        """Test with all scores missing."""
        score, grade = compute_overall_wrestler_score(
            overview_score=None,
            body_comp_score=None,
            bloodwork_score=None,
            recovery_score=None,
            supplements_score=None,
            performance_score=None,
        )
        assert score == 0
        assert grade == Grade.BAD
