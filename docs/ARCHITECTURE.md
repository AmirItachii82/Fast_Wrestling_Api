# Architecture Documentation

This document describes the architecture, data model, caching strategy, and security considerations for the Wrestling Dashboard Backend API.

## System Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    Frontend     │────▶│   FastAPI App   │────▶│   PostgreSQL    │
│  (React/Next)   │     │   (Uvicorn)     │     │   Database      │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   Redis Cache   │     │   OpenAI API    │
                        │   (Optional)    │     │   (Optional)    │
                        └─────────────────┘     └─────────────────┘
```

## Data Model

### Entity Relationship Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    Teams    │◀───│   Wrestlers │───▶│    Users    │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
       ┌───────────────────┼───────────────────┐
       ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Overview   │   │    Body      │   │  Bloodwork   │
│   Metrics    │   │ Composition  │   │   Metrics    │
└──────────────┘   └──────────────┘   └──────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Overview   │   │    Body      │   │  Bloodwork   │
│   Series     │   │ Comp Series  │   │   Series     │
└──────────────┘   └──────────────┘   └──────────────┘
       
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Recovery   │   │  Supplements │   │ Performance  │
│   Metrics    │   │   Metrics    │   │   Metrics    │
└──────────────┘   └──────────────┘   └──────────────┘

┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   Training   │   │   AI Chart   │   │   Section    │
│   Programs   │   │   Insights   │   │    Scores    │
└──────────────┘   └──────────────┘   └──────────────┘
```

### Core Entities

#### Users
- Authentication and authorization
- Roles: admin, coach, athlete
- Linked to wrestler (for athletes) or team (for coaches)

#### Teams
- Organizational unit for wrestlers
- Coaches are assigned to teams

#### Wrestlers
- Athlete profiles
- All metrics are wrestler-scoped
- Status: competition_ready, normal, attention

### Metrics Tables

Each domain has two types of tables:

1. **Metrics (Snapshots)**: Latest values for quick queries
2. **Series (Time Series)**: Historical data for charts

| Domain | Metrics Table | Series Table |
|--------|---------------|--------------|
| Overview | overview_metrics | overview_series |
| Body Composition | body_composition_metrics | body_composition_series |
| Bloodwork | bloodwork_metrics | bloodwork_series |
| Recovery | recovery_metrics | recovery_series |
| Supplements | supplements_metrics | supplements_series |
| Performance | performance_metrics | performance_series |

### Indexing Strategy

```sql
-- All metrics tables
CREATE INDEX ix_{table}_wrestler_id ON {table}(wrestler_id);

-- All series tables (composite for time queries)
CREATE INDEX ix_{table}_wrestler_recorded ON {table}(wrestler_id, recorded_at);

-- Section scores (for filtering)
CREATE INDEX ix_section_scores_wrestler_section_recorded 
  ON section_scores(wrestler_id, section_key, recorded_at);

-- AI insights (unique constraint for caching)
CREATE UNIQUE INDEX uq_ai_insight_hash 
  ON ai_chart_insights(wrestler_id, chart_id, input_hash);
```

## Caching Strategy

### Redis Cache (Primary)

AI insights are cached in Redis with configurable TTL (default: 24 hours).

```python
Cache Key Format:
- chart_insight:{input_hash}
- advanced_insight:{input_hash}
- training_program:{input_hash}
```

### Database Cache (Secondary)

AI insights are also persisted to `ai_chart_insights` table for:
- Long-term storage
- Analytics on AI usage
- Backup if Redis is unavailable

### In-Memory Cache (Fallback)

If Redis is unavailable, the system falls back to an in-memory dictionary cache.

### Cache Flow

```
Request → Check Redis → Check DB → Generate New → Store to Redis + DB → Response
              ↓             ↓
           Return        Return
          Cached        Cached
```

## Security Architecture

### Authentication Flow

```
Login Request
     ↓
Validate Credentials
     ↓
Generate JWT Tokens
├── Access Token (30 min)
└── Refresh Token (7 days)
     ↓
Return Tokens
```

### Token Validation

```
API Request
     ↓
Extract Bearer Token
     ↓
Verify JWT Signature
     ↓
Check Token Type (access)
     ↓
Load User from DB
     ↓
Check Role Permissions
     ↓
Execute Handler
```

### Role-Based Access Control

| Role | Wrestlers Access | Team Access | Admin Actions |
|------|------------------|-------------|---------------|
| Admin | All | All | Yes |
| Coach | Team members only | Own team | No |
| Athlete | Own data only | No | No |

### Password Security

- Passwords hashed with bcrypt (work factor: default)
- Passwords never stored in plain text
- Passwords never logged or returned in API responses

### JWT Security

- Tokens signed with HS256 algorithm
- Separate secrets for app and JWT (recommended)
- Token type embedded in payload
- Refresh tokens can be blacklisted

## AI Integration

### Adapter Pattern

```python
class LLMAdapter(ABC):
    @abstractmethod
    async def generate_chart_insight(...)
    
    @abstractmethod
    async def generate_advanced_insight(...)
    
    @abstractmethod
    async def generate_training_program(...)
```

### Provider Selection

1. If `OPENAI_API_KEY` is set → Use `OpenAIAdapter`
2. Otherwise → Use `MockLLMAdapter`

### PII Sanitization

Before sending to AI:
- Email addresses removed
- Names (nameFa, nameEn) removed
- Phone numbers removed
- Only anonymized metrics sent

### Rate Limiting

AI endpoints are rate-limited to prevent abuse:
- 10 requests per minute per user (configurable)
- Uses `slowapi` with `get_remote_address` key function

## Error Handling

### Standard Error Response

```json
{
  "error": "ERROR_CODE",
  "message": "Human-readable description",
  "details": {
    "field": "specific error"
  }
}
```

### HTTP Status Codes

| Status | Use Case |
|--------|----------|
| 200 | Success |
| 401 | Invalid/missing authentication |
| 403 | Insufficient permissions |
| 404 | Resource not found |
| 422 | Validation error |
| 429 | Rate limit exceeded |
| 500 | Internal server error |
| 501 | AI provider not configured |

## Logging

### Structured Logging

Using `structlog` for structured JSON logging:

```python
logger.info(
    "Request processed",
    user_id=user.id,
    endpoint="/wrestlers",
    duration_ms=45
)
```

### Log Levels

- DEBUG: Detailed debugging information
- INFO: General operational events
- WARNING: Potential issues
- ERROR: Errors that need attention

### Sentry Integration

Optional error tracking with Sentry:

```python
if settings.sentry_dsn:
    sentry_sdk.init(dsn=settings.sentry_dsn)
```

## Scalability Considerations

### Horizontal Scaling

- Stateless API design
- Database connections via connection pool
- Redis for shared cache
- JWT tokens (no server-side sessions)

### Database Scaling

- Read replicas for heavy read workloads
- Partitioning for time-series data (by month/year)
- Archive old data to cold storage

### Caching Improvements

- CDN for static assets
- Response caching for stable endpoints
- Query result caching for expensive queries

## Deployment

### Production Checklist

- [ ] Change SECRET_KEY and JWT_SECRET_KEY
- [ ] Enable HTTPS
- [ ] Configure CORS for production domains
- [ ] Set APP_ENV=production
- [ ] Enable Sentry for error tracking
- [ ] Configure database connection pooling
- [ ] Set up monitoring and alerting
- [ ] Configure log aggregation
- [ ] Set up backup strategy
