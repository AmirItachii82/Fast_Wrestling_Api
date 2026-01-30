# API Full Usage Documentation

Complete usage documentation for all Wrestling Dashboard database APIs.

## Base URL

```
http://localhost/api/{table_name}
```

## Common Features

All APIs share the following behavior:

- **Default Behavior**: Returns all rows from the table
- **Filtering**: Filter on any column using query parameters
- **Multiple Filters**: Combine multiple filters with `&` (AND logic)

### Filter Syntax

```
GET /api/{table_name}?column1=value1&column2=value2
```

---

## Legacy Fittechno APIs

### GET /api/athlete

Retrieve athlete records from the legacy Fittechno database.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Filter by athlete ID |
| `athlete_name` | string | Filter by athlete name |
| `field` | string | Filter by wrestling style (freestyle/greco-roman) |
| `name` | string | Filter by English name |
| `created_at` | datetime | Filter by creation date |

**Example Request:**

```bash
# Get all athletes
GET /api/athlete

# Filter by wrestling style
GET /api/athlete?field=freestyle

# Filter by name
GET /api/athlete?athlete_name=حسن یزدانی
```

**Example Response:**

```json
[
  {
    "id": 1,
    "athlete_name": "حسن یزدانی",
    "field": "freestyle",
    "name": "Hassan Yazdani",
    "created_at": "2025-01-15T09:30:00"
  }
]
```

---

### GET /api/session_time

Retrieve session time records linking sessions to dates.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `session_id` | integer | Filter by session ID |
| `athlete_id` | integer | Filter by athlete ID |
| `miladi_date` | string | Filter by Gregorian date |
| `shamsi_date` | string | Filter by Persian/Shamsi date |
| `start_time` | string | Filter by start time |
| `test_category` | string | Filter by test category |
| `athlete_name` | string | Filter by athlete name |
| `created_at` | datetime | Filter by creation date |

**Example Request:**

```bash
# Get all sessions
GET /api/session_time

# Filter by athlete
GET /api/session_time?athlete_id=1

# Filter by date and category
GET /api/session_time?miladi_date=2025-01-15&test_category=body_composition
```

**Example Response:**

```json
[
  {
    "session_id": 1001,
    "athlete_id": 1,
    "miladi_date": "2025-01-15",
    "shamsi_date": "1403-10-26",
    "start_time": "09:30",
    "test_category": "body_composition",
    "created_at": "2025-01-15T09:30:00",
    "athlete_name": "حسن یزدانی"
  }
]
```

---

### GET /api/metric

Retrieve metric definitions.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Filter by metric ID |
| `metric_name` | string | Filter by metric name |
| `metric_method` | string | Filter by measurement method |
| `category` | string | Filter by category |

**Example Request:**

```bash
# Get all metrics
GET /api/metric

# Filter by category
GET /api/metric?category=body_composition

# Filter by method
GET /api/metric?metric_method=InBody
```

**Example Response:**

```json
[
  {
    "id": 1,
    "metric_name": "Weight",
    "metric_method": "InBody",
    "category": "body_composition"
  }
]
```

---

### GET /api/body_composition_fs

Retrieve freestyle wrestling body composition measurements.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Filter by record ID |
| `session_id` | string | Filter by session ID |
| `athlete_name` | string | Filter by athlete name |
| `metric_name` | string | Filter by metric name |
| `nvalue` | float | Filter by numeric value |
| `tvalue` | string | Filter by text value |

**Example Request:**

```bash
# Get all freestyle body composition records
GET /api/body_composition_fs

# Filter by athlete
GET /api/body_composition_fs?athlete_name=حسن یزدانی

# Filter by metric and athlete
GET /api/body_composition_fs?athlete_name=حسن یزدانی&metric_name=Weight
```

**Example Response:**

```json
[
  {
    "id": 1,
    "session_id": "1001",
    "athlete_name": "حسن یزدانی",
    "metric_name": "Weight",
    "nvalue": 86.5,
    "tvalue": null
  }
]
```

---

### GET /api/body_composition_gr

Retrieve Greco-Roman wrestling body composition measurements.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Filter by record ID |
| `session_id` | string | Filter by session ID |
| `athlete_name` | string | Filter by athlete name |
| `metric_name` | string | Filter by metric name |
| `nvalue` | float | Filter by numeric value |
| `tvalue` | string | Filter by text value |

**Example Request:**

