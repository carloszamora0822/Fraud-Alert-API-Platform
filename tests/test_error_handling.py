"""Tests for RFC 7807 error handling."""

import uuid

import pytest

RFC7807_KEYS = {"type", "title", "status", "detail", "instance"}


@pytest.mark.asyncio
async def test_404_has_rfc7807_keys(client, analyst_headers):
    resp = await client.get(f"/api/v1/accounts/{uuid.uuid4()}", headers=analyst_headers)
    assert resp.status_code == 404
    assert RFC7807_KEYS.issubset(resp.json().keys())


@pytest.mark.asyncio
async def test_422_has_rfc7807_format(client, admin_headers):
    resp = await client.post(
        "/api/v1/accounts/",
        json={"account_name": ""},
        headers=admin_headers,
    )
    assert resp.status_code == 422
    assert RFC7807_KEYS.issubset(resp.json().keys())


@pytest.mark.asyncio
async def test_401_has_www_authenticate_header(client):
    resp = await client.get("/api/v1/accounts/")
    assert resp.status_code == 401
    assert "WWW-Authenticate" in resp.headers


@pytest.mark.asyncio
async def test_403_has_rfc7807_format(client, analyst_headers):
    resp = await client.post(
        "/api/v1/accounts/",
        json={"account_name": "Blocked"},
        headers=analyst_headers,
    )
    assert resp.status_code == 403
    assert RFC7807_KEYS.issubset(resp.json().keys())


@pytest.mark.asyncio
async def test_error_content_type_is_problem_json(client, analyst_headers):
    resp = await client.get(f"/api/v1/accounts/{uuid.uuid4()}", headers=analyst_headers)
    assert "application/problem+json" in resp.headers["content-type"]
