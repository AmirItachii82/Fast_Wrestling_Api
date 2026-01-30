# Database Import Guide

This guide explains how to set up the database schema and safely import data into the Wrestling Dashboard API database.

## Overview

The Wrestling Dashboard database consists of two categories of tables:

1. **Legacy Fittechno Tables** - Existing measurement data from the original Fittechno system
2. **New API Tables** - Modern data model for the Wrestling Dashboard frontend

## Database Schema File

The complete database schema is defined in `complete_database_schema.sql`. This file contains:

- All table definitions with `IF NOT EXISTS` clauses for safe execution
- Primary keys, foreign keys, and indexes
- Database views for joining measurement data with session dates

### Schema Location

```
/complete_database_schema.sql
```

## Setting Up the Database

### 1. Create the Database

```sql
CREATE DATABASE wrestling_dashboard;
```

### 2. Run the Schema Script

```bash
psql -d wrestling_dashboard -f complete_database_schema.sql
```

Or via psql:

```sql
\i complete_database_schema.sql
```

## Table Reference

### Legacy Tables (Fittechno)

| Table | Description | Primary Key |
|-------|-------------|-------------|
| `athlete` | Legacy athlete records | `id` (BIGINT) |
| `session_time` | Session dates and metadata | `session_id` (BIGINT) |
| `metric` | Metric definitions | `id` (BIGINT) |
| `body_composition_fs` | Freestyle body composition | `id` (BIGINT) |
| `body_composition_gr` | Greco-Roman body composition | `id` (BIGINT) |
| `chestbelt_hr_gr` | Heart rate measurements | `id` (BIGINT) |
| `fitness_fs` | Freestyle fitness data | `id` (BIGINT) |
| `urion_analysis_gr` | Urion analysis data | `id` (BIGINT) |

### New API Tables

| Table | Description | Primary Key |
|-------|-------------|-------------|
| `teams` | Team organizations | `id` (UUID) |
| `wrestlers` | Wrestler profiles | `id` (UUID) |
| `api_users` | API authentication users | `id` (UUID) |
| `overview_metrics` | Overview snapshot metrics | `id` (UUID) |
| `body_composition_metrics` | Body composition snapshots | `id` (UUID) |
| `bloodwork_metrics` | Bloodwork snapshots | `id` (UUID) |
| `recovery_metrics` | Recovery snapshots | `id` (UUID) |
| `supplements_metrics` | Supplement tracking | `id` (UUID) |
| `performance_metrics` | Performance metrics | `id` (UUID) |
| `training_programs` | Training programs | `id` (UUID) |
| `section_scores` | Section-level scores | `id` (UUID) |

## Safe Data Import

### Understanding Partial Data

The schema is designed to handle partial data imports safely:

1. **Legacy tables use BIGINT primary keys** - Your existing data uses sequential IDs
2. **New API tables use UUID primary keys** - Generated automatically
3. **Foreign keys allow NULL** - Missing related data won't break imports
4. **`IF NOT EXISTS` clauses** - Running schema multiple times is safe

### Import Legacy Data

#### Using COPY Command (Recommended for large datasets)

```sql
-- Import athletes
COPY athlete(id, athlete_name, field, name, created_at)
FROM '/path/to/athletes.csv'
WITH (FORMAT csv, HEADER true);

-- Import session times
COPY session_time(session_id, athlete_id, miladi_date, shamsi_date, start_time, test_category, athlete_name)
FROM '/path/to/sessions.csv'
WITH (FORMAT csv, HEADER true);

-- Import body composition freestyle
COPY body_composition_fs(id, session_id, athlete_name, metric_name, nvalue, tvalue)
FROM '/path/to/body_comp_fs.csv'
WITH (FORMAT csv, HEADER true);
```

#### Using INSERT with Conflict Handling

For updating existing records safely:

```sql
-- Upsert athlete
INSERT INTO athlete (id, athlete_name, field, name)
VALUES (1, 'حسن یزدانی', 'freestyle', 'Hassan Yazdani')
ON CONFLICT (id) DO UPDATE SET 
    athlete_name = EXCLUDED.athlete_name,
    field = EXCLUDED.field,
    name = EXCLUDED.name;

-- Upsert session time
INSERT INTO session_time (session_id, athlete_id, miladi_date, shamsi_date, start_time, test_category, athlete_name)
VALUES (1001, 1, '2025-01-15', '1403-10-26', '09:30', 'body_composition', 'حسن یزدانی')
ON CONFLICT (session_id) DO UPDATE SET
    miladi_date = EXCLUDED.miladi_date,
    shamsi_date = EXCLUDED.shamsi_date,
    start_time = EXCLUDED.start_time,
    test_category = EXCLUDED.test_category;
```

### Import New API Data

For new API tables, the primary key is auto-generated:

```sql
-- Insert team
INSERT INTO teams (name)
VALUES ('Iran National Team');

-- Insert wrestler (returns generated ID)
INSERT INTO wrestlers (team_id, name_fa, name_en, weight_class, status)
VALUES (
    (SELECT id FROM teams WHERE name = 'Iran National Team'),
    'حسن یزدانی',
    'Hassan Yazdani',
    86,
    'competition_ready'
)
RETURNING id;

-- Insert API user
INSERT INTO api_users (email, password_hash, name, role)
VALUES (
    'admin@wrestling.com',
    '$2b$12$...hashed_password...',
    'System Admin',
    'admin'
);
```

