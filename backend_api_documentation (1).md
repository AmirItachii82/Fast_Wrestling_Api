# Wrestling Dashboard Backend API Documentation

This document specifies how the backend should handle, compute, and deliver data to the frontend. It defines endpoints, response shapes, AI analysis flows, scoring, and authentication. It is designed to be implemented as a REST API but can be adapted to any backend.

---

## 1) Overview

The frontend is organized by routes and expects structured, wrestler-scoped data. The backend should:

- Provide a roster and per-wrestler profiles.
- Serve domain-specific metrics (overview, body composition, bloodwork, recovery, supplements, performance).
- Provide chart-ready time series and summary stats.
- Provide AI analysis for charts on demand.
- Provide scoring endpoints (overall and per-domain scoring).
- Provide login/auth endpoints and session lifecycle.

All endpoints should accept a `wrestlerId` so the UI can switch between athletes. All time series should include `date` and `value` arrays or a list of points.

---

## 2) Core Concepts

### 2.1 Wrestler Entity

A wrestler record includes:

- Identifiers: `id`, `nameFa`, `nameEn`, `weightClass`, `imageUrl`.
- Domain metrics: overview, body composition, bloodwork, recovery, supplements, performance.
- History: time series for each domain to support charts.

### 2.2 Time Series Format

Use one of these shapes consistently:

```json
{
  "series": [
    { "name": "metricName", "points": [{ "date": "YYYY-MM-DD", "value": 0 }] }
  ]
}
```

or

```json
{
  "dates": ["YYYY-MM-DD"],
  "values": [0]
}
```

### 2.3 Chart Insight (AI Analyze Button)

Each chart can request AI insights. The backend should return:

- A concise human-readable explanation.
- A list of detected patterns.
- Recommendations with priority.
- Optional anomalies or thresholds breached.

---

## 3) Authentication & Session

### 3.1 Login

`POST /auth/login`

**Request**
```json
{
  "email": "user@example.com",
  "password": "string"
}
```

**Response**
```json
{
  "accessToken": "jwt",
  "refreshToken": "jwt",
  "user": {
    "id": "string",
    "name": "string",
    "role": "coach|athlete|admin"
  }
}
```

### 3.2 Refresh Token

`POST /auth/refresh`

**Request**
```json
{ "refreshToken": "jwt" }
```

**Response**
```json
{ "accessToken": "jwt" }
```

### 3.3 Logout

`POST /auth/logout`

**Request**
```json
{ "refreshToken": "jwt" }
```

**Response**
```json
{ "success": true }
```

### 3.4 Role Rules

- `admin`: full access.
- `coach`: access to team roster and all team athletes.
- `athlete`: access only to own data.

---

## 4) Roster & Wrestler Profile

### 4.1 List Wrestlers

`GET /wrestlers`

**Response**
```json
{
  "wrestlers": [
    { "id": "1", "nameFa": "...", "nameEn": "...", "weightClass": 86, "imageUrl": "/athletes/..." }
  ]
}
```

### 4.2 Wrestler Summary

`GET /wrestlers/{wrestlerId}`

**Response**
```json
{
  "id": "1",
  "nameFa": "...",
  "nameEn": "...",
  "weightClass": 86,
  "imageUrl": "/athletes/...",
  "status": "competition_ready|normal|attention"
}
```

---

## 5) Dashboard Overview (Route: /dashboard)

### 5.1 Overview Metrics

`GET /wrestlers/{wrestlerId}/overview`

**Purpose**: feeds the dashboard metric cards.

