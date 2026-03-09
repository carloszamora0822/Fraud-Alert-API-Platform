"""
Fraud alert data generator.

Produces realistic fake accounts and alerts using the Faker library.
Each fraud type has its own patterns so the data looks like what a real
detection system (Azure Sentinel, etc.) would output.
"""

import random
import uuid
from datetime import datetime, timedelta, timezone

from faker import Faker

from app.schemas.account import AccountCreate
from app.schemas.alert import AlertCreate, Severity

fake = Faker()

# ---------------------------------------------------------------------------
# Event type distribution — weights control how often each type appears.
# ~70% legitimate, ~30% fraud spread across 6 types.
# ---------------------------------------------------------------------------
EVENT_TYPES: list[tuple[str, float]] = [
    ("legitimate", 70),
    ("impossible_travel", 5),
    ("brute_force", 6),
    ("privilege_escalation", 4),
    ("data_exfiltration", 4),
    ("suspicious_login", 6),
    ("resource_abuse", 5),
]

EVENT_NAMES = [e[0] for e in EVENT_TYPES]
EVENT_WEIGHTS = [e[1] for e in EVENT_TYPES]

# Pairs of distant cities — used for impossible_travel alerts.
DISTANT_CITY_PAIRS = [
    ("New York, US", "Tokyo, JP"),
    ("London, UK", "Sydney, AU"),
    ("Chicago, US", "Mumbai, IN"),
    ("San Francisco, US", "Berlin, DE"),
    ("Toronto, CA", "São Paulo, BR"),
]

# Resource types that each event type would realistically target.
RESOURCE_TYPES = {
    "legitimate": ["vm_instance", "storage_account", "web_app", "database"],
    "impossible_travel": ["azure_ad", "office_365", "vpn_gateway"],
    "brute_force": ["azure_ad", "ssh_server", "rdp_server", "web_app"],
    "privilege_escalation": ["iam_role", "admin_console", "key_vault", "rbac_policy"],
    "data_exfiltration": ["blob_storage", "sql_database", "file_share", "data_lake"],
    "suspicious_login": ["azure_ad", "office_365", "vpn_gateway"],
    "resource_abuse": ["compute_instance", "gpu_cluster", "container_group"],
}


def _pick_event_type() -> str:
    """Pick a random event type using the weighted distribution."""
    return random.choices(EVENT_NAMES, weights=EVENT_WEIGHTS, k=1)[0]


def _random_timestamp(days_back: int = 30) -> datetime:
    """Generate a random timestamp within the last N days."""
    now = datetime.now(timezone.utc)
    offset = random.random() * days_back * 24 * 3600  # random seconds
    return now - timedelta(seconds=offset)


def _severity_for(event_type: str) -> Severity:
    """Pick a realistic severity based on the event type.

    Fraud types skew toward higher severities.
    Legitimate traffic is almost always low.
    """
    if event_type == "legitimate":
        return random.choices(
            [Severity.low, Severity.medium],
            weights=[90, 10],
            k=1,
        )[0]

    if event_type in ("brute_force", "data_exfiltration", "privilege_escalation"):
        return random.choices(
            [Severity.medium, Severity.high, Severity.critical],
            weights=[20, 50, 30],
            k=1,
        )[0]

    # impossible_travel, suspicious_login, resource_abuse
    return random.choices(
        [Severity.medium, Severity.high, Severity.critical],
        weights=[40, 40, 20],
        k=1,
    )[0]


def _build_raw_payload(event_type: str) -> dict:
    """Build a realistic raw_payload dict for the given event type.

    This is the "extra details" blob that a real detection system would attach.
    """
    if event_type == "legitimate":
        return {
            "action": random.choice(["read", "list", "get", "describe"]),
            "user_agent": fake.user_agent(),
        }

    if event_type == "impossible_travel":
        city_a, city_b = random.choice(DISTANT_CITY_PAIRS)
        return {
            "login_1_location": city_a,
            "login_2_location": city_b,
            "time_between_minutes": random.randint(1, 15),
        }

    if event_type == "brute_force":
        return {
            "failed_attempts": random.randint(50, 5000),
            "time_window_seconds": random.randint(60, 600),
            "method": random.choice(
                ["password_spray", "credential_stuffing", "dictionary"]
            ),
        }

    if event_type == "privilege_escalation":
        return {
            "previous_role": "reader",
            "new_role": random.choice(["owner", "contributor", "admin"]),
            "method": random.choice(
                ["role_assignment", "token_manipulation", "policy_change"]
            ),
        }

    if event_type == "data_exfiltration":
        return {
            "bytes_transferred": random.randint(500_000_000, 50_000_000_000),
            "destination": fake.ipv4_public(),
            "protocol": random.choice(["https", "sftp", "azcopy"]),
        }

    if event_type == "suspicious_login":
        return {
            "login_hour_utc": random.randint(0, 5),  # middle of the night
            "device": random.choice(["unknown_device", "new_browser", "tor_exit_node"]),
            "mfa_passed": random.choice([True, False]),
        }

    # resource_abuse
    return {
        "cpu_percent": random.randint(90, 100),
        "instances_spawned": random.randint(10, 200),
        "suspected_activity": random.choice(
            ["cryptomining", "botnet_c2", "spam_relay"]
        ),
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_accounts(n: int = 20) -> list[AccountCreate]:
    """Generate N fake company accounts."""
    environments = ["production", "staging", "development"]
    return [
        AccountCreate(
            account_name=fake.company(),
            environment=random.choice(environments),
        )
        for _ in range(n)
    ]


def generate_alert(account_id: uuid.UUID) -> AlertCreate:
    """Generate a single realistic alert for the given account."""
    event_type = _pick_event_type()

    # For impossible_travel, geo_location shows the two cities.
    # For everything else, it's a random city.
    if event_type == "impossible_travel":
        city_a, city_b = random.choice(DISTANT_CITY_PAIRS)
        geo_location = f"{city_a} → {city_b}"
    else:
        geo_location = f"{fake.city()}, {fake.country_code()}"

    return AlertCreate(
        alert_id=f"ALERT-{uuid.uuid4().hex[:12].upper()}",
        severity=_severity_for(event_type),
        event_type=event_type,
        resource_type=random.choice(RESOURCE_TYPES[event_type]),
        source_ip=fake.ipv4_public(),
        geo_location=geo_location,
        raw_payload=_build_raw_payload(event_type),
        account_id=account_id,
        timestamp=_random_timestamp(),
    )


def generate_alerts(
    account_ids: list[uuid.UUID], n: int = 10_000
) -> list[AlertCreate]:
    """Generate N alerts spread randomly across the given accounts."""
    return [generate_alert(random.choice(account_ids)) for _ in range(n)]
