import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AccountCreate(BaseModel):
    """What the client sends to create an account."""

    account_name: str = Field(min_length=1, max_length=255)
    environment: str = Field(default="production", max_length=50)


class AccountResponse(BaseModel):
    """What the API sends back when returning account data."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    account_name: str
    environment: str
    created_at: datetime
    updated_at: datetime
