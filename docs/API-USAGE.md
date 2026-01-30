# API Usage Guide

This document provides detailed examples for using the Wrestling Dashboard Backend API.

## Table of Contents

- [Authentication](#authentication)
- [Wrestlers](#wrestlers)
- [Overview Metrics](#overview-metrics)
- [Body Composition](#body-composition)
- [Bloodwork](#bloodwork)
- [Recovery](#recovery)
- [Supplements](#supplements)
- [Bodybuilding Performance](#bodybuilding-performance)
- [Training Program](#training-program)
- [Calendar](#calendar)
- [Teams](#teams)
- [AI Endpoints](#ai-endpoints)
- [Scoring](#scoring)
- [Legacy Data Endpoints](#legacy-data-endpoints)
- [Error Responses](#error-responses)

---

## Authentication

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@wrestling.com",
    "password": "admin123"
  }'
```

**Response:**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIs...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "uuid",
    "name": "System Admin",
    "role": "admin"
  }
}
```

### Refresh Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refreshToken": "your-refresh-token"
  }'
```

### Logout

```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Content-Type: application/json" \
  -d '{
    "refreshToken": "your-refresh-token"
  }'
```

## Wrestlers

### List All Wrestlers

```bash
curl http://localhost:8000/api/v1/wrestlers \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "wrestlers": [
    {
      "id": "uuid",
      "nameFa": "حسن یزدانی",
      "nameEn": "Hassan Yazdani",
      "weightClass": 86,
      "imageUrl": "/athletes/hassan.jpg"
    }
  ]
}
```

### Get Wrestler Details

```bash
curl http://localhost:8000/api/v1/wrestlers/{wrestlerId} \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Overview Metrics

### Get Overview

```bash
curl http://localhost:8000/api/v1/wrestlers/{wrestlerId}/overview \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "metrics": {
    "overallScore": 86,
    "msi": 92,
    "mes": 78,
    "api": 420,
    "vo2max": 55,
    "frr": 84,
    "acs": 72,
    "bos": 4
  },
  "deltas": {
    "overallScore": 3.2,
    "msi": 1.5,
    ...
  },
  "statusLabels": {
    "overallScore": "good",
    "msi": "good",
    ...
  }
}
```

### Get Section Score

```bash
curl http://localhost:8000/api/v1/wrestlers/{wrestlerId}/overview/score \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Radar Chart Data

```bash
curl http://localhost:8000/api/v1/wrestlers/{wrestlerId}/overview/chart \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Body Composition

### Get Metrics

```bash
curl http://localhost:8000/api/v1/wrestlers/{wrestlerId}/body-composition \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Trends

```bash
curl http://localhost:8000/api/v1/wrestlers/{wrestlerId}/body-composition/trends?limit=30 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get InBody Breakdown

```bash
curl http://localhost:8000/api/v1/wrestlers/{wrestlerId}/body-composition/inbody \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Bloodwork

### Get Bloodwork Metrics

```bash
curl http://localhost:8000/api/v1/wrestlers/{wrestlerId}/bloodwork \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Panel Charts

```bash
curl http://localhost:8000/api/v1/wrestlers/{wrestlerId}/bloodwork/charts?limit=30 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Recovery

### Get Recovery Metrics

```bash
curl http://localhost:8000/api/v1/wrestlers/{wrestlerId}/recovery \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Recovery Charts

```bash
curl http://localhost:8000/api/v1/wrestlers/{wrestlerId}/recovery/charts \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Supplements

### Get Supplements Metrics

```bash
curl http://localhost:8000/api/v1/wrestlers/{wrestlerId}/supplements \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Supplements Charts

```bash
curl http://localhost:8000/api/v1/wrestlers/{wrestlerId}/supplements/charts \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Bodybuilding Performance

### Get Performance Metrics

```bash
curl http://localhost:8000/api/v1/wrestlers/{wrestlerId}/bodybuilding-performance \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Performance Charts

```bash
curl http://localhost:8000/api/v1/wrestlers/{wrestlerId}/bodybuilding-performance/charts \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Training Program

### Get Today's Program

```bash
curl http://localhost:8000/api/v1/wrestlers/{wrestlerId}/training-program \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Submit Program Update

```bash
curl -X POST http://localhost:8000/api/v1/wrestlers/{wrestlerId}/training-program \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-01-29",
    "readiness": 7,
    "sessionRPE": 7,
    "bodyweight": 86,
    "hydration": 3.0,
    "notes": "Good session",
    "exercises": [
      {
        "name": "Bench Press",
        "sets": [
          {"reps": 8, "weight": 100},
          {"reps": 8, "weight": 105}
        ]
      }
    ]
  }'
```

## Calendar

### Get Monthly Calendar

```bash
curl "http://localhost:8000/api/v1/wrestlers/{wrestlerId}/calendar?month=1&year=2025" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Teams

### Get Team Stats

```bash
curl http://localhost:8000/api/v1/teams/{teamId}/stats \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Team Athletes

```bash
curl http://localhost:8000/api/v1/teams/{teamId}/athletes \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## AI Endpoints

### Get Chart Insight

```bash
curl -X POST http://localhost:8000/api/v1/ai/chart-insight \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "wrestlerId": "wrestler-uuid",
    "chartId": "overview-radar",
    "chartData": {
      "labels": ["کمر", "سینه", "پاها"],
      "values": [92, 85, 78]
    },
    "locale": "fa-IR"
  }'
```

**Response:**
```json
{
  "summary": "تحلیل نمودار overview-radar: میانگین مقادیر 85.0 است.",
  "patterns": ["روند صعودی مشاهده شده", "نوسانات طبیعی"],
  "recommendations": [
    {"text": "ادامه برنامه فعلی", "priority": "medium"},
    {"text": "افزایش تمرینات قدرتی", "priority": "low"}
  ],
  "warnings": []
}
```

### Get Advanced Chart Insight

```bash
curl -X POST http://localhost:8000/api/v1/ai/chart-insight/advanced \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "wrestlerId": "wrestler-uuid",
    "section": "body_composition",
    "chartId": "weight-trend",
    "chartData": {
      "series": [
        {
          "name": "weight",
          "points": [
            {"date": "2025-01-01", "value": 87},
            {"date": "2025-01-15", "value": 86}
          ]
        }
      ]
    },
    "context": {
      "baseline": {"value": 85, "label": "Target Weight"},
      "thresholds": [{"label": "Competition", "value": 86}]
    },
    "locale": "en-US"
  }'
```

### Generate AI Training Program

```bash
curl -X POST http://localhost:8000/api/v1/ai/training-program \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "wrestlerId": "wrestler-uuid",
    "goal": "strength",
    "date": "2025-02-01"
  }'
```

## Scoring

### Get Overall Score

```bash
curl http://localhost:8000/api/v1/wrestlers/{wrestlerId}/scores/overall \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Domain Scores

```bash
curl http://localhost:8000/api/v1/wrestlers/{wrestlerId}/scores/domains \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get Score Explanation

```bash
curl http://localhost:8000/api/v1/wrestlers/{wrestlerId}/scores/explanation \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Legacy Data Endpoints

These endpoints provide access to measurement data from the legacy Fittechno database. All responses include session dates automatically resolved via joins with the `session_time` table.

### Common Query Parameters

All legacy data endpoints support these filter parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | int | Page number (default: 1) |
| `perPage` | int | Items per page (1-100, default: 50) |
| `athleteName` | string | Filter by athlete name (partial match) |
| `metricName` | string | Filter by metric name (partial match) |
| `sessionId` | string | Filter by exact session ID |
| `dateFrom` | string | Filter from date (YYYY-MM-DD) |
| `dateTo` | string | Filter to date (YYYY-MM-DD) |

### List Legacy Athletes

```bash
curl "http://localhost:8000/api/v1/data/athletes?page=1&perPage=50" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "athletes": [
    {
      "id": 1,
      "athleteName": "حسن یزدانی",
      "field": "freestyle",
      "name": "Hassan Yazdani",
      "createdAt": "2025-01-15T09:30:00"
    }
  ],
  "pagination": {
    "page": 1,
    "perPage": 50,
    "total": 100,
    "totalPages": 2
  }
}
```

### List Session Times

```bash
curl "http://localhost:8000/api/v1/data/sessions?athleteName=یزدانی&dateFrom=2025-01-01" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "sessions": [
    {
      "sessionId": 1001,
      "athleteId": 1,
      "athleteName": "حسن یزدانی",
      "miladiDate": "2025-01-15",
      "shamsiDate": "1403-10-26",
      "startTime": "09:30",
      "testCategory": "body_composition",
      "createdAt": "2025-01-15T09:30:00"
    }
  ],
  "pagination": {...}
}
```

### List Metric Definitions

```bash
curl "http://localhost:8000/api/v1/data/metrics?category=body_composition" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### List Body Composition (Freestyle)

```bash
curl "http://localhost:8000/api/v1/data/body-composition/freestyle?athleteName=یزدانی&metricName=Weight" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "sessionId": "1001",
      "athleteName": "حسن یزدانی",
      "metricName": "Weight",
      "nvalue": 86.5,
      "tvalue": null,
      "sessionDate": "2025-01-15",
      "sessionDateShamsi": "1403-10-26"
    }
  ],
  "pagination": {...},
  "style": "freestyle"
}
```

### List Body Composition (Greco-Roman)

```bash
curl "http://localhost:8000/api/v1/data/body-composition/greco-roman?athleteName=کریمی" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### List Chestbelt Heart Rate Data

```bash
curl "http://localhost:8000/api/v1/data/chestbelt-hr?sessionId=1001" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "sessionId": "1001",
      "athleteName": "حسن یزدانی",
      "metricName": "MaxHR",
      "nvalue": 185.0,
      "tvalue": null,
      "sessionDate": "2025-01-15",
      "sessionDateShamsi": "1403-10-26"
    }
  ],
  "pagination": {...}
}
```

### List Fitness Data

```bash
curl "http://localhost:8000/api/v1/data/fitness?metricName=VO2Max&dateFrom=2025-01-01&dateTo=2025-01-31" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "sessionId": "1001",
      "athleteName": "حسن یزدانی",
      "metricName": "VO2Max",
      "metricMethod": "Treadmill",
      "value": 55.5,
      "sessionDate": "2025-01-15",
      "sessionDateShamsi": "1403-10-26"
    }
  ],
  "pagination": {...}
}
```

### List Urion Analysis Data

```bash
curl "http://localhost:8000/api/v1/data/urion-analysis?athleteName=یزدانی" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Session Date Resolution Explained

Every measurement response includes the session date resolved automatically:

1. **How it works**: The API joins measurement tables with `session_time` using `session_id`
2. **Both date formats**: Responses include both Gregorian (`sessionDate`) and Persian (`sessionDateShamsi`) dates
3. **No manual joins**: The client doesn't need to make separate queries to resolve dates

**Example SQL Query (internally):**
```sql
SELECT 
    bc.id, bc.session_id, bc.athlete_name, bc.metric_name, bc.nvalue,
    st.miladi_date AS session_date,
    st.shamsi_date AS session_date_shamsi
FROM body_composition_fs bc
LEFT JOIN session_time st ON bc.session_id::bigint = st.session_id
WHERE bc.athlete_name ILIKE '%یزدانی%';
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable message",
  "details": {
    "field": "Specific field error"
  }
}
```

Common error codes:
- `VALIDATION_ERROR` (422): Invalid input data
- `INVALID_CREDENTIALS` (401): Wrong email/password
- `INVALID_TOKEN` (401): Expired or invalid JWT
- `NOT_FOUND` (404): Resource not found
- `FORBIDDEN` (403): Insufficient permissions
- `AI_ERROR` (501): AI provider error
