from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token
from app.schemas.user import Token, UserCreate, UserResponse
from app.services import user as user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new user account.
    Hashes the password and stores the user. Returns user info (no password).
    """
    # Check if email is already taken
    existing = await user_service.get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = await user_service.create_user(db, data)
    return user


@router.post("/login", response_model=Token)
async def login(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Authenticate and return a JWT.
    Takes email + password, verifies against the database,
    and returns a signed token if valid.
    """
    user = await user_service.authenticate_user(db, data.email, data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Build the JWT with the user's email and role as claims
    token = create_access_token({"sub": user.email, "role": user.role})
    return Token(access_token=token)
