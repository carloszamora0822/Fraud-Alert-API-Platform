"""
Shared test fixtures for the fraud alert API test suite.

Key concept: SAVEPOINT-BASED TRANSACTION ROLLBACK
Each test runs inside a database transaction that gets rolled back after the test,
so tests never leave data behind.
"""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import settings
from app.core.database import get_db
from app.main import app
from app.models.base import Base

# ── Test database URL ────────────────────────────────────────────
TEST_DATABASE_URL = settings.DATABASE_URL.replace("/fraud_db", "/fraud_db_test")

# Track whether tables have been created this session
_tables_created = False


# Disable rate limiter at import time
from app.core.rate_limit import limiter  # noqa: E402

limiter.enabled = False


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Per-test database session using savepoint rollback.

    Creates a fresh engine per test to avoid event loop issues,
    and uses savepoint rollback so each test is isolated.
    """
    global _tables_created

    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create tables once per session
    if not _tables_created:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        _tables_created = True

    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection, expire_on_commit=False)
        await connection.begin_nested()

        @event.listens_for(session.sync_session, "after_transaction_end")
        def restart_savepoint(sync_session, trans):
            if trans.nested and not trans._parent.nested:
                session.begin_nested()

        yield session

        await session.close()
        await transaction.rollback()

    await engine.dispose()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Test HTTP client with DB dependency overridden."""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


# ── Auth helper fixtures ─────────────────────────────────────────


async def _register_and_login(
    client: AsyncClient, email: str, password: str, role: str
) -> str:
    """Register a user and return their JWT token."""
    await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "role": role},
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    return resp.json()["access_token"]


@pytest.fixture
async def admin_token(client: AsyncClient) -> str:
    return await _register_and_login(client, "admin@test.com", "adminpass123", "admin")


@pytest.fixture
async def analyst_token(client: AsyncClient) -> str:
    return await _register_and_login(
        client, "analyst@test.com", "analystpass123", "analyst"
    )


@pytest.fixture
async def admin_headers(admin_token: str) -> dict:
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
async def analyst_headers(analyst_token: str) -> dict:
    return {"Authorization": f"Bearer {analyst_token}"}


@pytest.fixture
async def sample_account(client: AsyncClient, admin_headers: dict) -> dict:
    """Create and return a sample account."""
    resp = await client.post(
        "/api/v1/accounts/",
        json={"account_name": "Test Corp", "environment": "production"},
        headers=admin_headers,
    )
    return resp.json()


@pytest.fixture
async def sample_alert(
    client: AsyncClient, admin_headers: dict, sample_account: dict
) -> dict:
    """Create and return a sample alert."""
    resp = await client.post(
        "/api/v1/alerts/",
        json={
            "alert_id": "TEST-001",
            "severity": "high",
            "event_type": "unusual_login",
            "resource_type": "virtual_machine",
            "source_ip": "192.168.1.1",
            "geo_location": "US-East",
            "raw_payload": {"key": "value"},
            "account_id": sample_account["id"],
        },
        headers=admin_headers,
    )
    return resp.json()