```bash
# Get all Greco-Roman body composition records
GET /api/body_composition_gr

# Filter by athlete
GET /api/body_composition_gr?athlete_name=محمد کریمی
```

**Example Response:**

```json
[
  {
    "id": 1,
    "session_id": "1002",
    "athlete_name": "محمد کریمی",
    "metric_name": "Body Fat %",
    "nvalue": 12.5,
    "tvalue": null
  }
]
```

---

### GET /api/chestbelt_hr_gr

Retrieve Greco-Roman chestbelt heart rate measurements.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Filter by record ID |
| `session_id` | string | Filter by session ID |
| `athlete_name` | string | Filter by athlete name |
| `metric_name` | string | Filter by metric name |
| `nvalue` | float | Filter by numeric value |
| `tvalue` | string | Filter by text value |

**Example Request:**

```bash
# Get all chestbelt heart rate records
GET /api/chestbelt_hr_gr

# Filter by session
GET /api/chestbelt_hr_gr?session_id=1001

# Filter by metric
GET /api/chestbelt_hr_gr?metric_name=MaxHR
```

**Example Response:**

```json
[
  {
    "id": 1,
    "session_id": "1001",
    "athlete_name": "حسن یزدانی",
    "metric_name": "MaxHR",
    "nvalue": 185.0,
    "tvalue": null
  }
]
```

---

### GET /api/fitness_fs

Retrieve freestyle wrestling fitness measurements.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Filter by record ID |
| `session_id` | string | Filter by session ID |
| `athlete_name` | string | Filter by athlete name |
| `metric_name` | string | Filter by metric name |
| `metric_method` | string | Filter by measurement method |
| `value` | float | Filter by value |

**Example Request:**

```bash
# Get all fitness records
GET /api/fitness_fs

# Filter by metric name
GET /api/fitness_fs?metric_name=VO2Max

# Filter by athlete and metric
GET /api/fitness_fs?athlete_name=حسن یزدانی&metric_name=VO2Max
```

**Example Response:**

```json
[
  {
    "id": 1,
    "session_id": "1001",
    "athlete_name": "حسن یزدانی",
    "metric_name": "VO2Max",
    "metric_method": "Treadmill",
    "value": 55.5
  }
]
```

---

### GET /api/urion_analysis_gr

Retrieve Greco-Roman urion analysis measurements.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Filter by record ID |
| `session_id` | string | Filter by session ID |
| `athlete_name` | string | Filter by athlete name |
| `metric_name` | string | Filter by metric name |
| `metric_method` | string | Filter by measurement method |
| `value` | float | Filter by value |

**Example Request:**

```bash
# Get all urion analysis records
GET /api/urion_analysis_gr

# Filter by athlete
GET /api/urion_analysis_gr?athlete_name=حسن یزدانی
```

**Example Response:**

```json
[
  {
    "id": 1,
    "session_id": "1001",
    "athlete_name": "حسن یزدانی",
    "metric_name": "pH",
    "metric_method": "Urion",
    "value": 6.5
  }
]
```

---

## Modern API Tables

### GET /api/teams

Retrieve team records.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Filter by team ID (UUID) |
| `name` | string | Filter by team name |
| `created_at` | datetime | Filter by creation date |
| `updated_at` | datetime | Filter by update date |

**Example Request:**

```bash
# Get all teams
GET /api/teams

# Filter by name
GET /api/teams?name=Team Iran
```

**Example Response:**

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Team Iran",
    "created_at": "2025-01-15T09:00:00",
    "updated_at": "2025-01-15T09:00:00"
  }
]
```

---

### GET /api/wrestlers

Retrieve wrestler profiles and details.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Filter by wrestler ID (UUID) |
| `team_id` | string | Filter by team ID |
| `name_fa` | string | Filter by Persian name |
| `name_en` | string | Filter by English name |
| `weight_class` | integer | Filter by weight class (50-150 kg) |
| `image_url` | string | Filter by image URL |
| `status` | string | Filter by status (competition_ready/normal/attention) |
| `created_at` | datetime | Filter by creation date |
| `updated_at` | datetime | Filter by update date |

**Example Request:**

```bash
# Get all wrestlers
GET /api/wrestlers

# Filter by weight class
GET /api/wrestlers?weight_class=86

# Filter by status
GET /api/wrestlers?status=competition_ready

