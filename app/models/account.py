from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.alert import Alert


class Account(Base):
    __tablename__ = "accounts"

    account_name: Mapped[str] = mapped_column(String(255))
    environment: Mapped[str] = mapped_column(String(50), default="production")

    # Relationship — gives us account.alerts to get all alerts for this account.
    # back_populates="account" links this to Alert.account on the other side.
    alerts: Mapped[list["Alert"]] = relationship(back_populates="account")  # noqa: F821
