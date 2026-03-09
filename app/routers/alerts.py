import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.schemas.alert import AlertCreate, AlertResponse, AlertStatusUpdate
from app.services import alert as alert_service

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("/", response_model=AlertResponse, status_code=201)
async def create_alert(
    data: AlertCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("admin")),
):
    """Create a new fraud alert. Requires admin role."""
    alert = await alert_service.create_alert(db, data)
    return alert


@router.get("/", response_model=list[AlertResponse])
async def list_alerts(
    account_id: uuid.UUID | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("analyst")),
):
    """List alerts, optionally filtered by account_id. Requires analyst role."""
    return await alert_service.list_alerts(db, account_id=account_id)


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("analyst")),
):
    """Get a single alert by ID. Requires analyst role."""
    alert = await alert_service.get_alert(db, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert


@router.patch("/{alert_id}/status", response_model=AlertResponse)
async def update_alert_status(
    alert_id: uuid.UUID,
    data: AlertStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("admin")),
):
    """Update an alert's status. Requires admin role."""
    alert = await alert_service.update_alert_status(db, alert_id, data)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