# Filter by team and weight
GET /api/wrestlers?team_id=550e8400-e29b-41d4-a716-446655440000&weight_class=86
```

**Example Response:**

```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "team_id": "550e8400-e29b-41d4-a716-446655440000",
    "name_fa": "حسن یزدانی",
    "name_en": "Hassan Yazdani",
    "weight_class": 86,
    "image_url": "/athletes/hassan.jpg",
    "status": "competition_ready",
    "created_at": "2025-01-15T09:00:00",
    "updated_at": "2025-01-15T09:00:00"
  }
]
```

---

### GET /api/api_users

Retrieve API user accounts.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Filter by user ID (UUID) |
| `email` | string | Filter by email |
| `name` | string | Filter by name |
| `role` | string | Filter by role (admin/coach/athlete) |
| `wrestler_id` | string | Filter by linked wrestler ID |
| `team_id` | string | Filter by linked team ID |
| `created_at` | datetime | Filter by creation date |
| `updated_at` | datetime | Filter by update date |

**Example Request:**

```bash
# Get all users
GET /api/api_users

# Filter by role
GET /api/api_users?role=coach

# Filter by team
GET /api/api_users?team_id=550e8400-e29b-41d4-a716-446655440000
```

**Example Response:**

```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "email": "coach@wrestling.com",
    "password_hash": "[HIDDEN]",
    "name": "Coach Ali",
    "role": "coach",
    "wrestler_id": null,
    "team_id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2025-01-15T09:00:00",
    "updated_at": "2025-01-15T09:00:00"
  }
]
```

---

### GET /api/token_blacklist

Retrieve blacklisted JWT tokens.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Filter by record ID (UUID) |
| `token_jti` | string | Filter by token JTI |
| `expires_at` | datetime | Filter by expiration date |
| `created_at` | datetime | Filter by creation date |

**Example Request:**

```bash
# Get all blacklisted tokens
GET /api/token_blacklist
```

**Example Response:**

```json
[
  {
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "token_jti": "abc123xyz",
    "expires_at": "2025-01-20T12:00:00",
    "created_at": "2025-01-15T10:00:00"
  }
]
```

---

### GET /api/overview_metrics

Retrieve wrestler overview metrics.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Filter by record ID (UUID) |
| `wrestler_id` | string | Filter by wrestler ID |
| `overall_score` | float | Filter by overall score (0-100) |
| `msi` | float | Filter by MSI (0-100) |
| `mes` | float | Filter by MES (0-100) |
| `api` | float | Filter by API (0-1000) |
| `vo2max` | float | Filter by VO2max (0-100) |
| `frr` | float | Filter by FRR (0-100) |
| `acs` | float | Filter by ACS (0-100) |
| `bos` | float | Filter by BOS (0-10) |
| `recorded_at` | datetime | Filter by recorded date |

**Example Request:**

```bash
# Get all overview metrics
GET /api/overview_metrics

# Filter by wrestler
GET /api/overview_metrics?wrestler_id=660e8400-e29b-41d4-a716-446655440001

# Filter by high overall score
GET /api/overview_metrics?overall_score=90
```

**Example Response:**

```json
[
  {
    "id": "990e8400-e29b-41d4-a716-446655440004",
    "wrestler_id": "660e8400-e29b-41d4-a716-446655440001",
    "overall_score": 86.0,
    "msi": 92.0,
    "mes": 78.0,
    "api": 420.0,
    "vo2max": 55.0,
    "frr": 84.0,
    "acs": 72.0,
    "bos": 4.0,
    "recorded_at": "2025-01-15T09:00:00"
  }
]
```

---

### GET /api/overview_series

Retrieve wrestler overview time series data.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Filter by record ID (UUID) |
| `wrestler_id` | string | Filter by wrestler ID |
| `label` | string | Filter by label |
| `value` | float | Filter by value (0-100) |
| `recorded_at` | datetime | Filter by recorded date |

**Example Request:**

```bash
# Get all overview series data
GET /api/overview_series

