# API Short Descriptions

Brief descriptions of all available APIs for the Wrestling Dashboard database.

## Base URL

```
http://localhost/api/v1
```

---

## Authentication APIs

| API Endpoint | Method | Description |
|--------------|--------|-------------|
| `/api/v1/auth/signup` | POST | Register a new user account with email, password, name, and role |
| `/api/v1/auth/login` | POST | Authenticate user and receive JWT access and refresh tokens |
| `/api/v1/auth/refresh` | POST | Refresh an expired access token using a valid refresh token |
| `/api/v1/auth/logout` | POST | Logout user by blacklisting their refresh token |

---

## Data APIs

| API Endpoint | Description |
|--------------|-------------|
| `/api/athlete` | Retrieve athlete records from the legacy Fittechno database |
| `/api/session_time` | Retrieve session time records linking sessions to dates |
| `/api/metric` | Retrieve metric definitions (names, methods, categories) |
| `/api/body_composition_fs` | Retrieve freestyle wrestling body composition measurements |
| `/api/body_composition_gr` | Retrieve Greco-Roman wrestling body composition measurements |
| `/api/chestbelt_hr_gr` | Retrieve Greco-Roman chestbelt heart rate measurements |
| `/api/fitness_fs` | Retrieve freestyle wrestling fitness measurements |
| `/api/urion_analysis_gr` | Retrieve Greco-Roman urion analysis measurements |
| `/api/teams` | Retrieve team records |
| `/api/wrestlers` | Retrieve wrestler profiles and details |
| `/api/api_users` | Retrieve API user accounts |
| `/api/token_blacklist` | Retrieve blacklisted JWT tokens |
| `/api/overview_metrics` | Retrieve wrestler overview metrics (MSI, MES, VO2max, etc.) |
| `/api/overview_series` | Retrieve wrestler overview time series data |
| `/api/body_composition_metrics` | Retrieve wrestler body composition metrics (weight, body fat, muscle mass, etc.) |
| `/api/body_composition_series` | Retrieve wrestler body composition time series data |
| `/api/bloodwork_metrics` | Retrieve wrestler bloodwork metrics (hemoglobin, hematocrit, testosterone) |
| `/api/bloodwork_series` | Retrieve wrestler bloodwork time series data |
| `/api/recovery_metrics` | Retrieve wrestler recovery metrics (sleep quality, HRV, fatigue, hydration) |
| `/api/recovery_series` | Retrieve wrestler recovery time series data |
| `/api/supplements_metrics` | Retrieve wrestler supplements adherence and intake metrics |
| `/api/supplements_series` | Retrieve wrestler supplements time series data |
| `/api/performance_metrics` | Retrieve wrestler performance metrics (bench max, squat max, deadlift max, VO2max) |
| `/api/performance_series` | Retrieve wrestler performance time series data |
| `/api/training_programs` | Retrieve wrestler training program records |
| `/api/training_program_blocks` | Retrieve training program exercise blocks |
| `/api/training_program_ai_recommendations` | Retrieve AI-generated training recommendations |
| `/api/ai_chart_insights` | Retrieve AI-generated chart insights |
| `/api/section_scores` | Retrieve wrestler section scores (grades for each metric domain) |
| `/api/score_drivers` | Retrieve score driver metrics that impact section scores |