## Session Date Resolution

The `session_time` table is the central link between measurements and dates.

### How It Works

1. Each measurement record has a `session_id`
2. The `session_time` table maps `session_id` to dates
3. API responses automatically include session dates via JOINs

### Example Query

```sql
-- Get body composition with session dates
SELECT 
    bc.id,
    bc.session_id,
    bc.athlete_name,
    bc.metric_name,
    bc.nvalue,
    st.miladi_date AS session_date,
    st.shamsi_date AS session_date_shamsi
FROM body_composition_fs bc
LEFT JOIN session_time st ON bc.session_id::bigint = st.session_id
WHERE bc.athlete_name = 'حسن یزدانی';
```

### Pre-built Views

The schema includes views that automatically join with session dates:

```sql
-- Use the view instead of manual JOINs
SELECT * FROM v_body_composition_fs_with_date
WHERE athlete_name = 'حسن یزدانی';

-- Available views:
-- - v_body_composition_fs_with_date
-- - v_body_composition_gr_with_date
-- - v_chestbelt_hr_gr_with_date
-- - v_fitness_fs_with_date
-- - v_urion_analysis_gr_with_date
```

## Migration Considerations

### From Existing Fittechno Database

If you already have a Fittechno database:

1. **Export existing data** to CSV files
2. **Run the schema script** on your new database (safe with `IF NOT EXISTS`)
3. **Import legacy data** using COPY or INSERT
4. **Verify counts** to ensure all data was imported

### Handling Duplicate Primary Keys

If importing data that may overlap with existing records:

```sql
-- Check for existing records first
SELECT COUNT(*) FROM athlete WHERE id IN (1, 2, 3);

-- Use ON CONFLICT for safe upserts
INSERT INTO athlete (id, athlete_name, field, name)
VALUES 
    (1, 'Athlete 1', 'freestyle', 'Name 1'),
    (2, 'Athlete 2', 'greco-roman', 'Name 2')
ON CONFLICT (id) DO UPDATE SET
    athlete_name = EXCLUDED.athlete_name,
    field = EXCLUDED.field,
    name = EXCLUDED.name;
```

## Required vs Optional Fields

### Legacy Tables

| Table | Required | Optional |
|-------|----------|----------|
| `athlete` | `id`, `athlete_name` | `field`, `name`, `created_at` |
| `session_time` | `session_id` | All other fields |
| `metric` | `id`, `metric_name` | `metric_method`, `category` |
| `body_composition_fs` | `id`, `session_id`, `athlete_name`, `metric_name` | `nvalue`, `tvalue` |
| `body_composition_gr` | `id`, `session_id`, `athlete_name`, `metric_name` | `nvalue`, `tvalue` |
| `chestbelt_hr_gr` | `id`, `session_id`, `athlete_name`, `metric_name` | `nvalue`, `tvalue` |
| `fitness_fs` | `id`, `session_id`, `athlete_name`, `metric_name` | `metric_method`, `value` |
| `urion_analysis_gr` | `id`, `session_id`, `athlete_name`, `metric_name` | `metric_method`, `value` |

### New API Tables

| Table | Required | Optional |
|-------|----------|----------|
| `teams` | `name` | `id` (auto), timestamps |
| `wrestlers` | `name_fa`, `name_en`, `weight_class` | `team_id`, `image_url`, `status` |
| `api_users` | `email`, `password_hash`, `name` | `role`, `wrestler_id`, `team_id` |

## Backup and Recovery

### Create Backup

```bash
pg_dump -Fc wrestling_dashboard > backup_$(date +%Y%m%d).dump
```

### Restore Backup

```bash
pg_restore -d wrestling_dashboard backup_20250130.dump
```

### Backup Specific Tables

```bash
pg_dump -t athlete -t session_time -t body_composition_fs wrestling_dashboard > legacy_backup.sql
```

## Troubleshooting

### Foreign Key Violations

If you see foreign key errors during import:

```sql
-- Temporarily disable foreign key checks
SET session_replication_role = replica;

-- Import your data
COPY ...

-- Re-enable foreign key checks
SET session_replication_role = DEFAULT;

-- Verify data integrity manually
SELECT bc.* FROM body_composition_fs bc
LEFT JOIN session_time st ON bc.session_id::bigint = st.session_id
WHERE st.session_id IS NULL;
```

### Duplicate Key Errors

Use `ON CONFLICT` clauses or delete existing records:

```sql
-- Option 1: Update on conflict
INSERT INTO athlete (...) VALUES (...)
ON CONFLICT (id) DO UPDATE SET ...;

-- Option 2: Delete and reinsert
DELETE FROM athlete WHERE id IN (1, 2, 3);
INSERT INTO athlete (...) VALUES (...);
```

### Data Type Mismatches

The `session_id` in measurement tables is VARCHAR but INTEGER in `session_time`. Queries use casting:

```sql
-- Correct: Cast session_id to BIGINT for joining
SELECT * FROM body_composition_fs bc
JOIN session_time st ON bc.session_id::bigint = st.session_id;
```

## Support

For issues with database setup or data import:

1. Check PostgreSQL logs for detailed error messages
2. Verify database connection settings in `.env`
3. Ensure PostgreSQL version compatibility (17.x recommended)