# Filter by wrestler
GET /api/overview_series?wrestler_id=660e8400-e29b-41d4-a716-446655440001
```

**Example Response:**

```json
[
  {
    "id": "aa0e8400-e29b-41d4-a716-446655440005",
    "wrestler_id": "660e8400-e29b-41d4-a716-446655440001",
    "label": "Week 1",
    "value": 85.0,
    "recorded_at": "2025-01-08T09:00:00"
  }
]
```

---

### GET /api/body_composition_metrics

Retrieve wrestler body composition metrics.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Filter by record ID (UUID) |
| `wrestler_id` | string | Filter by wrestler ID |
| `weight` | float | Filter by weight (30-200 kg) |
| `body_fat_percent` | float | Filter by body fat percentage (0-50) |
| `muscle_mass` | float | Filter by muscle mass (20-150 kg) |
| `bmr` | float | Filter by BMR (1000-5000) |
| `power_to_weight` | float | Filter by power to weight ratio (0-5) |
| `intracellular_water` | float | Filter by intracellular water (0-100) |
| `extracellular_water` | float | Filter by extracellular water (0-100) |
| `visceral_fat_level` | float | Filter by visceral fat level (0-30) |
| `phase_angle` | float | Filter by phase angle (0-15) |
| `recorded_at` | datetime | Filter by recorded date |

**Example Request:**

```bash
# Get all body composition metrics
GET /api/body_composition_metrics

# Filter by wrestler
GET /api/body_composition_metrics?wrestler_id=660e8400-e29b-41d4-a716-446655440001

# Filter by weight range
GET /api/body_composition_metrics?weight=86
```

**Example Response:**

```json
[
  {
    "id": "bb0e8400-e29b-41d4-a716-446655440006",
    "wrestler_id": "660e8400-e29b-41d4-a716-446655440001",
    "weight": 86.5,
    "body_fat_percent": 12.5,
    "muscle_mass": 72.0,
    "bmr": 1850.0,
    "power_to_weight": 3.2,
    "intracellular_water": 55.0,
    "extracellular_water": 40.0,
    "visceral_fat_level": 5.0,
    "phase_angle": 7.5,
    "recorded_at": "2025-01-15T09:00:00"
  }
]
```

---

### GET /api/body_composition_series

Retrieve wrestler body composition time series data.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Filter by record ID (UUID) |
| `wrestler_id` | string | Filter by wrestler ID |
| `metric_name` | string | Filter by metric name |
| `value` | float | Filter by value |
| `recorded_at` | datetime | Filter by recorded date |

**Example Request:**

```bash
# Get all body composition series data
GET /api/body_composition_series

# Filter by wrestler and metric
GET /api/body_composition_series?wrestler_id=660e8400-e29b-41d4-a716-446655440001&metric_name=weight
```

**Example Response:**

```json
[
  {
    "id": "cc0e8400-e29b-41d4-a716-446655440007",
    "wrestler_id": "660e8400-e29b-41d4-a716-446655440001",
    "metric_name": "weight",
    "value": 86.5,
    "recorded_at": "2025-01-15T09:00:00"
  }
]
```

---

### GET /api/bloodwork_metrics

Retrieve wrestler bloodwork metrics.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Filter by record ID (UUID) |
| `wrestler_id` | string | Filter by wrestler ID |
| `hemoglobin` | float | Filter by hemoglobin (8-25) |
| `hematocrit` | float | Filter by hematocrit (20-70) |
| `testosterone` | float | Filter by testosterone (100-1500) |
| `status` | string | Filter by status (optimal/normal/attention) |
| `last_test_date` | date | Filter by last test date |
| `recorded_at` | datetime | Filter by recorded date |

**Example Request:**

```bash
# Get all bloodwork metrics
GET /api/bloodwork_metrics

# Filter by wrestler
GET /api/bloodwork_metrics?wrestler_id=660e8400-e29b-41d4-a716-446655440001

# Filter by status
GET /api/bloodwork_metrics?status=optimal
```

**Example Response:**

```json
[
  {
    "id": "dd0e8400-e29b-41d4-a716-446655440008",
    "wrestler_id": "660e8400-e29b-41d4-a716-446655440001",
    "hemoglobin": 15.5,
    "hematocrit": 45.0,
    "testosterone": 650.0,
    "status": "optimal",
    "last_test_date": "2025-01-10",
    "recorded_at": "2025-01-15T09:00:00"
  }
]
```

---

### GET /api/bloodwork_series

Retrieve wrestler bloodwork time series data.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Filter by record ID (UUID) |
| `wrestler_id` | string | Filter by wrestler ID |
| `panel` | string | Filter by panel |
| `metric_name` | string | Filter by metric name |
| `value` | float | Filter by value |
| `recorded_at` | datetime | Filter by recorded date |

**Example Request:**

```bash
# Get all bloodwork series data
GET /api/bloodwork_series

