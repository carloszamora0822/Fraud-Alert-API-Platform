"""Tests for alert endpoints."""

import uuid

import pytest


def _alert_payload(account_id: str, alert_id: str = "ALERT-001") -> dict:
    return {
        "alert_id": alert_id,
        "severity": "high",
        "event_type": "unusual_login",
        "resource_type": "virtual_machine",
        "source_ip": "10.0.0.1",
        "geo_location": "US-West",
        "raw_payload": {"detail": "test"},
        "account_id": account_id,
    }


@pytest.mark.asyncio
async def test_create_alert(client, admin_headers, sample_account):
    resp = await client.post(
        "/api/v1/alerts/",
        json=_alert_payload(sample_account["id"], "CREATE-001"),
        headers=admin_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["severity"] == "high"


@pytest.mark.asyncio
async def test_list_alerts_paginated_structure(
    client, admin_headers, sample_alert, analyst_headers
):
    resp = await client.get("/api/v1/alerts/", headers=analyst_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "next_cursor" in data
    assert "has_more" in data


@pytest.mark.asyncio
async def test_get_alert_by_id(client, admin_headers, sample_alert, analyst_headers):
    alert_id = sample_alert["id"]
    resp = await client.get(f"/api/v1/alerts/{alert_id}", headers=analyst_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == alert_id


@pytest.mark.asyncio
async def test_get_nonexistent_alert(client, analyst_headers):
    resp = await client.get(f"/api/v1/alerts/{uuid.uuid4()}", headers=analyst_headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_alert_status(client, admin_headers, sample_alert):
    alert_id = sample_alert["id"]
    resp = await client.patch(
        f"/api/v1/alerts/{alert_id}/status",
        json={"status": "reviewed"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "reviewed"


@pytest.mark.asyncio
async def test_update_nonexistent_alert(client, admin_headers):
    resp = await client.patch(
        f"/api/v1/alerts/{uuid.uuid4()}/status",
        json={"status": "reviewed"},
        headers=admin_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_analyst_cannot_create_alert(client, analyst_headers, sample_account):
    resp = await client.post(
        "/api/v1/alerts/",
        json=_alert_payload(sample_account["id"], "BLOCKED-001"),
        headers=analyst_headers,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_analyst_cannot_update_status(client, analyst_headers, sample_alert):
    resp = await client.patch(
        f"/api/v1/alerts/{sample_alert['id']}/status",
        json={"status": "resolved"},
        headers=analyst_headers,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_no_auth_returns_401(client):
    resp = await client.get("/api/v1/alerts/")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_filter_by_severity(
    client, admin_headers, analyst_headers, sample_account
):
    await client.post(
        "/api/v1/alerts/",
        json=_alert_payload(sample_account["id"], "SEV-LOW") | {"severity": "low"},
        headers=admin_headers,
    )
    await client.post(
        "/api/v1/alerts/",
        json=_alert_payload(sample_account["id"], "SEV-CRIT")
        | {"severity": "critical"},
        headers=admin_headers,
    )
    resp = await client.get("/api/v1/alerts/?severity=low", headers=analyst_headers)
    items = resp.json()["items"]
    assert all(a["severity"] == "low" for a in items)


@pytest.mark.asyncio
async def test_filter_by_status(client, admin_headers, analyst_headers, sample_account):
    create_resp = await client.post(
        "/api/v1/alerts/",
        json=_alert_payload(sample_account["id"], "STAT-001"),
        headers=admin_headers,
    )
    alert_id = create_resp.json()["id"]
    await client.patch(
        f"/api/v1/alerts/{alert_id}/status",
        json={"status": "escalated"},
        headers=admin_headers,
    )
    resp = await client.get("/api/v1/alerts/?status=escalated", headers=analyst_headers)
    items = resp.json()["items"]
    assert all(a["status"] == "escalated" for a in items)


@pytest.mark.asyncio
async def test_filter_by_event_type(
    client, admin_headers, analyst_headers, sample_account
):
    await client.post(
        "/api/v1/alerts/",
        json=_alert_payload(sample_account["id"], "EVT-001")
        | {"event_type": "data_exfil"},
        headers=admin_headers,
    )
    resp = await client.get(
        "/api/v1/alerts/?event_type=data_exfil", headers=analyst_headers
    )
    items = resp.json()["items"]
    assert all(a["event_type"] == "data_exfil" for a in items)


@pytest.mark.asyncio
async def test_filter_by_account_id(
    client, admin_headers, analyst_headers, sample_account
):
    await client.post(
        "/api/v1/alerts/",
        json=_alert_payload(sample_account["id"], "ACCT-001"),
        headers=admin_headers,
    )
    resp = await client.get(
        f"/api/v1/alerts/?account_id={sample_account['id']}", headers=analyst_headers
    )
    items = resp.json()["items"]
    assert all(a["account_id"] == sample_account["id"] for a in items)


@pytest.mark.asyncio
async def test_pagination_next_cursor(
    client, admin_headers, analyst_headers, sample_account
):
    # Create 3 alerts, request with limit=2 → should have next_cursor
    for i in range(3):
        await client.post(
            "/api/v1/alerts/",
            json=_alert_payload(sample_account["id"], f"PAGE-{i}"),
            headers=admin_headers,
        )
    resp = await client.get("/api/v1/alerts/?limit=2", headers=analyst_headers)
    data = resp.json()
    assert data["has_more"] is True
    assert data["next_cursor"] is not None


@pytest.mark.asyncio
async def test_pagination_limit_respected(
    client, admin_headers, analyst_headers, sample_account
):
    for i in range(5):
        await client.post(
            "/api/v1/alerts/",
            json=_alert_payload(sample_account["id"], f"LIM-{i}"),
            headers=admin_headers,
        )
    resp = await client.get("/api/v1/alerts/?limit=3", headers=analyst_headers)
    assert len(resp.json()["items"]) == 3
