# API Usage Guide

This document provides detailed examples for using the Wrestling Dashboard Backend API.

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
