"""
Pytest configuration and fixtures.
"""

import asyncio
from datetime import datetime
from typing import AsyncGenerator, Generator
import uuid

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from app.main import app
from app.db.session import get_db
from app.core.security import get_password_hash
from app.models import (
    User,
    UserRole,
    Team,
    Wrestler,
    WrestlerStatus,
    OverviewMetrics,
    SectionScore,
    Grade,
)


# Use SQLite for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """Create async session for testing."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    async_session_factory = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session_factory() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(async_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client with database override."""
    
    async def override_get_db():
        yield async_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_team(async_session: AsyncSession) -> Team:
    """Create test team."""
    team = Team(
        id=str(uuid.uuid4()),
        name="Test Team",
    )
    async_session.add(team)
    await async_session.commit()
    await async_session.refresh(team)
    return team


@pytest_asyncio.fixture
async def test_wrestler(async_session: AsyncSession, test_team: Team) -> Wrestler:
    """Create test wrestler."""
    wrestler = Wrestler(
        id=str(uuid.uuid4()),
        team_id=test_team.id,
        name_fa="ورزشکار تست",
        name_en="Test Wrestler",
        weight_class=86,
        status=WrestlerStatus.NORMAL,
    )
    async_session.add(wrestler)
    await async_session.commit()
    await async_session.refresh(wrestler)
    return wrestler


@pytest_asyncio.fixture
async def test_admin_user(async_session: AsyncSession) -> User:
    """Create test admin user."""
    user = User(
        id=str(uuid.uuid4()),
        email="admin@test.com",
        password_hash=get_password_hash("admin123"),
        name="Test Admin",
        role=UserRole.ADMIN,
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_coach_user(async_session: AsyncSession, test_team: Team) -> User:
    """Create test coach user."""
    user = User(
        id=str(uuid.uuid4()),
        email="coach@test.com",
        password_hash=get_password_hash("coach123"),
        name="Test Coach",
        role=UserRole.COACH,
        team_id=test_team.id,
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_athlete_user(async_session: AsyncSession, test_wrestler: Wrestler) -> User:
    """Create test athlete user."""
    user = User(
        id=str(uuid.uuid4()),
        email="athlete@test.com",
        password_hash=get_password_hash("athlete123"),
        name="Test Athlete",
        role=UserRole.ATHLETE,
        wrestler_id=test_wrestler.id,
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_overview_metrics(async_session: AsyncSession, test_wrestler: Wrestler) -> OverviewMetrics:
    """Create test overview metrics."""
    metrics = OverviewMetrics(
        wrestler_id=test_wrestler.id,
        overall_score=86,
        msi=92,
        mes=78,
        api=420,
        vo2max=55,
        frr=84,
        acs=72,
        bos=4,
    )
    async_session.add(metrics)
    await async_session.commit()
    await async_session.refresh(metrics)
    return metrics


@pytest_asyncio.fixture
async def test_section_score(async_session: AsyncSession, test_wrestler: Wrestler) -> SectionScore:
    """Create test section score."""
    score = SectionScore(
        wrestler_id=test_wrestler.id,
        section_key="overview",
        score=86,
        grade=Grade.GOOD,
    )
    async_session.add(score)
    await async_session.commit()
    await async_session.refresh(score)
    return score


async def get_auth_token(client: AsyncClient, email: str, password: str) -> str:
    """Helper to get auth token."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    if response.status_code == 200:
        return response.json()["accessToken"]
    raise ValueError(f"Failed to get token: {response.text}")
