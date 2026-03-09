from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AuthenticationError, ConflictError
from app.core.rate_limit import limiter
from app.core.security import create_access_token
from app.schemas.user import Token, UserCreate, UserResponse
from app.services import user as user_service

router = APIRouter(prefix="/auth", tags=["auth"])


# Auth endpoints use a fixed, stricter limit (no JWT to read role from).
# 20/minute is tight because login attempts are a brute-force vector.
@router.post("/register", response_model=UserResponse, status_code=201)
@limiter.limit("20/minute")
async def register(
    request: Request, data: UserCreate, db: AsyncSession = Depends(get_db)
):
    """
    Create a new user account.
    Hashes the password and stores the user. Returns user info (no password).
    """
    existing = await user_service.get_user_by_email(db, data.email)
    if existing:
        raise ConflictError("Email already registered")

    user = await user_service.create_user(db, data)
    return user


@router.post("/login", response_model=Token)
@limiter.limit("20/minute")
async def login(request: Request, data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Authenticate and return a JWT.
    Takes email + password, verifies against the database,
    and returns a signed token if valid.
    """
    user = await user_service.authenticate_user(db, data.email, data.password)
    if user is None:
        raise AuthenticationError("Invalid email or password")

    token = create_access_token({"sub": user.email, "role": user.role})
    return Token(access_token=token)
