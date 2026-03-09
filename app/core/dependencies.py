from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.services.user import get_user_by_email

# OAuth2PasswordBearer tells FastAPI: "look for a token in the Authorization header."
# tokenUrl is just for Swagger docs — it points to our login endpoint so the
# interactive docs know where to send credentials.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """
    Dependency that runs before any protected route.

    1. Extracts the JWT from the Authorization header (via oauth2_scheme)
    2. Decodes the token and reads the "sub" claim (the user's email)
    3. Looks up the user in the database
    4. Returns the user object — or raises 401 if anything fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode the JWT — this also checks if it's expired
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Look up the user — the token is valid, but does this user still exist?
    user = await get_user_by_email(db, email)
    if user is None:
        raise credentials_exception

    return user
