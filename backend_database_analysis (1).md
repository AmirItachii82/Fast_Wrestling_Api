# Backend Database Analysis

This document outlines the recommended database entities, relationships, and key queries to support the Wrestling Dashboard API. It focuses on data needed for advanced charts, AI analysis, and per-section scoring.

---

## 1) Data Model Overview

### 1.1 Core Entities

- users
  - id, email, password_hash, role, created_at, updated_at
- teams
  - id, name, created_at, updated_at
- wrestlers
  - id, team_id, name_fa, name_en, weight_class, image_url, status

### 1.2 Metrics and Time Series

- overview_metrics (latest snapshot per wrestler)
  - id, wrestler_id, overall_score, msi, mes, api, vo2max, frr, acs, bos, recorded_at
- overview_series (per muscle group radar or timeseries if needed)
  - id, wrestler_id, label, value, recorded_at

- body_composition_metrics
  - id, wrestler_id, weight, body_fat_percent, muscle_mass, bmr, power_to_weight, recorded_at
- body_composition_series
  - id, wrestler_id, metric_name, value, recorded_at

- bloodwork_metrics
  - id, wrestler_id, hemoglobin, hematocrit, testosterone, status, last_test_date
- bloodwork_series
  - id, wrestler_id, panel, metric_name, value, recorded_at

- recovery_metrics
  - id, wrestler_id, sleep_quality, hrv_score, fatigue_level, hydration_level, readiness_score, recorded_at
- recovery_series
  - id, wrestler_id, metric_name, value, recorded_at

- supplements_metrics
  - id, wrestler_id, adherence_rate, monthly_progress, performance_corr, total_supplements,
    creatine_daily_grams, protein_daily_grams, hydration_liters, recorded_at
- supplements_series
  - id, wrestler_id, metric_name, value, recorded_at

- performance_metrics
  - id, wrestler_id, bench_max, squat_max, deadlift_max, vo2max, body_fat_percent, performance_score, recorded_at
- performance_series
  - id, wrestler_id, metric_name, value, recorded_at

### 1.3 Programs & Calendar

- training_programs
  - id, wrestler_id, date, title, focus, nutrition, recovery, created_at
- training_program_blocks
  - id, program_id, name, sets, reps, load, notes
- training_program_ai_recommendations
  - id, program_id, recommendation

### 1.4 AI Analysis

- ai_chart_insights
  - id, wrestler_id, chart_id, input_hash, summary, patterns_json, recommendations_json, warnings_json, created_at

### 1.5 Scoring

- section_scores
  - id, wrestler_id, section_key, score, grade, recorded_at
  - section_key in: overview, body_composition, bloodwork, recovery, supplements, bodybuilding_performance
- score_drivers
  - id, section_score_id, metric_name, impact, weight

---

## 2) Relationships

- teams 1-to-many wrestlers
- wrestlers 1-to-many metrics tables
- training_programs 1-to-many blocks, recommendations
- section_scores 1-to-many score_drivers

---

## 3) Query Patterns

### 3.1 Latest Snapshot for a Section

Select the newest metrics row by recorded_at:

- overview_metrics
- body_composition_metrics
- bloodwork_metrics
- recovery_metrics
- supplements_metrics
- performance_metrics

### 3.2 Time Series for Advanced Charts

Select time window by wrestler_id and metric_name:

- body_composition_series
- bloodwork_series
- recovery_series
- supplements_series
- performance_series

### 3.3 AI Insight Caching

Use chart_id + input_hash to avoid repeated AI calls for unchanged data. If a cached insight is newer than a TTL, return it.

---

## 4) Indexing Strategy

- Index on wrestler_id for all metric tables.
- Composite index on (wrestler_id, recorded_at) for time series tables.
- Index on (wrestler_id, section_key, recorded_at) for section_scores.
- Unique index on (wrestler_id, chart_id, input_hash) for ai_chart_insights.

---

## 5) Data Retention

- Keep at least 12 months of time series for trend charts.
- Archive older records or downsample to weekly averages.

---

## 6) Scoring Computation Notes

- Each section has a score stored in section_scores.
- Score drivers capture the weighted factors for transparency.
- Use deterministic formulas so the same inputs always yield the same score.

---

End of document.
