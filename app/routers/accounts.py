import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.account import AccountCreate, AccountResponse
from app.services import account as account_service

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("/", response_model=AccountResponse, status_code=201)
async def create_account(data: AccountCreate, db: AsyncSession = Depends(get_db)):
    """Create a new account."""
    account = await account_service.create_account(db, data)
    return account


@router.get("/", response_model=list[AccountResponse])
async def list_accounts(db: AsyncSession = Depends(get_db)):
    """List all accounts."""
    return await account_service.list_accounts(db)


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(account_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Get a single account by ID."""
    account = await account_service.get_account(db, account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account
