"""Tests for account endpoints."""

import uuid

import pytest


@pytest.mark.asyncio
async def test_create_account(client, admin_headers):
    resp = await client.post(
        "/api/v1/accounts/",
        json={"account_name": "Acme Inc"},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["account_name"] == "Acme Inc"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_accounts(client, admin_headers, analyst_headers):
    await client.post(
        "/api/v1/accounts/",
        json={"account_name": "Listed Corp"},
        headers=admin_headers,
    )
    resp = await client.get("/api/v1/accounts/", headers=analyst_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_get_account_by_id(client, admin_headers, analyst_headers):
    create_resp = await client.post(
        "/api/v1/accounts/",
        json={"account_name": "Findable Corp"},
        headers=admin_headers,
    )
    account_id = create_resp.json()["id"]
    resp = await client.get(f"/api/v1/accounts/{account_id}", headers=analyst_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == account_id


@pytest.mark.asyncio
async def test_get_nonexistent_account(client, analyst_headers):
    fake_id = str(uuid.uuid4())
    resp = await client.get(f"/api/v1/accounts/{fake_id}", headers=analyst_headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_analyst_cannot_create_account(client, analyst_headers):
    resp = await client.post(
        "/api/v1/accounts/",
        json={"account_name": "Blocked Corp"},
        headers=analyst_headers,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_no_auth_returns_401(client):
    resp = await client.get("/api/v1/accounts/")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_empty_name_returns_422(client, admin_headers):
    resp = await client.post(
        "/api/v1/accounts/",
        json={"account_name": ""},
        headers=admin_headers,
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_default_environment_is_production(client, admin_headers):
    resp = await client.post(
        "/api/v1/accounts/",
        json={"account_name": "Default Env Corp"},
        headers=admin_headers,
    )
    assert resp.json()["environment"] == "production"
