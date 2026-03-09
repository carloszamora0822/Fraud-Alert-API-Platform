import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import User
from app.schemas.account import AccountCreate, AccountResponse
from app.services import account as account_service

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/", response_model=AccountResponse, status_code=201)
async def create_account(
    data: AccountCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("admin")),
):
    """Create a new account. Requires admin role."""
    account = await account_service.create_account(db, data)
    return account


@router.get("/", response_model=list[AccountResponse])
async def list_accounts(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("analyst")),
):
    """List all accounts. Requires analyst role."""
    return await account_service.list_accounts(db)


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    alert_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(require_role("analyst")),
):
    """Get a single account by ID. Requires analyst role."""
    account = await account_service.get_account(db, alert_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account
