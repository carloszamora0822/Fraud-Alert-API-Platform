import uuid

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_role
from app.core.exceptions import NotFoundError
from app.core.rate_limit import get_role_limit, limiter
from app.models.user import User
from app.schemas.alert import (
    AlertCreate,
    AlertFilters,
    AlertResponse,
    AlertStatusUpdate,
)
from app.schemas.pagination import PaginatedResponse
from app.services import alert as alert_service

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("/", response_model=AlertResponse, status_code=201)
@limiter.limit(get_role_limit)
async def create_alert(
    request: Request,
    data: AlertCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("admin")),
):
    """Create a new fraud alert. Requires admin role."""
    alert = await alert_service.create_alert(db, data)
    return alert


@router.get("/", response_model=PaginatedResponse[AlertResponse])
@limiter.limit(get_role_limit)
async def list_alerts(
    request: Request,
    filters: AlertFilters = Depends(),
    cursor: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("analyst")),
):
    """List alerts with filtering and cursor-based pagination. Requires analyst role."""
    return await alert_service.list_alerts(
        db, filters=filters, cursor=cursor, limit=limit
    )


@router.get("/{alert_id}", response_model=AlertResponse)
@limiter.limit(get_role_limit)
async def get_alert(
    request: Request,
    alert_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("analyst")),
):
    """Get a single alert by ID. Requires analyst role."""
    alert = await alert_service.get_alert(db, alert_id)
    if alert is None:
        raise NotFoundError("Alert", alert_id)
    return alert


@router.patch("/{alert_id}/status", response_model=AlertResponse)
@limiter.limit(get_role_limit)
async def update_alert_status(
    request: Request,
    alert_id: uuid.UUID,
    data: AlertStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("admin")),
):
    """Update an alert's status. Requires admin role."""
    alert = await alert_service.update_alert_status(db, alert_id, data)
    if alert is None:
        raise NotFoundError("Alert", alert_id)
    return alert
