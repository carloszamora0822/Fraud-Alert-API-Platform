import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.schemas.account import AccountCreate


async def create_account(db: AsyncSession, data: AccountCreate) -> Account:
    """Insert a new account row and return the ORM object."""
    account = Account(**data.model_dump())
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


async def get_account(db: AsyncSession, account_id: uuid.UUID) -> Account | None:
    """Fetch a single account by its primary key. Returns None if not found."""
    result = await db.execute(select(Account).where(Account.id == account_id))
    return result.scalar_one_or_none()


async def list_accounts(db: AsyncSession) -> list[Account]:
    """Fetch all accounts, ordered by creation time (newest first)."""
    result = await db.execute(select(Account).order_by(Account.created_at.desc()))
    return list(result.scalars().all())
