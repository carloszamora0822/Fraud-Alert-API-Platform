"""Tests for role-based access control."""

from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.core.config import settings


@pytest.mark.asyncio
async def test_admin_accesses_admin_endpoints(client, admin_headers):
    resp = await client.post(
        "/api/v1/accounts/",
        json={"account_name": "Admin Test Corp"},
        headers=admin_headers,
    )
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_analyst_accesses_analyst_endpoints(
    client, admin_headers, analyst_headers
):
    await client.post(
        "/api/v1/accounts/",
        json={"account_name": "Viewable Corp"},
        headers=admin_headers,
    )
    resp = await client.get("/api/v1/accounts/", headers=analyst_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_analyst_blocked_from_admin_endpoints(client, analyst_headers):
    resp = await client.post(
        "/api/v1/accounts/",
        json={"account_name": "Nope Corp"},
        headers=analyst_headers,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_expired_token_returns_401(client):
    expired_token = jwt.encode(
        {
            "sub": "expired@test.com",
            "role": "admin",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    resp = await client.get(
        "/api/v1/accounts/",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_malformed_token_returns_401(client):
    resp = await client.get(
        "/api/v1/accounts/",
        headers={"Authorization": "Bearer not.a.real.token"},
    )
    assert resp.status_code == 401