# Filter by wrestler and panel
GET /api/bloodwork_series?wrestler_id=660e8400-e29b-41d4-a716-446655440001&panel=cbc
```

**Example Response:**

```json
[
  {
    "id": "ee0e8400-e29b-41d4-a716-446655440009",
    "wrestler_id": "660e8400-e29b-41d4-a716-446655440001",
    "panel": "cbc",
    "metric_name": "hemoglobin",
    "value": 15.5,
    "recorded_at": "2025-01-15T09:00:00"
  }
]
```

---

### GET /api/recovery_metrics

Retrieve wrestler recovery metrics.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Filter by record ID (UUID) |
| `wrestler_id` | string | Filter by wrestler ID |
| `sleep_quality` | float | Filter by sleep quality (0-100) |
| `hrv_score` | float | Filter by HRV score (0-200) |
| `fatigue_level` | float | Filter by fatigue level (0-100) |
| `hydration_level` | float | Filter by hydration level (0-100) |
| `readiness_score` | float | Filter by readiness score (0-100) |
| `recorded_at` | datetime | Filter by recorded date |

**Example Request:**

```bash
# Get all recovery metrics
GET /api/recovery_metrics

# Filter by wrestler
GET /api/recovery_metrics?wrestler_id=660e8400-e29b-41d4-a716-446655440001
```

**Example Response:**

```json
[
  {
    "id": "ff0e8400-e29b-41d4-a716-446655440010",
    "wrestler_id": "660e8400-e29b-41d4-a716-446655440001",
    "sleep_quality": 85.0,
    "hrv_score": 65.0,
    "fatigue_level": 25.0,
    "hydration_level": 80.0,
    "readiness_score": 90.0,
    "recorded_at": "2025-01-15T09:00:00"
  }
]
```

---

### GET /api/recovery_series

Retrieve wrestler recovery time series data.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Filter by record ID (UUID) |
| `wrestler_id` | string | Filter by wrestler ID |
| `metric_name` | string | Filter by metric name |
| `value` | float | Filter by value |
| `recorded_at` | datetime | Filter by recorded date |

**Example Request:**

```bash
# Get all recovery series data
GET /api/recovery_series

# Filter by wrestler
GET /api/recovery_series?wrestler_id=660e8400-e29b-41d4-a716-446655440001
```

**Example Response:**

```json
[
  {
    "id": "110e8400-e29b-41d4-a716-446655440011",
    "wrestler_id": "660e8400-e29b-41d4-a716-446655440001",
    "metric_name": "sleep_quality",
    "value": 85.0,
    "recorded_at": "2025-01-15T09:00:00"
  }
]
```

---

### GET /api/supplements_metrics

Retrieve wrestler supplements adherence and intake metrics.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Filter by record ID (UUID) |
| `wrestler_id` | string | Filter by wrestler ID |
| `adherence_rate` | float | Filter by adherence rate (0-100) |
| `monthly_progress` | string | Filter by monthly progress |
| `performance_corr` | float | Filter by performance correlation (-1 to 1) |
| `total_supplements` | integer | Filter by total supplements (0-50) |
| `creatine_daily_grams` | float | Filter by creatine daily intake (0-20) |
| `protein_daily_grams` | float | Filter by protein daily intake (0-500) |
| `hydration_liters` | float | Filter by hydration (0-10) |
| `recorded_at` | datetime | Filter by recorded date |

**Example Request:**

```bash
# Get all supplements metrics
GET /api/supplements_metrics

# Filter by wrestler
GET /api/supplements_metrics?wrestler_id=660e8400-e29b-41d4-a716-446655440001
```

**Example Response:**

```json
[
  {
    "id": "220e8400-e29b-41d4-a716-446655440012",
    "wrestler_id": "660e8400-e29b-41d4-a716-446655440001",
    "adherence_rate": 92.0,
    "monthly_progress": "+5%",
    "performance_corr": 0.75,
    "total_supplements": 5,
    "creatine_daily_grams": 5.0,
    "protein_daily_grams": 150.0,
    "hydration_liters": 3.5,
    "recorded_at": "2025-01-15T09:00:00"
  }
]
```

---

### GET /api/supplements_series

Retrieve wrestler supplements time series data.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Filter by record ID (UUID) |
| `wrestler_id` | string | Filter by wrestler ID |
| `metric_name` | string | Filter by metric name |
| `value` | float | Filter by value |
| `recorded_at` | datetime | Filter by recorded date |

**Example Request:**

```bash
# Get all supplements series data
GET /api/supplements_series

