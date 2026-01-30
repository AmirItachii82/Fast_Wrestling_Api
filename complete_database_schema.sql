-- ============================================================================
-- Complete PostgreSQL Database Schema for Wrestling Dashboard API
-- ============================================================================
-- This file contains:
-- 1. Legacy Fittechno tables (athlete, body_composition_fs/gr, chestbelt_hr_gr, 
--    fitness_fs, metric, session_time, urion_analysis_gr)
-- 2. New API tables from api_schema.sql (teams, wrestlers, api_users, etc.)
-- 
-- IMPORTANT:
-- - All tables use IF NOT EXISTS for safe imports
-- - Foreign key constraints are flexible to allow partial data imports
-- - Indexes are created for common query patterns
-- ============================================================================

-- ============================================================================
-- SECTION 1: LEGACY FITTECHNO TABLES (Existing Database Tables)
-- ============================================================================
-- These tables store existing measurement data from the Fittechno system.
-- They are preserved exactly as-is to maintain compatibility.

-- Athletes table (legacy)
CREATE TABLE IF NOT EXISTS public.athlete (
    id BIGINT NOT NULL PRIMARY KEY,
    athlete_name TEXT NOT NULL,
    field TEXT,
    name TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_athlete_name ON public.athlete(athlete_name);

-- Session Time table - links session_id to dates
CREATE TABLE IF NOT EXISTS public.session_time (
    session_id BIGINT NOT NULL PRIMARY KEY,
    athlete_id BIGINT,
    miladi_date TEXT,
    shamsi_date TEXT,
    start_time TEXT,
    test_category TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    athlete_name TEXT
);

CREATE INDEX IF NOT EXISTS ix_session_time_athlete_id ON public.session_time(athlete_id);
CREATE INDEX IF NOT EXISTS ix_session_time_athlete_name ON public.session_time(athlete_name);
CREATE INDEX IF NOT EXISTS ix_session_time_miladi_date ON public.session_time(miladi_date);
CREATE INDEX IF NOT EXISTS ix_session_time_test_category ON public.session_time(test_category);

-- Metric definitions table
CREATE TABLE IF NOT EXISTS public.metric (
    id BIGINT NOT NULL PRIMARY KEY,
    metric_name TEXT NOT NULL,
    metric_method TEXT,
    category TEXT
);

CREATE INDEX IF NOT EXISTS ix_metric_name ON public.metric(metric_name);
CREATE INDEX IF NOT EXISTS ix_metric_category ON public.metric(category);

-- Body Composition - Freestyle wrestling data
CREATE TABLE IF NOT EXISTS public.body_composition_fs (
    id BIGINT NOT NULL PRIMARY KEY,
    session_id CHARACTER VARYING(255) NOT NULL,
    athlete_name CHARACTER VARYING(255) NOT NULL,
    metric_name CHARACTER VARYING(255) NOT NULL,
    nvalue DOUBLE PRECISION,
    tvalue CHARACTER VARYING(255) DEFAULT ''::CHARACTER VARYING
);

CREATE INDEX IF NOT EXISTS ix_body_composition_fs_session_id ON public.body_composition_fs(session_id);
CREATE INDEX IF NOT EXISTS ix_body_composition_fs_athlete_name ON public.body_composition_fs(athlete_name);
CREATE INDEX IF NOT EXISTS ix_body_composition_fs_metric_name ON public.body_composition_fs(metric_name);

-- Body Composition - Greco-Roman wrestling data
CREATE TABLE IF NOT EXISTS public.body_composition_gr (
    id BIGINT NOT NULL PRIMARY KEY,
    session_id CHARACTER VARYING(255) NOT NULL,
    athlete_name CHARACTER VARYING(255) NOT NULL,
    metric_name CHARACTER VARYING(255) NOT NULL,
    nvalue DOUBLE PRECISION,
    tvalue CHARACTER VARYING(255) DEFAULT ''::CHARACTER VARYING
);

CREATE INDEX IF NOT EXISTS ix_body_composition_gr_session_id ON public.body_composition_gr(session_id);
CREATE INDEX IF NOT EXISTS ix_body_composition_gr_athlete_name ON public.body_composition_gr(athlete_name);
CREATE INDEX IF NOT EXISTS ix_body_composition_gr_metric_name ON public.body_composition_gr(metric_name);

-- Chestbelt Heart Rate - Greco-Roman wrestling data
CREATE TABLE IF NOT EXISTS public.chestbelt_hr_gr (
    id BIGINT NOT NULL PRIMARY KEY,
    session_id CHARACTER VARYING(255) NOT NULL,
    athlete_name CHARACTER VARYING(255) NOT NULL,
    metric_name CHARACTER VARYING(255) NOT NULL,
    nvalue DOUBLE PRECISION,
    tvalue CHARACTER VARYING(255)
);

CREATE INDEX IF NOT EXISTS ix_chestbelt_hr_gr_session_id ON public.chestbelt_hr_gr(session_id);
CREATE INDEX IF NOT EXISTS ix_chestbelt_hr_gr_athlete_name ON public.chestbelt_hr_gr(athlete_name);
CREATE INDEX IF NOT EXISTS ix_chestbelt_hr_gr_metric_name ON public.chestbelt_hr_gr(metric_name);

-- Fitness - Freestyle wrestling data
CREATE TABLE IF NOT EXISTS public.fitness_fs (
    id BIGINT NOT NULL PRIMARY KEY,
    session_id CHARACTER VARYING(255) NOT NULL,
    athlete_name CHARACTER VARYING(255) NOT NULL,
    metric_name CHARACTER VARYING(255) NOT NULL,
    metric_method CHARACTER VARYING(255),
    value DOUBLE PRECISION
);

CREATE INDEX IF NOT EXISTS ix_fitness_fs_session_id ON public.fitness_fs(session_id);
CREATE INDEX IF NOT EXISTS ix_fitness_fs_athlete_name ON public.fitness_fs(athlete_name);
CREATE INDEX IF NOT EXISTS ix_fitness_fs_metric_name ON public.fitness_fs(metric_name);

-- Urion Analysis - Greco-Roman wrestling data
CREATE TABLE IF NOT EXISTS public.urion_analysis_gr (
    id BIGINT NOT NULL PRIMARY KEY,
    session_id CHARACTER VARYING(255) NOT NULL,
    athlete_name CHARACTER VARYING(255) NOT NULL,
    metric_name CHARACTER VARYING(255) NOT NULL,
    metric_method CHARACTER VARYING(255),
    value DOUBLE PRECISION
);

CREATE INDEX IF NOT EXISTS ix_urion_analysis_gr_session_id ON public.urion_analysis_gr(session_id);
CREATE INDEX IF NOT EXISTS ix_urion_analysis_gr_athlete_name ON public.urion_analysis_gr(athlete_name);
CREATE INDEX IF NOT EXISTS ix_urion_analysis_gr_metric_name ON public.urion_analysis_gr(metric_name);

-- ============================================================================
-- SECTION 2: NEW API TABLES (from api_schema.sql)
-- ============================================================================
-- These tables are used by the new Wrestling Dashboard API.
-- They provide a modern data model for the frontend application.

-- Teams Table
CREATE TABLE IF NOT EXISTS public.teams (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

-- Wrestlers Table
CREATE TABLE IF NOT EXISTS public.wrestlers (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    team_id VARCHAR(36) REFERENCES public.teams(id) ON DELETE SET NULL,
    name_fa VARCHAR(255) NOT NULL,
    name_en VARCHAR(255) NOT NULL,
    weight_class INTEGER NOT NULL CHECK (weight_class >= 50 AND weight_class <= 150),
    image_url VARCHAR(500),
    status VARCHAR(50) NOT NULL DEFAULT 'normal' CHECK (status IN ('competition_ready', 'normal', 'attention')),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_wrestlers_team_id ON public.wrestlers(team_id);

-- API Users Table
CREATE TABLE IF NOT EXISTS public.api_users (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'athlete' CHECK (role IN ('admin', 'coach', 'athlete')),
    wrestler_id VARCHAR(36) REFERENCES public.wrestlers(id) ON DELETE SET NULL,
    team_id VARCHAR(36) REFERENCES public.teams(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_api_users_email ON public.api_users(email);

-- Token Blacklist Table
CREATE TABLE IF NOT EXISTS public.token_blacklist (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    token_jti VARCHAR(64) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_token_blacklist_token_jti ON public.token_blacklist(token_jti);

-- Overview Metrics Table
CREATE TABLE IF NOT EXISTS public.overview_metrics (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    wrestler_id VARCHAR(36) NOT NULL REFERENCES public.wrestlers(id) ON DELETE CASCADE,
    overall_score FLOAT NOT NULL CHECK (overall_score >= 0 AND overall_score <= 100),
    msi FLOAT NOT NULL CHECK (msi >= 0 AND msi <= 100),
    mes FLOAT NOT NULL CHECK (mes >= 0 AND mes <= 100),
    api FLOAT NOT NULL CHECK (api >= 0 AND api <= 1000),
    vo2max FLOAT NOT NULL CHECK (vo2max >= 0 AND vo2max <= 100),
    frr FLOAT NOT NULL CHECK (frr >= 0 AND frr <= 100),
    acs FLOAT NOT NULL CHECK (acs >= 0 AND acs <= 100),
    bos FLOAT NOT NULL CHECK (bos >= 0 AND bos <= 10),
    recorded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_overview_metrics_wrestler_id ON public.overview_metrics(wrestler_id);

-- Overview Series Table
CREATE TABLE IF NOT EXISTS public.overview_series (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    wrestler_id VARCHAR(36) NOT NULL REFERENCES public.wrestlers(id) ON DELETE CASCADE,
    label VARCHAR(100) NOT NULL,
    value FLOAT NOT NULL CHECK (value >= 0 AND value <= 100),
    recorded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_overview_series_wrestler_recorded ON public.overview_series(wrestler_id, recorded_at);

-- Body Composition Metrics Table (new API)
CREATE TABLE IF NOT EXISTS public.body_composition_metrics (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    wrestler_id VARCHAR(36) NOT NULL REFERENCES public.wrestlers(id) ON DELETE CASCADE,
    weight FLOAT NOT NULL CHECK (weight >= 30 AND weight <= 200),
    body_fat_percent FLOAT NOT NULL CHECK (body_fat_percent >= 0 AND body_fat_percent <= 50),
    muscle_mass FLOAT NOT NULL CHECK (muscle_mass >= 20 AND muscle_mass <= 150),
    bmr FLOAT NOT NULL CHECK (bmr >= 1000 AND bmr <= 5000),
    power_to_weight FLOAT NOT NULL CHECK (power_to_weight >= 0 AND power_to_weight <= 5),
    intracellular_water FLOAT CHECK (intracellular_water >= 0 AND intracellular_water <= 100),
    extracellular_water FLOAT CHECK (extracellular_water >= 0 AND extracellular_water <= 100),
    visceral_fat_level FLOAT CHECK (visceral_fat_level >= 0 AND visceral_fat_level <= 30),
    phase_angle FLOAT CHECK (phase_angle >= 0 AND phase_angle <= 15),
    recorded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_body_composition_metrics_wrestler_id ON public.body_composition_metrics(wrestler_id);

-- Body Composition Series Table (new API)
CREATE TABLE IF NOT EXISTS public.body_composition_series (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    wrestler_id VARCHAR(36) NOT NULL REFERENCES public.wrestlers(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    value FLOAT NOT NULL,
    recorded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_body_composition_series_wrestler_recorded ON public.body_composition_series(wrestler_id, recorded_at);

-- Bloodwork Metrics Table
CREATE TABLE IF NOT EXISTS public.bloodwork_metrics (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    wrestler_id VARCHAR(36) NOT NULL REFERENCES public.wrestlers(id) ON DELETE CASCADE,
    hemoglobin FLOAT NOT NULL CHECK (hemoglobin >= 8 AND hemoglobin <= 25),
    hematocrit FLOAT NOT NULL CHECK (hematocrit >= 20 AND hematocrit <= 70),
    testosterone FLOAT NOT NULL CHECK (testosterone >= 100 AND testosterone <= 1500),
    status VARCHAR(50) NOT NULL DEFAULT 'normal' CHECK (status IN ('optimal', 'normal', 'attention')),
    last_test_date DATE NOT NULL DEFAULT CURRENT_DATE,
    recorded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_bloodwork_metrics_wrestler_id ON public.bloodwork_metrics(wrestler_id);

-- Bloodwork Series Table
CREATE TABLE IF NOT EXISTS public.bloodwork_series (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    wrestler_id VARCHAR(36) NOT NULL REFERENCES public.wrestlers(id) ON DELETE CASCADE,
    panel VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    value FLOAT NOT NULL,
    recorded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_bloodwork_series_wrestler_recorded ON public.bloodwork_series(wrestler_id, recorded_at);

-- Recovery Metrics Table
CREATE TABLE IF NOT EXISTS public.recovery_metrics (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    wrestler_id VARCHAR(36) NOT NULL REFERENCES public.wrestlers(id) ON DELETE CASCADE,
    sleep_quality FLOAT NOT NULL CHECK (sleep_quality >= 0 AND sleep_quality <= 100),
    hrv_score FLOAT NOT NULL CHECK (hrv_score >= 0 AND hrv_score <= 200),
    fatigue_level FLOAT NOT NULL CHECK (fatigue_level >= 0 AND fatigue_level <= 100),
    hydration_level FLOAT NOT NULL CHECK (hydration_level >= 0 AND hydration_level <= 100),
    readiness_score FLOAT NOT NULL CHECK (readiness_score >= 0 AND readiness_score <= 100),
    recorded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_recovery_metrics_wrestler_id ON public.recovery_metrics(wrestler_id);

-- Recovery Series Table
CREATE TABLE IF NOT EXISTS public.recovery_series (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    wrestler_id VARCHAR(36) NOT NULL REFERENCES public.wrestlers(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    value FLOAT NOT NULL,
    recorded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_recovery_series_wrestler_recorded ON public.recovery_series(wrestler_id, recorded_at);

-- Supplements Metrics Table
CREATE TABLE IF NOT EXISTS public.supplements_metrics (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    wrestler_id VARCHAR(36) NOT NULL REFERENCES public.wrestlers(id) ON DELETE CASCADE,
    adherence_rate FLOAT NOT NULL CHECK (adherence_rate >= 0 AND adherence_rate <= 100),
    monthly_progress VARCHAR(20) NOT NULL DEFAULT '0%',
    performance_corr FLOAT NOT NULL CHECK (performance_corr >= -1 AND performance_corr <= 1),
    total_supplements INTEGER NOT NULL CHECK (total_supplements >= 0 AND total_supplements <= 50),
    creatine_daily_grams FLOAT NOT NULL CHECK (creatine_daily_grams >= 0 AND creatine_daily_grams <= 20),
    protein_daily_grams FLOAT NOT NULL CHECK (protein_daily_grams >= 0 AND protein_daily_grams <= 500),
    hydration_liters FLOAT NOT NULL CHECK (hydration_liters >= 0 AND hydration_liters <= 10),
    recorded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_supplements_metrics_wrestler_id ON public.supplements_metrics(wrestler_id);

-- Supplements Series Table
CREATE TABLE IF NOT EXISTS public.supplements_series (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    wrestler_id VARCHAR(36) NOT NULL REFERENCES public.wrestlers(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    value FLOAT NOT NULL,
    recorded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_supplements_series_wrestler_recorded ON public.supplements_series(wrestler_id, recorded_at);

-- Performance Metrics Table
CREATE TABLE IF NOT EXISTS public.performance_metrics (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    wrestler_id VARCHAR(36) NOT NULL REFERENCES public.wrestlers(id) ON DELETE CASCADE,
    bench_max FLOAT NOT NULL CHECK (bench_max >= 0 AND bench_max <= 1000),
    squat_max FLOAT NOT NULL CHECK (squat_max >= 0 AND squat_max <= 1000),
    deadlift_max FLOAT NOT NULL CHECK (deadlift_max >= 0 AND deadlift_max <= 1000),
    vo2max FLOAT NOT NULL CHECK (vo2max >= 0 AND vo2max <= 100),
    body_fat_percent FLOAT NOT NULL CHECK (body_fat_percent >= 0 AND body_fat_percent <= 50),
    performance_score FLOAT NOT NULL CHECK (performance_score >= 0 AND performance_score <= 100),
    recorded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_performance_metrics_wrestler_id ON public.performance_metrics(wrestler_id);

-- Performance Series Table
CREATE TABLE IF NOT EXISTS public.performance_series (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    wrestler_id VARCHAR(36) NOT NULL REFERENCES public.wrestlers(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    value FLOAT NOT NULL,
    recorded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_performance_series_wrestler_recorded ON public.performance_series(wrestler_id, recorded_at);

-- Training Programs Table
CREATE TABLE IF NOT EXISTS public.training_programs (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    wrestler_id VARCHAR(36) NOT NULL REFERENCES public.wrestlers(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    title VARCHAR(255),
    focus VARCHAR(255),
    readiness INTEGER CHECK (readiness >= 1 AND readiness <= 10),
    session_rpe INTEGER CHECK (session_rpe >= 1 AND session_rpe <= 10),
    bodyweight FLOAT CHECK (bodyweight >= 30 AND bodyweight <= 200),
    hydration FLOAT CHECK (hydration >= 0 AND hydration <= 10),
    notes TEXT,
    nutrition TEXT,
    recovery TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_training_programs_wrestler_id ON public.training_programs(wrestler_id);

-- Training Program Blocks Table
CREATE TABLE IF NOT EXISTS public.training_program_blocks (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    program_id VARCHAR(36) NOT NULL REFERENCES public.training_programs(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    sets INTEGER NOT NULL CHECK (sets >= 1 AND sets <= 20),
    reps VARCHAR(50) NOT NULL,
    load FLOAT CHECK (load >= 0),
    notes VARCHAR(500)
);

CREATE INDEX IF NOT EXISTS ix_training_program_blocks_program_id ON public.training_program_blocks(program_id);

-- Training Program AI Recommendations Table
CREATE TABLE IF NOT EXISTS public.training_program_ai_recommendations (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    program_id VARCHAR(36) NOT NULL REFERENCES public.training_programs(id) ON DELETE CASCADE,
    recommendation TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_training_program_ai_recommendations_program_id ON public.training_program_ai_recommendations(program_id);

-- AI Chart Insights Table
CREATE TABLE IF NOT EXISTS public.ai_chart_insights (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    wrestler_id VARCHAR(36) NOT NULL REFERENCES public.wrestlers(id) ON DELETE CASCADE,
    chart_id VARCHAR(100) NOT NULL,
    input_hash VARCHAR(64) NOT NULL,
    summary TEXT NOT NULL,
    patterns_json TEXT,
    recommendations_json TEXT,
    warnings_json TEXT,
    anomalies_json TEXT,
    confidence FLOAT CHECK (confidence >= 0 AND confidence <= 1),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    CONSTRAINT uq_ai_insight_hash UNIQUE (wrestler_id, chart_id, input_hash)
);

CREATE INDEX IF NOT EXISTS ix_ai_chart_insights_wrestler_id ON public.ai_chart_insights(wrestler_id);
CREATE INDEX IF NOT EXISTS ix_ai_chart_insights_input_hash ON public.ai_chart_insights(input_hash);

-- Section Scores Table
CREATE TABLE IF NOT EXISTS public.section_scores (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    wrestler_id VARCHAR(36) NOT NULL REFERENCES public.wrestlers(id) ON DELETE CASCADE,
    section_key VARCHAR(50) NOT NULL,
    score FLOAT NOT NULL CHECK (score >= 0 AND score <= 100),
    grade VARCHAR(20) NOT NULL DEFAULT 'good' CHECK (grade IN ('good', 'warning', 'bad')),
    recorded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_section_scores_wrestler_section_recorded ON public.section_scores(wrestler_id, section_key, recorded_at);

-- Score Drivers Table
CREATE TABLE IF NOT EXISTS public.score_drivers (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    section_score_id VARCHAR(36) NOT NULL REFERENCES public.section_scores(id) ON DELETE CASCADE,
    metric_name VARCHAR(100) NOT NULL,
    impact VARCHAR(10) NOT NULL,
    weight FLOAT NOT NULL CHECK (weight >= 0 AND weight <= 1)
);

CREATE INDEX IF NOT EXISTS ix_score_drivers_section_score_id ON public.score_drivers(section_score_id);

-- ============================================================================
-- SECTION 3: SAMPLE INSERT STATEMENTS (For Reference)
-- ============================================================================
-- These are examples showing how to safely insert data into the tables.
-- Use ON CONFLICT clauses to handle duplicate primary keys during imports.

-- Example: Insert athlete
-- INSERT INTO public.athlete (id, athlete_name, field, name)
-- VALUES (1, 'حسن یزدانی', 'freestyle', 'Hassan Yazdani')
-- ON CONFLICT (id) DO UPDATE SET 
--     athlete_name = EXCLUDED.athlete_name,
--     field = EXCLUDED.field,
--     name = EXCLUDED.name;

-- Example: Insert session_time
-- INSERT INTO public.session_time (session_id, athlete_id, miladi_date, shamsi_date, start_time, test_category, athlete_name)
-- VALUES (1001, 1, '2025-01-15', '1403-10-26', '09:30', 'body_composition', 'حسن یزدانی')
-- ON CONFLICT (session_id) DO UPDATE SET
--     miladi_date = EXCLUDED.miladi_date,
--     shamsi_date = EXCLUDED.shamsi_date,
--     start_time = EXCLUDED.start_time,
--     test_category = EXCLUDED.test_category;

-- Example: Insert metric
-- INSERT INTO public.metric (id, metric_name, metric_method, category)
-- VALUES (1, 'Weight', 'InBody', 'body_composition')
-- ON CONFLICT (id) DO UPDATE SET
--     metric_name = EXCLUDED.metric_name,
--     metric_method = EXCLUDED.metric_method,
--     category = EXCLUDED.category;

-- ============================================================================
-- SECTION 4: USEFUL VIEWS (Optional)
-- ============================================================================
-- These views simplify common queries by joining measurement data with session dates.

-- View: Body Composition FS with Session Date
CREATE OR REPLACE VIEW public.v_body_composition_fs_with_date AS
SELECT 
    bc.id,
    bc.session_id,
    bc.athlete_name,
    bc.metric_name,
    bc.nvalue,
    bc.tvalue,
    st.miladi_date AS session_date,
    st.shamsi_date AS session_date_shamsi,
    st.test_category
FROM public.body_composition_fs bc
LEFT JOIN public.session_time st ON bc.session_id::bigint = st.session_id;

-- View: Body Composition GR with Session Date
CREATE OR REPLACE VIEW public.v_body_composition_gr_with_date AS
SELECT 
    bc.id,
    bc.session_id,
    bc.athlete_name,
    bc.metric_name,
    bc.nvalue,
    bc.tvalue,
    st.miladi_date AS session_date,
    st.shamsi_date AS session_date_shamsi,
    st.test_category
FROM public.body_composition_gr bc
LEFT JOIN public.session_time st ON bc.session_id::bigint = st.session_id;

-- View: Chestbelt HR GR with Session Date
CREATE OR REPLACE VIEW public.v_chestbelt_hr_gr_with_date AS
SELECT 
    ch.id,
    ch.session_id,
    ch.athlete_name,
    ch.metric_name,
    ch.nvalue,
    ch.tvalue,
    st.miladi_date AS session_date,
    st.shamsi_date AS session_date_shamsi,
    st.test_category
FROM public.chestbelt_hr_gr ch
LEFT JOIN public.session_time st ON ch.session_id::bigint = st.session_id;

-- View: Fitness FS with Session Date
CREATE OR REPLACE VIEW public.v_fitness_fs_with_date AS
SELECT 
    f.id,
    f.session_id,
    f.athlete_name,
    f.metric_name,
    f.metric_method,
    f.value,
    st.miladi_date AS session_date,
    st.shamsi_date AS session_date_shamsi,
    st.test_category
FROM public.fitness_fs f
LEFT JOIN public.session_time st ON f.session_id::bigint = st.session_id;

-- View: Urion Analysis GR with Session Date
CREATE OR REPLACE VIEW public.v_urion_analysis_gr_with_date AS
SELECT 
    u.id,
    u.session_id,
    u.athlete_name,
    u.metric_name,
    u.metric_method,
    u.value,
    st.miladi_date AS session_date,
    st.shamsi_date AS session_date_shamsi,
    st.test_category
FROM public.urion_analysis_gr u
LEFT JOIN public.session_time st ON u.session_id::bigint = st.session_id;
