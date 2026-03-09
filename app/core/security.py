from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# CryptContext manages hashing for us.
# "bcrypt" is the scheme — the algorithm we discussed.
# deprecated="auto" means if we ever switch algorithms, old hashes still verify.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt. Returns the hash (includes the salt)."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Check a login attempt: hash the input with the stored salt,
    compare to the stored hash. Returns True if they match.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    Build and sign a JWT.

    - Copies the input data (so we don't mutate the original)
    - Adds an expiration claim ("exp") — 30 minutes from now by default
    - Signs it with our secret key using HS256
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