**Response**
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
    "mes": -0.8,
    "api": 2.1,
    "vo2max": 0.4,
    "frr": -1.2,
    "acs": 0.9,
    "bos": -0.6
  },
  "statusLabels": {
    "overallScore": "good|warning|bad",
    "msi": "good|warning|bad",
    "mes": "good|warning|bad",
    "api": "good|warning|bad",
    "vo2max": "good|warning|bad",
    "frr": "good|warning|bad",
    "acs": "good|warning|bad",
    "bos": "good|warning|bad"
  }
}
```

### 5.2 Overview Section Score

`GET /wrestlers/{wrestlerId}/overview/score`

**Response**
```json
{
  "section": "overview",
  "score": 86,
  "grade": "good|warning|bad",
  "lastUpdated": "YYYY-MM-DD"
}
```

### 5.2 Overview Chart (Radar)

`GET /wrestlers/{wrestlerId}/overview/chart`

**Response**
```json
{
  "labels": ["کمر", "سینه", "پاها", "بازوها", "شانه‌ها", "میان‌تنه"],
  "values": [92, 85, 78, 48, 80, 55]
}
```

---

## 6) Body Composition (Route: /dashboard/body-composition)

### 6.1 Summary Metrics

`GET /wrestlers/{wrestlerId}/body-composition`

**Response**
```json
{
  "metrics": {
    "weight": 86,
    "bodyFatPercentage": 8.5,
    "muscleMass": 76.2,
    "bmr": 2150,
    "powerToWeight": 1.92
  }
}
```

### 6.2 Section Score

`GET /wrestlers/{wrestlerId}/body-composition/score`

**Response**
```json
{
  "section": "body_composition",
  "score": 84,
  "grade": "good|warning|bad",
  "lastUpdated": "YYYY-MM-DD"
}
```

### 6.2 Trend Charts

`GET /wrestlers/{wrestlerId}/body-composition/trends`

**Response**
```json
{
  "powerToWeight": {
    "dates": ["2025-09-01", "2025-09-15"],
    "values": [1.82, 1.88]
  },
  "bodyWeight": {
    "dates": ["2025-09-01", "2025-09-15"],
    "values": [87.0, 86.0]
  },
  "bodyFat": {
    "dates": ["2025-09-01", "2025-09-15"],
    "values": [9.1, 8.5]
  }
}
```

### 6.3 InBody Breakdown

`GET /wrestlers/{wrestlerId}/body-composition/inbody`

**Response**
```json
{
  "intracellularWater": 28.2,
  "extracellularWater": 14.1,
  "visceralFatLevel": 7.8,
  "phaseAngle": 7.2
}
```

---

## 7) Bloodwork (Route: /dashboard/bloodwork)

### 7.1 Panels Summary

`GET /wrestlers/{wrestlerId}/bloodwork`

**Response**
```json
{
  "metrics": {
    "hemoglobin": 16.2,
    "hematocrit": 47.5,
    "testosteroneLevel": 720,
    "lastTestDate": "2025-10-28",
    "status": "optimal|normal|attention"
  }
}
```

### 7.2 Section Score

`GET /wrestlers/{wrestlerId}/bloodwork/score`

**Response**
```json
{
  "section": "bloodwork",
  "score": 88,
  "grade": "good|warning|bad",
  "lastUpdated": "YYYY-MM-DD"
}
```

### 7.2 Panel Charts

`GET /wrestlers/{wrestlerId}/bloodwork/charts`

**Response**
```json
{
  "cbc": {
    "wbc": { "dates": ["..."], "values": [6.8, 7.2] },
    "rbc": { "dates": ["..."], "values": [4.8, 4.9] },
    "hemoglobin": { "dates": ["..."], "values": [15.2, 15.8] },
    "hematocrit": { "dates": ["..."], "values": [44.2, 45.1] },
    "platelets": { "dates": ["..."], "values": [245, 258] }
  },
  "lipids": {
    "ldl": { "dates": ["..."], "values": [90, 95] },
    "hdl": { "dates": ["..."], "values": [55, 58] },
    "triglycerides": { "dates": ["..."], "values": [120, 110] }
  }
}
```

---

## 8) Recovery (Route: /dashboard/recovery)

### 8.1 Recovery Metrics

`GET /wrestlers/{wrestlerId}/recovery`

**Response**
```json
{
  "metrics": {
    "sleepQuality": 88,
    "hrvScore": 72,
    "fatigueLevel": 22,
    "hydrationLevel": 85,
    "readinessScore": 87
  }
}
```

### 8.2 Section Score

`GET /wrestlers/{wrestlerId}/recovery/score`

**Response**
```json
{
  "section": "recovery",
  "score": 87,
  "grade": "good|warning|bad",
  "lastUpdated": "YYYY-MM-DD"
}
```

### 8.2 Recovery Charts

`GET /wrestlers/{wrestlerId}/recovery/charts`

**Response**
```json
{
  "sleep": {
    "dates": ["..."],
    "duration": [7.5, 8.2],
    "quality": [7, 8]
  },
  "hrv": { "dates": ["..."], "values": [45, 48] },
  "stress": { "dates": ["..."], "values": [4, 3] },
  "soreness": {
    "dates": ["..."],
    "upper": [3, 2],
    "core": [2, 3],
    "lower": [4, 3]
  }
}
```

---

## 9) Supplements (Route: /dashboard/supplements)

### 9.1 Supplements Summary

`GET /wrestlers/{wrestlerId}/supplements`

**Response**
```json
{
  "metrics": {
    "adherenceRate": 92,
    "monthlyProgress": "+8%",
    "performanceCorrelation": 0.85,
    "totalSupplements": 8,
    "creatineDailyGrams": 5,
    "proteinDailyGrams": 180,
    "hydrationLiters": 3.0
  }
}
```

### 9.2 Section Score

`GET /wrestlers/{wrestlerId}/supplements/score`

**Response**
```json
{
  "section": "supplements",
  "score": 80,
  "grade": "good|warning|bad",
  "lastUpdated": "YYYY-MM-DD"
}
```

### 9.2 Supplements Charts

`GET /wrestlers/{wrestlerId}/supplements/charts`

**Response**
```json
{
  "creatine": { "dates": ["..."], "values": [5, 5, 4] },
  "protein": { "dates": ["..."], "values": [160, 175, 180] },
  "adherence": { "dates": ["..."], "values": [85, 90, 92] },
  "hydration": { "dates": ["..."], "values": [2.6, 2.8, 3.0] },
  "performanceCorrelation": { "dates": ["..."], "values": [0.72, 0.81, 0.85] },
  "stackOverview": {
    "supplements": [
      { "name": "Creatine", "daily": true },
      { "name": "Omega-3", "daily": true }
    ]
  }
}
```

---

## 10) Bodybuilding Performance (Route: /dashboard/bodybuilding-performance)

### 10.1 Strength/Performance Summary

`GET /wrestlers/{wrestlerId}/bodybuilding-performance`

**Response**
```json
{
  "metrics": {
    "benchPressMax": 330,
    "squatMax": 460,
    "deadliftMax": 520,
    "vo2max": 53.7,
    "bodyFatPercentage": 13.5,
    "performanceScore": 87
  }
}
```

### 10.2 Section Score

`GET /wrestlers/{wrestlerId}/bodybuilding-performance/score`

**Response**
```json
{
  "section": "bodybuilding_performance",
  "score": 87,
  "grade": "good|warning|bad",
  "lastUpdated": "YYYY-MM-DD"
}
```

### 10.2 Charts

`GET /wrestlers/{wrestlerId}/bodybuilding-performance/charts`

**Response**
```json
{
  "strength": {
    "bench": { "dates": ["..."], "values": [295, 330] },
    "squat": { "dates": ["..."], "values": [420, 460] },
    "deadlift": { "dates": ["..."], "values": [470, 520] }
  },
  "cardio": {
    "vo2max": { "dates": ["..."], "values": [50.2, 53.7] },
    "hrZones": { "zones": ["Z1", "Z2"], "values": [22, 35] }
  },
  "analytics": {
    "volumeLoad": { "dates": ["..."], "values": [12000, 13500] },
    "rpe": { "buckets": ["6", "7", "8"], "values": [20, 30, 15] }
  },
  "bodybuilding": {
    "symmetry": { "labels": ["Upper", "Lower"], "values": [88, 83] },
    "activation": { "labels": ["Core", "Legs"], "values": [80, 92] }
  }
}
```

---

## 11) Training Program (Route: /dashboard/training-program)

### 11.1 Current Day Program

`GET /wrestlers/{wrestlerId}/training-program`

**Response**
```json
{
  "date": "YYYY-MM-DD",
  "readiness": 7,
  "sessionRPE": 7,
  "bodyweight": 86,
  "hydration": 3.0,
  "notes": "string",
  "exercises": [
    {
      "name": "پرس سینه",
      "sets": [
        { "reps": 8, "weight": 100 },
        { "reps": 8, "weight": 105 }
      ]
    }
  ]
}
```

### 11.2 Submit Program Update

`POST /wrestlers/{wrestlerId}/training-program`

**Request**: same shape as GET.

**Response**
```json
{ "success": true }
```

---

## 12) Calendar (Route: /dashboard/calendar)

### 12.1 Monthly Programs

`GET /wrestlers/{wrestlerId}/calendar`

**Response**
```json
{
  "programs": [
    {
      "date": "YYYY-MM-DD",
      "title": "string",
      "focus": "string",
      "blocks": [{ "name": "...", "sets": 4, "reps": "6-8" }],
      "nutrition": "string",
      "recovery": "string",
      "aiRecommendations": ["string"]
    }
  ]
}
```

---

## 13) Team Overview (Route: /dashboard/team-overview)

### 13.1 Team Stats

`GET /teams/{teamId}/stats`

**Response**
```json
{
  "totalAthletes": 12,
  "averageScore": 83,
  "competitionReady": 6,
  "needsAttention": 2
}
```

### 13.2 Team Roster Cards

`GET /teams/{teamId}/athletes`

**Response**
```json
{
  "athletes": [
    {
      "id": "1",
      "nameFa": "...",
      "weightClass": 86,
      "overallScore": 92,
      "currentActivity": "...",
      "insights": [{ "label": "...", "type": "success|warning|info" }],
      "trainingWeek": 6,
      "totalWeeks": 8
    }
  ]
}
```

---

## 14) AI Endpoints

### 14.1 Chart Insight

`POST /ai/chart-insight`

**Request**
```json
{
  "wrestlerId": "1",
  "chartId": "overview-radar",
  "chartData": { "labels": ["..."], "values": [92, 85] },
  "locale": "fa-IR"
}
```

**Response**
```json
{
  "summary": "string",
  "patterns": ["string"],
  "recommendations": [
    { "text": "string", "priority": "high|medium|low" }
  ],
  "warnings": ["string"]
}
```

### 14.1.1 Advanced Chart Insight (Structured)

Use this for advanced charts that need deeper analysis such as body composition trends, bloodwork panels, recovery charts, and performance analytics.

`POST /ai/chart-insight/advanced`

**Request**
```json
{
  "wrestlerId": "1",
  "section": "body_composition|bloodwork|recovery|supplements|bodybuilding_performance",
  "chartId": "string",
  "chartData": {
    "series": [
      { "name": "metricName", "points": [{ "date": "YYYY-MM-DD", "value": 0 }] }
    ]
  },
  "context": {
    "baseline": { "value": 0, "label": "string" },
    "thresholds": [{ "label": "string", "value": 0 }],
    "recentNotes": ["string"]
  },
  "locale": "fa-IR"
}
```

**Response**
```json
{
  "summary": "string",
  "patterns": ["string"],
  "anomalies": [{ "label": "string", "date": "YYYY-MM-DD", "value": 0 }],
  "recommendations": [
    { "text": "string", "priority": "high|medium|low" }
  ],
  "confidence": 0.0
}
```

### 14.1.2 Insight Caching

If the same chart data is sent repeatedly, the backend should return a cached insight for a TTL window (e.g. 24h) to reduce AI calls.

### 14.2 Program Generation

`POST /ai/training-program`

**Request**
```json
{ "wrestlerId": "1", "goal": "strength", "date": "YYYY-MM-DD" }
```

**Response**
```json
{
  "program": {
    "date": "YYYY-MM-DD",
    "title": "string",
    "focus": "string",
    "blocks": [{ "name": "...", "sets": 4, "reps": "6-8" }],
    "nutrition": "string",
    "recovery": "string",
    "aiRecommendations": ["string"]
  }
}
```

---

## 15) Score Endpoints

### 15.1 Overall Score

`GET /wrestlers/{wrestlerId}/scores/overall`

**Response**
```json
{
  "score": 86,
  "grade": "good|warning|bad",
  "lastUpdated": "YYYY-MM-DD"
}
```

### 15.2 Domain Scores

`GET /wrestlers/{wrestlerId}/scores/domains`

**Response**
```json
{
  "strength": 90,
  "endurance": 82,
  "recovery": 87,
  "bodyComposition": 84,
  "bloodwork": 88,
  "supplements": 80
}
```

### 15.3 Score Explanation

`GET /wrestlers/{wrestlerId}/scores/explanation`

**Response**
```json
{
  "drivers": [
    { "metric": "vo2max", "impact": "+", "weight": 0.2 },
    { "metric": "fatigueLevel", "impact": "-", "weight": 0.15 }
  ],
  "notes": "string"
}
```

### 15.4 Section Score Payload Notes

Every section endpoint should expose a `score` endpoint and include `grade` plus `lastUpdated` in the response.

---

## 16) Error Handling

Standard error shape for non-2xx responses:

```json
{
  "error": "string",
  "message": "string",
  "details": { "field": "reason" }
}
```

---

## 17) Caching & Rate Limiting

- Cache stable metrics (bloodwork, body composition) for 5–15 minutes.
- Rate limit AI endpoints more aggressively (e.g. 10 requests / minute / user).

---

## 18) Security & Data Validation

- Validate `wrestlerId` on every request and enforce role access.
- Keep AI inputs sanitized; avoid sending personally identifying info beyond wrestlerId unless required.
- Enforce input ranges for biometrics and training loads.

---

## 19) Frontend Integration Notes

- The frontend uses chart components that can consume `labels + values` or `dates + values`.
- AI analyze buttons should call `/ai/chart-insight` with chart data payloads.
- Team overview uses aggregate endpoints under `/teams/*`.
- Training program and calendar endpoints should be consistent with the chat program schema.

---

End of document.
