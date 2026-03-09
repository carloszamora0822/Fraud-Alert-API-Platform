import base64
import uuid
from datetime import datetime

from sqlalchemy import select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertFilters, AlertStatusUpdate
from app.schemas.pagination import PaginatedResponse

# ── Pagination defaults ─────────────────────────────────────
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 100


def _encode_cursor(timestamp: datetime, alert_id: uuid.UUID) -> str:
    """Turn a (timestamp, id) pair into an opaque base64 string.

    We include both values to handle the tiebreaker case —
    two alerts with the same timestamp get different cursors.
    """
    raw = f"{timestamp.isoformat()}|{alert_id}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def _decode_cursor(cursor: str) -> tuple[datetime, uuid.UUID]:
    """Reverse of _encode_cursor. Returns (timestamp, id)."""
    raw = base64.urlsafe_b64decode(cursor.encode()).decode()
    ts_str, id_str = raw.split("|")
    return datetime.fromisoformat(ts_str), uuid.UUID(id_str)


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
    db: AsyncSession,
    filters: AlertFilters | None = None,
    cursor: str | None = None,
    limit: int = DEFAULT_PAGE_SIZE,
) -> PaginatedResponse:
    """Fetch a page of alerts using cursor-based pagination.

    The sort order is (timestamp DESC, id DESC) so newest alerts come first.
    The cursor encodes the last-seen (timestamp, id) pair.
    We fetch limit+1 rows to determine if there's a next page.
    """
    # Clamp limit to the allowed max
    limit = min(limit, MAX_PAGE_SIZE)

    # Base query — always sorted newest-first, with id as tiebreaker
    query = select(Alert).order_by(Alert.timestamp.desc(), Alert.id.desc())

    # ── Apply filters (only the ones the user actually provided) ──
    if filters is not None:
        if filters.account_id is not None:
            query = query.where(Alert.account_id == filters.account_id)
        if filters.severity is not None:
            query = query.where(Alert.severity == filters.severity.value)
        if filters.status is not None:
            query = query.where(Alert.status == filters.status.value)
        if filters.event_type is not None:
            query = query.where(Alert.event_type == filters.event_type)
        if filters.start_date is not None:
            query = query.where(Alert.timestamp >= filters.start_date)
        if filters.end_date is not None:
            query = query.where(Alert.timestamp <= filters.end_date)

    # Apply cursor: "give me everything AFTER this point"
    if cursor is not None:
        cursor_ts, cursor_id = _decode_cursor(cursor)
        # tuple_ comparison: (timestamp, id) < (cursor_ts, cursor_id)
        # This is the SQL equivalent of: WHERE (timestamp, id) < (cursor_ts, cursor_id)
        query = query.where(
            tuple_(Alert.timestamp, Alert.id)
            < tuple_(cursor_ts, cursor_id)  # type: ignore[arg-type]
        )

    # Fetch one extra row to check if there's more
    query = query.limit(limit + 1)

    result = await db.execute(query)
    rows = list(result.scalars().all())

    # If we got more rows than the limit, there's a next page
    has_more = len(rows) > limit
    items = rows[:limit]  # Only return up to `limit` items

    # Build the next cursor from the last item returned
    next_cursor = None
    if has_more and items:
        last = items[-1]
        next_cursor = _encode_cursor(last.timestamp, last.id)

    return PaginatedResponse(items=items, next_cursor=next_cursor, has_more=has_more)


async def update_alert_status(
    db: AsyncSession, alert_id: uuid.UUID, data: AlertStatusUpdate
) -> Alert | None:
    """Change an alert's status (e.g., new -> reviewed -> resolved).

    Returns the updated alert, or None if the alert doesn't exist.
    """
    alert = await get_alert(db, alert_id)
    if alert is None:
        return None

    alert.status = data.status.value
    await db.commit()
    await db.refresh(alert)
    return alert
