"""
Data Sync Service — moves fraud alerts from PostgreSQL → Azure Data Explorer.

This is a "batch sync" pattern:
1. Query PG for alerts not yet synced (synced_to_adx = False)
2. Convert them to a pandas DataFrame (ADX ingestion format)
3. Push the DataFrame into ADX via queued ingestion
4. Mark those alerts as synced in PG

Why not sync in real-time (on every POST)?
- Ingestion has overhead. Batching is far more efficient.
- If ADX is temporarily down, we don't want API writes to fail.
- Decoupling write path (PG) from analytics path (ADX) is a core
  architectural pattern called "eventual consistency."
"""

import json
import logging

import pandas as pd
from azure.kusto.data import KustoConnectionStringBuilder
from azure.kusto.ingest import (
    IngestionProperties,
    QueuedIngestClient,
)
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.alert import Alert

logger = logging.getLogger(__name__)


def _build_ingest_client() -> QueuedIngestClient:
    """
    Create an ADX ingestion client.

    QueuedIngestClient is different from KustoClient (which we use for queries).
    - KustoClient talks to the QUERY endpoint (https://<cluster>.kusto.windows.net)
    - QueuedIngestClient talks to the INGEST endpoint (https://ingest-<cluster>...)

    For the free cluster, the ingest URI is the same as the cluster URI
    with "ingest-" prepended to the hostname.
    """
    ingest_uri = settings.ADX_CLUSTER_URI.replace("https://", "https://ingest-")

    kcsb = KustoConnectionStringBuilder.with_interactive_login(ingest_uri)
    return QueuedIngestClient(kcsb)


def _alerts_to_dataframe(alerts: list[Alert]) -> pd.DataFrame:
    """
    Convert SQLAlchemy Alert objects into a pandas DataFrame.

    The DataFrame columns must match the ADX table schema EXACTLY —
    same names, same order. ADX maps columns by position when ingesting
    from a DataFrame.
    """
    rows = []
    for alert in alerts:
        rows.append(
            {
                "alert_id": alert.alert_id,
                "timestamp": alert.timestamp,
                "severity": alert.severity,
                "event_type": alert.event_type,
                "resource_type": alert.resource_type,
                "source_ip": alert.source_ip,
                "geo_location": alert.geo_location,
                # ADX stores JSON as a string column — serialize it
                "raw_payload": json.dumps(alert.raw_payload),
                "status": alert.status,
                "account_id": str(alert.account_id),
            }
        )

    return pd.DataFrame(rows)


async def get_unsynced_alerts(db: AsyncSession) -> list[Alert]:
    """
    Fetch all alerts that haven't been synced to ADX yet.

    This is the "change tracking" mechanism — instead of comparing
    timestamps or keeping a separate log, we use a simple boolean flag.
    """
    result = await db.execute(
        select(Alert)
        .where(Alert.synced_to_adx == False)  # noqa: E712
        .order_by(Alert.id)
    )
    return list(result.scalars().all())


async def mark_alerts_synced(db: AsyncSession, alert_ids: list[int]) -> None:
    """
    After successful ingestion, flip synced_to_adx = True for these alerts.

    We do this in a single UPDATE statement (not one per row) for efficiency.
    This is the SQL equivalent of:
        UPDATE alerts SET synced_to_adx = true WHERE id IN (1, 2, 3, ...)
    """
    await db.execute(
        update(Alert).where(Alert.id.in_(alert_ids)).values(synced_to_adx=True)
    )
    await db.commit()


async def sync_alerts_to_adx(db: AsyncSession) -> dict:
    """
    Main sync function — orchestrates the full PG → ADX pipeline.

    Returns a summary dict with counts for logging/reporting.

    This function is IDEMPOTENT — running it multiple times is safe because:
    1. We only select alerts where synced_to_adx = False
    2. After ingestion, we mark them True
    3. If ingestion fails, we DON'T mark them — they'll be picked up next run
    """
    # Step 1: Find unsynced alerts
    alerts = await get_unsynced_alerts(db)

    if not alerts:
        logger.info("No unsynced alerts found — nothing to do.")
        return {"synced": 0, "status": "no_new_alerts"}

    logger.info(f"Found {len(alerts)} unsynced alerts to sync.")

    # Step 2: Convert to DataFrame
    df = _alerts_to_dataframe(alerts)

    # Step 3: Ingest into ADX
    ingest_client = _build_ingest_client()

    # IngestionProperties tells ADX which database/table to write to
    ingestion_props = IngestionProperties(
        database=settings.ADX_DATABASE,
        table="FraudAlerts",
    )

    # ingest_from_dataframe sends the DataFrame to ADX's ingestion queue.
    # "Queued" means ADX will process it asynchronously — the data won't
    # appear instantly but typically within a few minutes.
    ingest_client.ingest_from_dataframe(df, ingestion_properties=ingestion_props)

    logger.info(f"Ingestion request sent for {len(alerts)} alerts.")

    # Step 4: Mark as synced in PG
    alert_ids = [alert.id for alert in alerts]
    await mark_alerts_synced(db, alert_ids)

    logger.info(f"Marked {len(alert_ids)} alerts as synced.")

    return {
        "synced": len(alerts),
        "status": "success",
        "alert_ids": alert_ids,
    }