# Filter by wrestler
GET /api/supplements_series?wrestler_id=660e8400-e29b-41d4-a716-446655440001
```

**Example Response:**

```json
[
  {
    "id": "330e8400-e29b-41d4-a716-446655440013",
    "wrestler_id": "660e8400-e29b-41d4-a716-446655440001",
    "metric_name": "adherence_rate",
    "value": 92.0,
    "recorded_at": "2025-01-15T09:00:00"
  }
]
```

---

### GET /api/performance_metrics

Retrieve wrestler performance metrics.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Filter by record ID (UUID) |
| `wrestler_id` | string | Filter by wrestler ID |
| `bench_max` | float | Filter by bench press max (0-1000) |
| `squat_max` | float | Filter by squat max (0-1000) |
| `deadlift_max` | float | Filter by deadlift max (0-1000) |
| `vo2max` | float | Filter by VO2max (0-100) |
| `body_fat_percent` | float | Filter by body fat percentage (0-50) |
| `performance_score` | float | Filter by performance score (0-100) |
| `recorded_at` | datetime | Filter by recorded date |

**Example Request:**

```bash
# Get all performance metrics
GET /api/performance_metrics

# Filter by wrestler
GET /api/performance_metrics?wrestler_id=660e8400-e29b-41d4-a716-446655440001
```

**Example Response:**

```json
[
  {
    "id": "440e8400-e29b-41d4-a716-446655440014",
    "wrestler_id": "660e8400-e29b-41d4-a716-446655440001",
    "bench_max": 140.0,
    "squat_max": 180.0,
    "deadlift_max": 200.0,
    "vo2max": 55.0,
    "body_fat_percent": 12.5,
    "performance_score": 88.0,
    "recorded_at": "2025-01-15T09:00:00"
  }
]
```

---

### GET /api/performance_series

Retrieve wrestler performance time series data.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Filter by record ID (UUID) |
| `wrestler_id` | string | Filter by wrestler ID |
| `metric_name` | string | Filter by metric name |
| `value` | float | Filter by value |
| `recorded_at` | datetime | Filter by recorded date |

**Example Request:**

```bash
# Get all performance series data
GET /api/performance_series

# Filter by wrestler
GET /api/performance_series?wrestler_id=660e8400-e29b-41d4-a716-446655440001
```

**Example Response:**

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440015",
    "wrestler_id": "660e8400-e29b-41d4-a716-446655440001",
    "metric_name": "bench_max",
    "value": 140.0,
    "recorded_at": "2025-01-15T09:00:00"
  }
]
```

---

### GET /api/training_programs

Retrieve wrestler training program records.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Filter by program ID (UUID) |
| `wrestler_id` | string | Filter by wrestler ID |
| `date` | date | Filter by program date |
| `title` | string | Filter by program title |
| `focus` | string | Filter by program focus |
| `readiness` | integer | Filter by readiness (1-10) |
| `session_rpe` | integer | Filter by session RPE (1-10) |
| `bodyweight` | float | Filter by bodyweight (30-200) |
| `hydration` | float | Filter by hydration (0-10) |
| `created_at` | datetime | Filter by creation date |

**Example Request:**

```bash
# Get all training programs
GET /api/training_programs

# Filter by wrestler
GET /api/training_programs?wrestler_id=660e8400-e29b-41d4-a716-446655440001

# Filter by date
GET /api/training_programs?date=2025-01-15
```

**Example Response:**

```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440016",
    "wrestler_id": "660e8400-e29b-41d4-a716-446655440001",
    "date": "2025-01-15",
    "title": "Strength Day",
    "focus": "Upper Body",
    "readiness": 8,
    "session_rpe": 7,
    "bodyweight": 86.0,
    "hydration": 3.5,
    "notes": "Good session",
    "nutrition": "High protein",
    "recovery": "Ice bath",
    "created_at": "2025-01-15T09:00:00"
  }
]
```

---

### GET /api/training_program_blocks

Retrieve training program exercise blocks.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Filter by block ID (UUID) |
| `program_id` | string | Filter by program ID |
| `name` | string | Filter by exercise name |
| `sets` | integer | Filter by number of sets (1-20) |
| `reps` | string | Filter by reps |
| `load` | float | Filter by load weight |

**Example Request:**

