import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Severity(str, Enum):
    """Allowed severity levels. Using an enum prevents garbage values."""

    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class AlertStatus(str, Enum):
    """Allowed statuses for alert lifecycle tracking."""

    new = "new"
    reviewed = "reviewed"
    escalated = "escalated"
    resolved = "resolved"


class AlertFilters(BaseModel):
    """Query parameters for filtering the alerts list.

    Every field is optional — if the client doesn't send it, we skip
    that filter. Only the filters the user actually provides get
    applied to the SQL query.
    """

    severity: Severity | None = None
    status: AlertStatus | None = None
    event_type: str | None = None
    account_id: uuid.UUID | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None


class AlertCreate(BaseModel):
    """What the client sends to create an alert.

    Note what's NOT here: id, created_at, updated_at, status.
    The database generates those automatically.
    """

    alert_id: str = Field(max_length=100)
    severity: Severity
    event_type: str = Field(max_length=100)
    resource_type: str = Field(max_length=100)
    source_ip: str = Field(max_length=45)
    geo_location: str = Field(max_length=100)
    raw_payload: dict = Field(default_factory=dict)
    account_id: uuid.UUID
    timestamp: datetime | None = None  # optional — DB defaults to now()


class AlertStatusUpdate(BaseModel):
    """For PATCH /alerts/{id}/status — only the status field."""

    status: AlertStatus


class AlertResponse(BaseModel):
    """What the API sends back when returning alert data."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    alert_id: str
    timestamp: datetime
    severity: Severity
    event_type: str
    resource_type: str
    source_ip: str
    geo_location: str
    raw_payload: dict
    status: str
    account_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
