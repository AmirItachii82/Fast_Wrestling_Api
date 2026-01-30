# API Description

Complete documentation of all Wrestling Dashboard API endpoints, including both modern wrestler-focused endpoints and legacy Fittechno data endpoints.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All endpoints (except login and signup) require a valid JWT access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Response Format

All responses follow a consistent JSON format:

### Success Response
```json
{
  "data": {...}
}
```

### Error Response
```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable error description",
  "details": {
    "field": "Specific field error"
  }
}
```

---

## Authentication Endpoints

### POST /auth/login

Authenticate user and receive JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIs...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": "uuid",
    "name": "User Name",
    "role": "admin|coach|athlete"
  }
}
```

### POST /auth/refresh

Refresh an expired access token.

**Request Body:**
```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response:**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIs..."
}
```

### POST /auth/logout

Invalidate a refresh token.

**Request Body:**
```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response:**
```json
{
  "success": true
}
```

### POST /auth/signup

Create a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "User Name",
  "role": "athlete",
  "wrestlerId": "optional-uuid",
  "teamId": "optional-uuid"
}
```

---

## Wrestler Endpoints

### GET /wrestlers

List all wrestlers.

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

### GET /wrestlers/{wrestlerId}

Get wrestler details.

**Response:**
```json
{
  "id": "uuid",
  "nameFa": "حسن یزدانی",
  "nameEn": "Hassan Yazdani",
  "weightClass": 86,
  "imageUrl": "/athletes/hassan.jpg",
  "status": "competition_ready"
}
```

### POST /wrestlers

Create a new wrestler (admin/coach only).

### PUT /wrestlers/{wrestlerId}

Update wrestler details (admin/coach only).

### DELETE /wrestlers/{wrestlerId}

Delete a wrestler (admin only).

---

## Overview Endpoints

### GET /wrestlers/{wrestlerId}/overview

Get overview metrics for a wrestler.

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
    "msi": 1.5
  },
  "statusLabels": {
    "overallScore": "good",
    "msi": "good"
  }
}
```

### GET /wrestlers/{wrestlerId}/overview/score

Get section score for overview.

### GET /wrestlers/{wrestlerId}/overview/chart

Get radar chart data.

---

## Body Composition Endpoints

### GET /wrestlers/{wrestlerId}/body-composition

Get body composition metrics.

### GET /wrestlers/{wrestlerId}/body-composition/score

Get body composition section score.

### GET /wrestlers/{wrestlerId}/body-composition/trends

Get body composition trend data.

**Query Parameters:**
- `limit` (optional): Number of data points (default: 30, max: 365)

### GET /wrestlers/{wrestlerId}/body-composition/inbody

Get InBody breakdown data.

---

## Legacy Data Endpoints

These endpoints provide access to data from the legacy Fittechno database. All responses include session dates resolved automatically.

### Session Date Resolution

All measurement data responses include:
- `sessionId`: The session identifier
- `sessionDate`: Gregorian date (YYYY-MM-DD format)
- `sessionDateShamsi`: Persian/Shamsi date

The session date is automatically resolved by joining with the `session_time` table.

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

### Pagination Response

All list endpoints include pagination metadata:

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "perPage": 50,
    "total": 1234,
    "totalPages": 25
  }
}
```

---

### GET /data/athletes

List legacy athletes from Fittechno database.

**Query Parameters:**
- `page` (int): Page number
- `perPage` (int): Items per page
- `athleteName` (string): Filter by athlete name

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

---

### GET /data/sessions

List session times with date information.

**Query Parameters:**
- `page` (int): Page number
- `perPage` (int): Items per page
- `athleteName` (string): Filter by athlete name
- `testCategory` (string): Filter by test category
- `dateFrom` (string): Filter from date
- `dateTo` (string): Filter to date

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

---

### GET /data/metrics

List metric definitions.

**Query Parameters:**
- `page` (int): Page number
- `perPage` (int): Items per page
- `category` (string): Filter by category

**Response:**
```json
{
  "metrics": [
    {
      "id": 1,
      "metricName": "Weight",
      "metricMethod": "InBody",
      "category": "body_composition"
    }
  ],
  "pagination": {...}
}
```

---

### GET /data/body-composition/freestyle

List freestyle body composition measurements with session dates.

**Query Parameters:**
All common parameters plus:
- `athleteName` (string): Filter by athlete name
- `metricName` (string): Filter by metric name
- `sessionId` (string): Filter by session ID
- `dateFrom` (string): Filter from date
- `dateTo` (string): Filter to date

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

---

### GET /data/body-composition/greco-roman

List greco-roman body composition measurements with session dates.

Same parameters and response format as freestyle endpoint, with `"style": "greco-roman"`.

---

### GET /data/chestbelt-hr

List chestbelt heart rate measurements with session dates.

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

---

### GET /data/fitness

List fitness measurements with session dates.

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

---

### GET /data/urion-analysis

List urion analysis measurements with session dates.

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "sessionId": "1001",
      "athleteName": "حسن یزدانی",
      "metricName": "pH",
      "metricMethod": "Urion",
      "value": 6.5,
      "sessionDate": "2025-01-15",
      "sessionDateShamsi": "1403-10-26"
    }
  ],
  "pagination": {...}
}
```

---

## Team Endpoints

### GET /teams/{teamId}/stats

Get team statistics.

**Response:**
```json
{
  "totalAthletes": 15,
  "averageScore": 82.5,
  "competitionReady": 8,
  "needsAttention": 2
}
```

### GET /teams/{teamId}/athletes

Get athletes in a team.

---

## AI Endpoints

### POST /ai/chart-insight

Get AI-generated insight for chart data.

**Request Body:**
```json
{
  "wrestlerId": "uuid",
  "chartId": "overview-radar",
  "chartData": {
    "labels": ["کمر", "سینه", "پاها"],
    "values": [92, 85, 78]
  },
  "locale": "fa-IR"
}
```

**Response:**
```json
{
  "summary": "تحلیل نمودار...",
  "patterns": ["روند صعودی مشاهده شده"],
  "recommendations": [
    {"text": "ادامه برنامه فعلی", "priority": "medium"}
  ],
  "warnings": []
}
```

### POST /ai/chart-insight/advanced

Get advanced AI insight with context.

### POST /ai/training-program

Generate AI training program.

---

## Scoring Endpoints

### GET /wrestlers/{wrestlerId}/scores/overall

Get overall score.

### GET /wrestlers/{wrestlerId}/scores/domains

Get domain-level scores.

### GET /wrestlers/{wrestlerId}/scores/explanation

Get score explanation with drivers.

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 422 | Invalid request data |
| `INVALID_CREDENTIALS` | 401 | Wrong email/password |
| `INVALID_TOKEN` | 401 | Expired or invalid JWT |
| `TOKEN_EXPIRED` | 401 | JWT token has expired |
| `NOT_FOUND` | 404 | Resource not found |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `AI_ERROR` | 501 | AI provider error |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |

---

## Rate Limiting

API endpoints are rate-limited:
- **General endpoints**: 100 requests/minute
- **AI endpoints**: 10 requests/minute

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1706618400
```

---

## CORS Configuration

The API supports CORS for configured origins. Set `CORS_ORIGINS` in environment:

```
CORS_ORIGINS=http://localhost:3000,https://dashboard.wrestling.com
```