```bash
# Get all training program blocks
GET /api/training_program_blocks

# Filter by program
GET /api/training_program_blocks?program_id=660e8400-e29b-41d4-a716-446655440016
```

**Example Response:**

```json
[
  {
    "id": "770e8400-e29b-41d4-a716-446655440017",
    "program_id": "660e8400-e29b-41d4-a716-446655440016",
    "name": "Bench Press",
    "sets": 4,
    "reps": "8-10",
    "load": 100.0,
    "notes": "Focus on form"
  }
]
```

---

### GET /api/training_program_ai_recommendations

Retrieve AI-generated training recommendations.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Filter by recommendation ID (UUID) |
| `program_id` | string | Filter by program ID |
| `recommendation` | string | Filter by recommendation text |

**Example Request:**

```bash
# Get all AI recommendations
GET /api/training_program_ai_recommendations

# Filter by program
GET /api/training_program_ai_recommendations?program_id=660e8400-e29b-41d4-a716-446655440016
```

**Example Response:**

```json
[
  {
    "id": "880e8400-e29b-41d4-a716-446655440018",
    "program_id": "660e8400-e29b-41d4-a716-446655440016",
    "recommendation": "Consider increasing rest periods between sets for better recovery"
  }
]
```

---

### GET /api/ai_chart_insights

Retrieve AI-generated chart insights.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Filter by insight ID (UUID) |
| `wrestler_id` | string | Filter by wrestler ID |
| `chart_id` | string | Filter by chart ID |
| `input_hash` | string | Filter by input hash |
| `confidence` | float | Filter by confidence score (0-1) |
| `created_at` | datetime | Filter by creation date |

**Example Request:**

```bash
# Get all AI chart insights
GET /api/ai_chart_insights

# Filter by wrestler
GET /api/ai_chart_insights?wrestler_id=660e8400-e29b-41d4-a716-446655440001

# Filter by chart
GET /api/ai_chart_insights?chart_id=overview-radar
```

**Example Response:**

```json
[
  {
    "id": "990e8400-e29b-41d4-a716-446655440019",
    "wrestler_id": "660e8400-e29b-41d4-a716-446655440001",
    "chart_id": "overview-radar",
    "input_hash": "abc123",
    "summary": "Overall performance is excellent with strong upper body metrics",
    "patterns_json": "[\"Consistent improvement\", \"Strong recovery\"]",
    "recommendations_json": "[{\"text\": \"Continue current training\", \"priority\": \"medium\"}]",
    "warnings_json": "[]",
    "anomalies_json": "[]",
    "confidence": 0.92,
    "created_at": "2025-01-15T09:00:00"
  }
]
```

---

### GET /api/section_scores

Retrieve wrestler section scores.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Filter by score ID (UUID) |
| `wrestler_id` | string | Filter by wrestler ID |
| `section_key` | string | Filter by section key |
| `score` | float | Filter by score (0-100) |
| `grade` | string | Filter by grade (good/warning/bad) |
| `recorded_at` | datetime | Filter by recorded date |

**Example Request:**

```bash
# Get all section scores
GET /api/section_scores

# Filter by wrestler
GET /api/section_scores?wrestler_id=660e8400-e29b-41d4-a716-446655440001

# Filter by section
GET /api/section_scores?section_key=body_composition
```

**Example Response:**

```json
[
  {
    "id": "aa0e8400-e29b-41d4-a716-446655440020",
    "wrestler_id": "660e8400-e29b-41d4-a716-446655440001",
    "section_key": "body_composition",
    "score": 88.0,
    "grade": "good",
    "recorded_at": "2025-01-15T09:00:00"
  }
]
```

---

### GET /api/score_drivers

Retrieve score driver metrics.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | Filter by driver ID (UUID) |
| `section_score_id` | string | Filter by section score ID |
| `metric_name` | string | Filter by metric name |
| `impact` | string | Filter by impact |
| `weight` | float | Filter by weight (0-1) |

**Example Request:**

```bash
# Get all score drivers
GET /api/score_drivers

# Filter by section score
GET /api/score_drivers?section_score_id=aa0e8400-e29b-41d4-a716-446655440020
```

**Example Response:**

```json
[
  {
    "id": "bb0e8400-e29b-41d4-a716-446655440021",
    "section_score_id": "aa0e8400-e29b-41d4-a716-446655440020",
    "metric_name": "body_fat_percent",
    "impact": "positive",
    "weight": 0.35
  }
]
```
