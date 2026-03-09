from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Envelope for cursor-based paginated results.

    Generic over T so it works with any item type:
      PaginatedResponse[AlertResponse]
      PaginatedResponse[AccountResponse]
    """

    items: list[T]
    next_cursor: str | None
    has_more: bool
