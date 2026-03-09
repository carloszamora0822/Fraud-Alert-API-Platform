from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.account import Account


class Alert(Base):
    __tablename__ = "alerts"

    # ── Core fields ───────────────────────────────────────
    alert_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    severity: Mapped[str] = mapped_column(String(20))  # low, medium, high, critical
    event_type: Mapped[str] = mapped_column(String(100))  # e.g. "unusual_login"
    resource_type: Mapped[str] = mapped_column(String(100))  # e.g. "virtual_machine"

    # ── Network / location ────────────────────────────────
    source_ip: Mapped[str] = mapped_column(String(45))  # supports IPv6
    geo_location: Mapped[str] = mapped_column(String(100))

    # ── Payload ───────────────────────────────────────────
    raw_payload: Mapped[dict] = mapped_column(JSONB, default=dict)

    # ── Status tracking ───────────────────────────────────
    status: Mapped[str] = mapped_column(
        String(20), default="new"
    )  # new, reviewed, escalated, resolved

    # ── Sync tracking ──────────────────────────────────────
    # Tracks whether this alert has been copied to ADX yet.
    # The sync service queries WHERE synced_to_adx = False to find new alerts.
    synced_to_adx: Mapped[bool] = mapped_column(Boolean, default=False)

    # ── Foreign key to accounts ───────────────────────────
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=False
    )

    # Relationship — gives us alert.account to get the parent account.
    account: Mapped["Account"] = relationship(back_populates="alerts")  # noqa: F821

    # ── Indexes for fast queries ──────────────────────────
    __table_args__ = (
        Index("ix_alerts_timestamp", "timestamp"),
        Index("ix_alerts_account_id", "account_id"),
        Index("ix_alerts_severity", "severity"),
    )
