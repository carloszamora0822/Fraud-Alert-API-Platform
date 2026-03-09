import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertStatusUpdate


async def create_alert(db: AsyncSession, data: AlertCreate) -> Alert:
    """Insert a new fraud alert row and return the ORM object."""
    alert = Alert(**data.model_dump())
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return alert


async def get_alert(db: AsyncSession, alert_id: uuid.UUID) -> Alert | None:
    """Fetch a single alert by its primary key. Returns None if not found."""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    return result.scalar_one_or_none()


async def list_alerts(
    db: AsyncSession, account_id: uuid.UUID | None = None
) -> list[Alert]:
    """Fetch alerts, optionally filtered by account.

    If account_id is provided, only return alerts for that account.
    Otherwise, return all alerts.
    """
    query = select(Alert).order_by(Alert.timestamp.desc())

    if account_id is not None:
        query = query.where(Alert.account_id == account_id)

    result = await db.execute(query)
    return list(result.scalars().all())


async def update_alert_status(
    db: AsyncSession, alert_id: uuid.UUID, data: AlertStatusUpdate
) -> Alert | None:
    """Change an alert's status (e.g., new → reviewed → resolved).

    Returns the updated alert, or None if the alert doesn't exist.
    """
    alert = await get_alert(db, alert_id)
    if alert is None:
        return None

    alert.status = data.status.value
    await db.commit()
    await db.refresh(alert)
    return alert
