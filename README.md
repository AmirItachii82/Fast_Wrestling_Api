# Wrestling Dashboard Backend API

A production-quality FastAPI backend for the Wrestling Dashboard application, providing athlete performance management, metrics tracking, AI-powered insights, and training program generation.

## Features

- 🔐 **Secure Authentication**: JWT-based auth with role-based access control (admin, coach, athlete)
- 📊 **Comprehensive Metrics**: Body composition, bloodwork, recovery, supplements, performance tracking
- 🤖 **AI-Powered Insights**: Chart analysis and training program generation with caching
- 📈 **Time Series Data**: Historical trends for all metrics
- 🏆 **Scoring System**: Deterministic scoring with grade computation
- 🔄 **Caching**: Redis-backed caching with in-memory fallback
- 📝 **Full Documentation**: OpenAPI/Swagger, Postman collection, architecture docs

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd wrestling-dashboard-api

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Run migrations
docker-compose run migrate

# Seed initial data (optional)
docker-compose --profile seed up seed

# The API is now available at http://localhost:8000
```

### Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Seed initial data (optional)
python scripts/seed_data.py

# Start the server
uvicorn app.main:app --reload
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_NAME` | Application name | Wrestling Dashboard API |
| `APP_ENV` | Environment (development/production) | development |
| `DEBUG` | Enable debug mode | true |
| `SECRET_KEY` | Application secret key | (required) |
| `DATABASE_URL` | PostgreSQL connection URL (async) | postgresql+asyncpg://... |
| `DATABASE_URL_SYNC` | PostgreSQL connection URL (sync) | postgresql://... |
| `REDIS_URL` | Redis connection URL | redis://localhost:6379/0 |
| `JWT_SECRET_KEY` | JWT signing key | (required) |
| `JWT_ALGORITHM` | JWT algorithm | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | 30 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | 7 |
| `OPENAI_API_KEY` | OpenAI API key (optional) | (empty) |
| `AI_CACHE_TTL_HOURS` | AI insight cache TTL | 24 |
| `CORS_ORIGINS` | Allowed CORS origins | http://localhost:3000 |
| `SENTRY_DSN` | Sentry error tracking (optional) | (empty) |

## API Documentation

Once the server is running, access:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## Project Structure

```
.
├── app/
│   ├── api/v1/           # API route handlers
│   │   ├── auth.py       # Authentication endpoints
│   │   ├── wrestlers.py  # Wrestler CRUD
│   │   ├── ai.py         # AI insight endpoints
│   │   └── ...
│   ├── core/             # Core configuration
│   │   ├── config.py     # Settings management
│   │   └── security.py   # JWT & password utilities
│   ├── db/               # Database configuration
│   │   └── session.py    # Async session factory
│   ├── models/           # SQLModel database models
│   │   └── database.py   # All entity definitions
│   ├── schemas/          # Pydantic schemas
│   │   └── api.py        # Request/response models
│   ├── services/         # Business logic
│   │   ├── auth_service.py
│   │   ├── wrestler_service.py
│   │   ├── scoring_service.py
│   │   ├── ai_service.py
│   │   └── time_series_service.py
│   ├── utils/            # Utilities
│   │   ├── dependencies.py
│   │   └── logging.py
│   └── main.py           # Application entry point
├── alembic/              # Database migrations
├── tests/                # Test suite
│   ├── unit/
│   └── integration/
├── scripts/              # Utility scripts
│   └── seed_data.py
├── docs/                 # Documentation
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Running Tests

```bash
# Install test dependencies (already in requirements.txt)
pip install pytest pytest-asyncio pytest-cov aiosqlite

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/integration/test_auth.py

# Run tests with verbose output
pytest -v
```

## Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply all migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## Default Users (After Seeding)

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@wrestling.com | admin123 |
| Coach | coach@wrestling.com | coach123 |
| Athlete | athlete@wrestling.com | athlete123 |

## AI Provider Configuration

The API supports AI-powered chart insights and training program generation. By default, it uses a mock adapter that returns deterministic responses.

To use OpenAI:

1. Set `OPENAI_API_KEY` in your environment
2. The adapter will automatically switch to OpenAI

## Rate Limiting

AI endpoints (`/ai/*`) are rate-limited to 10 requests per minute per user. This can be configured via `AI_RATE_LIMIT_PER_MINUTE`.

## Security Considerations

- All passwords are hashed using bcrypt
- JWT tokens are signed with HS256
- Refresh tokens can be blacklisted (logout)
- Role-based access control on all endpoints
- PII is sanitized before sending to AI providers
- Input validation on all endpoints

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License
